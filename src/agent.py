from typing import override, Optional

import dotenv
from ichatbio.agent import IChatBioAgent
from ichatbio.agent_response import ResponseContext
from ichatbio.server import build_agent_app
from ichatbio.types import AgentCard
from pydantic import BaseModel
from starlette.applications import Starlette

from entrypoints import search_bhl


class BHLAgent(IChatBioAgent):
    """
    A simple example agent with a single entrypoint.
    """

    @override
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Biodiversity Heritage Library Search",
            description="Searches for literature in the Biodversity Heritage Library (https://www.biodiversitylibrary.org/).",
            icon=None,
            entrypoints=[
                search_bhl.entrypoint
            ]
        )

    @override
    async def run(self, context: ResponseContext, request: str, entrypoint: str, params: Optional[BaseModel]):
        match entrypoint:
            case search_bhl.entrypoint.id:
                await search_bhl.run(context, request)
            case _:
                raise ValueError()


def create_app() -> Starlette:
    dotenv.load_dotenv()
    agent = BHLAgent()
    app = build_agent_app(agent)
    return app
