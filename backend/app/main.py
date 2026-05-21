from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# Explicit, direct absolute imports to stop Python naming collisions
import app.routers.auth as auth_router
import app.routers.tasks as tasks_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# Fully open CORS configuration to guarantee zero blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Explicitly mount the APIRouters
app.include_router(auth_router.router)
app.include_router(tasks_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Task Manager API!", "documentation": "/docs"}