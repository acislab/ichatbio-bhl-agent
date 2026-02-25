from typing import Optional, Literal

from pydantic import BaseModel, Field


# See https://www.biodiversitylibrary.org/docs/api3/PublicationSearchAdvanced.html
class AdvancedPublicationSearchParameters(BaseModel):
    title: Optional[str]
    titleop: Optional[Literal["all", "phrase"]] = Field("all",
                                                        description="'all' to search for all specified words in the title fields; 'phrase' to search for the exact phrase specified")
    authorname: Optional[str] = Field(description="an author name for which to search")
    year: Optional[str] = Field(description="a four-digit publication year for which to search")
    subject: Optional[str] = Field(description="a subject for which to search")
    language: Optional[str] = Field(
        description="a language code; search will only return publications in the specified language")
    collection: Optional[str] = Field(
        description="a collection id; search will only return publications from the specfied collection")
    notes: Optional[str] = Field(description="one or more words for which to search in the publication notes")
    notesop: Optional[Literal["all", "phrase"]] = Field("all",
                                                        description="'all' to search for all specified words in the notes field; 'phrase' to search for the exact phrase specified")
    text: Optional[str] = Field(description="one or more words for which to search in the text of the publications")
    textop: Optional[Literal["all", "phrase"]] = Field("all",
                                                       description="'all' to search for all specified words in the text field; 'phrase' to search for the exact phrase specified")
    page: int = Field(1, description="1 for the first page of results, 2 for the second, and so on")
    pagesize: int = Field(100, description="the maximum number of results to return per page (default = 100)")
    format: Literal["xml", "json"] = Field("json",
                                           description="'xml' for an XML response or 'json' for JSON (OPTIONAL; 'xml' is the default)")


class SimplePublicationSearchParameters(BaseModel):
    searchterm: str = Field(description="The text for which to search. Add OR in caps between words to allow one match or the other.")
    searchtype: Literal["C", "F"] = Field("C",
                                           description="'C' for a catalog-only search; 'F' for a catalog+full-text search")
    page: int = Field(1, description="1 for the first page of results, 2 for the second, and so on")
    pageSize: int = Field(100, description="the maximum number of results to return per page (default = 100)")


class Author(BaseModel):
    author_id: Optional[str] = Field(None, alias="AuthorID", description="BHL identifier for the author")
    name: Optional[str] = Field(None, alias="Name", description="Personal, corporate, or meeting name.")
    role: Optional[str] = Field(None, alias="Role",
                                description="One of the following values, which identify the role of an author: Personal Name, Corporate Name, Meeting Name, Uncontrolled Name")
    numeration: Optional[str] = Field(None, alias="Numeration", description="Personal numeration.")
    unit: Optional[str] = Field(None, alias="Unit", description="Corporate unit.")
    title: Optional[str] = Field(None, alias="Title", description="Personal title.")
    location: Optional[str] = Field(None, alias="Location", description="Corporate/meeting location.")
    fuller_form: Optional[str] = Field(None, alias="FullerForm", description="Fuller form of name.")
    relationship: Optional[str] = Field(None, alias="Relationship",
                                        description="Relationship of person to work (editor, illustrator).")
    title_of_work: Optional[str] = Field(None, alias="TitleOfWork",
                                         description="Title page title or serial title related to person.")
    dates: Optional[str] = Field(None, alias="Dates", description="Date of birth/death or Corp/Meeting dates.")
    creator_url: Optional[str] = Field(None, alias="CreatorUrl", description="BHL address for the author")
    creation_date: Optional[str] = Field(None, alias="CreationDate",
                                         description="Date and time the author was created in BHL")


class Publication(BaseModel):
    bhl_type: Literal["Title", "Item", "Part"] = Field(alias="BHLType", description="Publication type")
    found_in: Literal["Metadata", "Text", "Both"] = Field(alias="FoundIn")
    item_id: Optional[str] = Field(None, alias="ItemID",
                                   description="BHL Identifier for the publication (if BHLType is Item) or the related BHL Item.")
    title_id: Optional[str] = Field(None, alias="TitleID",
                                    description="BHL Identifier for the publication (if BHLType is Title)")
    volume: Optional[str] = Field(None, alias="Volume",
                                  description="Volume of the publication or the publication's parent work.")
    external_url: Optional[str] = Field(None, alias="ExternalUrl",
                                        description="Non-BHL address for the publication")
    item_url: Optional[str] = Field(None, alias="ItemUrl",
                                    description="	BHL address for the publication (if BHLType is Item) or the related BHL Item.")
    title_url: Optional[str] = Field(None, alias="TitleUrl",
                                     description="BHL address for the publication (if BHLType is Title)")
    material_type: Optional[str] = Field(None, alias="MaterialType",
                                         description="One of the following values, which identify the characteristics of the work: Language material Notated music Manuscript notated music Cartographic material Manuscript cartographic material Projected medium Nonmusical sound recording Musical sound recording Two-dimensional nonprojectable graphic Computer file Kit Mixed materials Three-dimensional artifact or naturally occurring object Manuscript language material")
    publisher_place: Optional[str] = Field(None, alias="PublisherPlace", description="Place of publication")
    publisher_name: Optional[str] = Field(None, alias="PublisherName", description="Publisher of the publication")
    publication_date: Optional[str] = Field(None, alias="PublicationDate",
                                            description="Publishing date of a book or journal publication")
    date: Optional[str] = Field(None, alias="Date", description="Publishing date of a part publication")
    part_url: Optional[str] = Field(None, alias="PartUrl",
                                    description="BHL address for the publication (if BHLType is Part)")
    part_id: Optional[str] = Field(None, alias="PartID",
                                   description="BHL Identifier for the publication (if BHLType is Part)")
    genre: Optional[str] = Field(None, alias="Genre",
                                 description="Value identifying the genre of the publication. Examples include the following: Collection, Monograph/Item, Serial, Article, Chapte,  Journal, Issue, Proceeding Conference, Preprint, Treatment ")
    title: Optional[str] = Field(None, alias="Title", description="The title of the publication")
    container_title: Optional[str] = Field(None, alias="ContainerTitle",
                                           description="The title of the parent work of the publication. If the publication is an article, the ContainerTitle will be the journal in which the article appears.")
    series: Optional[str] = Field(None, alias="Series",
                                  description="Series of the publication or the publication's parent work.")
    issue: Optional[str] = Field(None, alias="Issue",
                                 description="Issue of the publication or the publication's parent work.")
    page_range: Optional[str] = Field(None, alias="PageRange",
                                      description="Combined start and end page information (applies when BHLType is Part)")


class PublicationSearchResponse(BaseModel):
    status: Optional[str] = Field(None, alias="Status")
    error_message: Optional[str] = Field(None, alias="ErrorMessage")
    result: list[Publication] = Field(alias="Result")


class BadResponse(BaseModel):
    message: str
