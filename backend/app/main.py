from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import email_processor

app = FastAPI(title="Email Processor API", version="1.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(email_processor.router)

@app.get("/")
def home():
    return {"message": "Welcome to the Email Processor API"}
