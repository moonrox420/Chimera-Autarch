import pytest
import asyncio
import httpx
from multiprocessing import Process
import time
import socket
import os

from chimera_autarch import main as chimera_main

def run_server(port):
    """Run the Chimera server on the given port."""
    os.environ["HTTP_PORT"] = str(port)
    os.environ["WS_PORT"] = str(port + 1)
    asyncio.run(chimera_main())

@pytest.fixture(scope="module")
def free_port():
    """Find a free port to run the server on."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.fixture(scope="module")
def server(free_port):
    """Fixture to run the Chimera server in a separate process."""
    
    p = Process(target=run_server, args=(free_port,))
    p.start()
    
    # Give the server time to start up
    time.sleep(3)
    yield f"http://localhost:{free_port}"
    p.terminate()
    p.join(timeout=5)
    if p.is_alive():
        p.kill()

@pytest.mark.asyncio
async def test_graphql_get_playground(server):
    """Test that GET /graphql returns the GraphQL Playground HTML."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{server}/graphql")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<title>GraphQL Playground</title>" in response.text

@pytest.mark.asyncio
async def test_graphql_post_query(server):
    """Test that POST /graphql with a query returns a JSON response."""
    query = {"query": "{ __schema { types { name } } }"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{server}/graphql", json=query)
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        data = response.json()
        assert "data" in data
        assert "__schema" in data["data"]

