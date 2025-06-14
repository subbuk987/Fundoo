import uvicorn
from config.config_loader import api_settings

if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host=api_settings.API_HOST,
        port=api_settings.API_PORT,
        reload=True
    )