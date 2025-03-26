import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # Path to FastAPI instance
        host="0.0.0.0",  # Allows access from any IP
        port=8000,  # Change as needed
        workers=4,  # Number of worker processes for handling requests
        reload=False,  # Disable reload in production
        log_level="info",  # Log level (debug, info, warning, error)
    )
