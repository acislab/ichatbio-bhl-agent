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
            icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAABnRSTlMAAAAAAABupgeRAAACrUlEQVR4AWL4+uMF7RADEAwKC0YtWL9hUmlpUlJSUGQkQF6hoe4JiQFz5zXDFU2eUl1engwk0TRPmVpTVZU2Zy5IJYCTctCxK4rCcFDzGscY6xHGtm3bU9uIajeo4tp6lfI9+iV7quvMxTkrS/8y+tDoRAY4cnTKtlWPxynLfk0PpqYZM7NdHz/dFUoDgw3p6XZff12IMZzsnJTZuW7o+YXenJwUOJEBJibbt27dHAx6a+sKx8Zb29srW9vKl1cGnjy9hBTa4dheXZ0XYlxTW+ByO3r76qD7+xvcbgc6kQFwqij+mpr8PwIKlZZuiehGRptVNQAnxBhgVQsMjzRDj462otPUVBIZAHFSkjY83PwvwPoN6+sbCqEnpzqQ9vTUhhgTu2Wro2MtogaWpQAZGQAXpinX1xf9EdDtrOxkKiuMDUOurS0IMa6rLzRMeWKyLT7A0nK/JPkIs6GxmIg6u6oZpKPHpt+8vSmM/X430rq6QtrY3VPDE+/JyTptW1jsiw+wZ++wz+fatm0LMKSSmmpQ96fPLiESxi7XDqRByavpkqYFmTRJ8sLxel1McKIZ2LZGlWga9SGDY8dn3r679ScDpFSJTpAfT2hyip9BSA+ev7j67fvHV6+vg8GMYxyrB3WhPWC+40zR128f1zZF4+NtrCo6sfeg4MXLaz9+fn795gYAqWkm+yz2QIu6B0FKKgDwUFWVF2uTaQNVgqY+GNMYbtTvTd4Re5PJUniASf/Ae/Dg3H+3iAp6PA5uka5LTBGxf/i4eoswSEuzcBR+i7KyV2/RocOTpik8+FQ1yF06fXrhv2tKvDhqa6tg3bEUN1L8Ll7ax60Nv5RwmO9bt49BP3x0nq3EA32mmENDjfd/bWnnyKnRRi24/PQz7RDIgsCSXtqhQWDBqAV0AAA7R59ljLi7xwAAAABJRU5ErkJggg==",
            documentation_url="https://github.com/acislab/ichatbio-bhl-agent",
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
