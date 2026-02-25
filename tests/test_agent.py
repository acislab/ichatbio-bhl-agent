import pytest
import pytest_asyncio
from ichatbio.agent_response import ArtifactResponse

from src.agent import BHLAgent


@pytest_asyncio.fixture()
def agent():
    return BHLAgent()


@pytest.mark.asyncio
async def test_search_bhl(agent, context, messages):
    await agent.run(context, "Rattus rattus in Colombia", "search_bhl", None)

    artifact: ArtifactResponse = next((m for m in messages if type(m) is ArtifactResponse), None)
    assert artifact
    assert artifact.mimetype == "application/json"
    assert "BHL search results" in artifact.description
    assert artifact.content is not None
