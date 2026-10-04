from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="TinPyUI Backend")

# Mount public directory for assets (wasm, js, css, images)
# Make sure to run `tinpyui build --web` to populate this directory
app.mount("/public", StaticFiles(directory="public"), name="public")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")

@app.get("/")
async def serve_app():
    """Serves the generated TinPyUI frontend."""
    return FileResponse("dist/index.html")

@app.get("/api/health")
async def health_check():
    """Example API endpoint for TinPyUI frontend to call."""
    return {"status": "healthy", "engine": "tinpyui-fastapi"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
