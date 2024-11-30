from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.core.config import settings

app = FastAPI(title="Academic Paper Search API")

# Include routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True
    )