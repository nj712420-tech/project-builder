# main.py
from fastapi import FastAPI
from routes import project_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize the core app
app = FastAPI(title="Generative IDE Backend")

# Plug in your routes
app.include_router(project_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: Add a health-check root route
@app.get("/")
def read_root():
    return {"status": "Server is running perfectly!"}