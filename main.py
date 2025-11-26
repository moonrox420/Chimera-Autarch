# main.py – health & info endpoints added, port config fixed

from fastapi.responses import JSONResponse
import uvicorn
import os
import time

app = FastAPI(title="CHIMERA AUTARCH v3", version="3.0.0")

# Global startup time for uptime calculation
START_TIME = time.time()

@app.get("/health")
async def health():
    return JSONResponse(status_code=200, content={"status": "healthy"})

@app.get("/info")
async def info():
    return {
        "service": "chimera-autarch",
        "version": "3.0.0",
        "uptime": time.time() - START_TIME,
        "nodes": 0,  # Will be updated when CHIMERA heart is initialized
        "status": "operational"
    }

# Respect environment variables – fixes previous port binding issues
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("HTTP_PORT", 9000
    ))
    uvicorn.run("main:app", host=host, port=port, log_level="info")
