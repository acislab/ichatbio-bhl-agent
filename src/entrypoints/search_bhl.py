import os
from typing import Optional, Self, Literal

import httpx
import instructor
from httpx import Response, HTTPError
from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint
from instructor import AsyncInstructor
from instructor.exceptions import InstructorRetryException
from openai import AsyncOpenAI
from pydantic import Field, BaseModel, model_validator
from tenacity import AsyncRetrying

from util import AIGenerationException, StopOnTerminalErrorOrMaxAttempts
from schema import PublicationSearchResponse, AdvancedPublicationSearchParameters, SimplePublicationSearchParameters

# This description helps iChatBio understand when to call this entrypoint
description = """
Searches the Biodiversity Heritage Library (BHL), a biodiversity literature repository that contains hundreds of
thousands of digitized articles. Returns the titles, authors, and other metadata for articles that might be relevant
(for example, contain key words) to the requested information.
"""

entrypoint = AgentEntrypoint(
    id="search_bhl",
    description=description,
    parameters=None
)

SYSTEM_PROMPT = """
You translate user requests into search parameters for the BHL publication advanced search API (version 3).

If searching for an exact phrase, such as a scientific name, set exact_match=true. You can only search for one exact
phrase at a time. Attempting to search for multiple exact phrases in the same field (e.g., title) will fail.
"""
# Prefer to search publication titles instead of publication text.

API_URL = "https://www.biodiversitylibrary.org/api3"


async def run(context: ResponseContext, request: str):
    """
    Executes this specific entrypoint. See description above. This function yields a sequence of messages that are
    returned one-by-one to iChatBio in response to the request, logging the retrieval process in real time.
    """
    async with context.begin_process("Searching BHL") as process:
        process: IChatBioAgentProcess

        await process.log("Generating search parameters for BHL API")

        try:
            params: SimplePublicationSearchParameters = await _generate_search_parameters(request)
        except AIGenerationException as e:
            await process.log(str(e))
            return

        await process.log("Generated search parameters", data=params.model_dump(exclude_none=True))

        api_params = {k: (v or "") for k, v in params.model_dump().items()}
        api_params |= {
            "op": "PublicationSearch",
            "format": "json"
        } | api_params

        cleaned_api_params = {k: v for k, v in api_params.items() if v}
        await process.log("Sending a GET request to the BHL publication search API", data=cleaned_api_params)

        try:
            api_response = await _pub_search(api_params)
        except HTTPError:
            # TODO: uh oh! This might expose our API access token
            await process.log(f"An error occurred while querying BHL")
            return

        search_results = PublicationSearchResponse(**api_response.json())
        if search_results.status != "ok":
            await process.log(f"Something went wrong! Message from the BHL API: {search_results.error_message}")
            return

        if search_results.error_message:
            await process.log(f"API returned an error message: {search_results.error_message}")

        num_pubs = len(search_results.result)

        if num_pubs > 0:
            await process.create_artifact(
                mimetype="application/json",
                description="BHL search results",
                content=api_response.content,
                metadata={
                    "data_source": "BHL",
                    "api_url": API_URL,
                    "api_parameters": api_params
                }
            )

            await context.reply(
                f"The BHL API returned {num_pubs} publications in page {params.page} (page size {params.pageSize}). The"
                f" API URL I provided will not work directly, because it requires an access token parameter. To get"
                f" around this, I have provided the API response in an artifact."
            )
        else:
            await context.reply("The BHL API returned no matching publications.")


class ExactOrFuzzySearch(BaseModel):
    search_string: str
    exact_phrase: bool = False


class LLMSimpleSearchParameters(BaseModel):
    search_terms: list[str] = Field(None, description="Search terms used to find literature in BHL. Separate search terms that are not part of the same phrase. For example, [Rattus rattus, Rattus gigantus]", min_length=1)
    search_type: Literal["catalog", "catalog_and_full_text"] = Field("C",
                                           description="Prefer to search only the catalog. Full text searches produce many unwanted false positive results.")
    page: int = Field(1, description="1 for the first page of results, 2 for the second, and so on")
    page_size: int = Field(100, description="the maximum number of results to return per page (default = 100)")


class LLMAdvancedSearchParameters(BaseModel):
    publication_title: ExactOrFuzzySearch = Field(None, description="search by publication title")
    # publication_notes: ExactOrFuzzySearch = Field(None, description="search by publication notes")
    # publication_text: ExactOrFuzzySearch = Field(None,
    #                                              description="full text search through publication texts. To use this field, you must also specify title, author, or collection search parameters to limit the scope of the search.")
    author_name: Optional[str] = Field(None, description="search by author name")
    year: Optional[str] = Field(None, description="only search for items published this year")
    # subject: Optional[str] = Field(None, description="a subject for which to search")
    language: Optional[str] = Field(None,
                                    description="a language code; only return publications in the specified language")
    # collection_id: Optional[str] = Field(None,
    #                                      description="a collection id; return publications from the specified collection")
    page: int = Field(1, description="used to page through API results")
    page_size: int = Field(100, description="the maximum number of API results to return per page")

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if not (self.search_terms or self.author_name or self.collection_id):
            raise ValueError(
                "API requires at least publication_title, author_name, and/or collection_id in the search parameters")
        return self


async def _generate_search_parameters(request: str) -> SimplePublicationSearchParameters:
    model = os.getenv("AGENTS_LLM", "gpt-4.1")
    try:
        client: AsyncInstructor = instructor.from_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        p = await client.chat.completions.create(
            model=model,
            temperature=0,
            response_model=LLMSimpleSearchParameters,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request}
            ],
            max_retries=AsyncRetrying(stop=StopOnTerminalErrorOrMaxAttempts(3))
        )

        api_params = SimplePublicationSearchParameters(
            searchterm=" OR ".join(p.search_terms),
            searchtype=("C" if p.search_type == "catalog" else "F"),
            page=p.page,
            pageSize=p.page_size
        )

        return api_params
    except InstructorRetryException as e:
        raise AIGenerationException(e)


async def _generate_advanced_search_parameters(request: str) -> AdvancedPublicationSearchParameters:
    model = os.getenv("AGENTS_LLM", "gpt-4.1")
    try:
        client: AsyncInstructor = instructor.from_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        p = await client.chat.completions.create(
            model=model,
            temperature=0,
            response_model=LLMAdvancedSearchParameters,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request}
            ],
            max_retries=AsyncRetrying(stop=StopOnTerminalErrorOrMaxAttempts(3))
        )

        api_params = AdvancedPublicationSearchParameters(
            title=p.publication_title.search_string if p.publication_title else None,
            titleop=("phrase" if p.publication_title.exact_phrase else "all") if p.publication_title else None,
            authorname=p.author_name,
            year=p.year,
            subject=None,
            language=p.language,
            collection=None,
            notes=None,
            notesop=None,
            text=None,  # p.publication_text.search_string if p.publication_text else None,
            textop=None,  # ("phrase" if p.publication_text.exact_phrase else "all") if p.publication_text else None,
            page=p.page,
            pageSize=p.page_size,
            format="json"
        )

        return api_params
    except InstructorRetryException as e:
        raise AIGenerationException(e)


async def _pub_search(api_params: dict) -> Response:
    token = os.environ.get("BHL_API_KEY")
    api_params |= {"apikey": token}

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(API_URL, params=api_params)
        response.raise_for_status()
        return response
