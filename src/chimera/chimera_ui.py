from aiohttp import web
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.resolve()

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000

# You can set this in env: $env:CHIMERA_TOKEN="dev-token-9001"
DEFAULT_TOKEN = os.environ.get("CHIMERA_TOKEN", "dev-token-9001")

INDEX_FILE = BASE_DIR / "chimera_ui.html"

async def index(request: web.Request):
    html = INDEX_FILE.read_text(encoding="utf-8")
    # Inject token safely so you don't hardcode it in the HTML
    html = html.replace("{{CHIMERA_TOKEN}}", DEFAULT_TOKEN)
    return web.Response(text=html, content_type="text/html")

def main():
    app = web.Application()
    app.router.add_get("/", index)
    print(f"✓ Dashboard: http://localhost:{HTTP_PORT}")
    web.run_app(app, host=HTTP_HOST, port=HTTP_PORT)

if __name__ == "__main__":
    main()
