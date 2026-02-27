# main.py
import uvicorn
from fastapi import FastAPI
from routes import project_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize the core app
app = FastAPI(title="Generative IDE Backend")

# Plug in your routes
app.include_router(project_router, prefix="/api/v1")

origins = [
    "http://localhost:5173",    # Your local React app
    "http://127.0.0.1:5173",    # Alternative local address
    "*"                         # Allow all (Temporary for debugging)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: Add a health-check root route
@app.get("/")
def read_root():
    return {"status": "Server is running perfectly!"}

if __name__ == "__main__":
    # This allows you to run 'python main.py' directly
    uvicorn.run("main:app", host="127.0.0.1", port=8000)