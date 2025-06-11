import uvicorn
from config.config_loader import settings

if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )