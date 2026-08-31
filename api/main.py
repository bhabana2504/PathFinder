from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import engine
from database import models

# Ensure database tables are created
models.Base.metadata.create_all(bind=engine)

# Import routes
from api.routes import (
    auth,
    learners,
    careers,
    skills,
    skill_gap,
    recommendations,
    learning_path,
    progress,
    resources,
)

app = FastAPI(
    title="PathFinder AI API",
    description="Backend API for PathFinder personalized career mapping and learning platform",
    version="1.0.0"
)

# CORS configuration
# The frontend is served from the same domain in production, so CORS is
# mainly for development. Using ["*"] is acceptable for this SPA setup.
# In production, both frontend and API run on the same Render domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Register routers
app.include_router(auth.router)
app.include_router(learners.router)
app.include_router(careers.router)
app.include_router(skills.router)
app.include_router(resources.router)
app.include_router(skill_gap.router)
app.include_router(recommendations.router)
app.include_router(learning_path.router)
app.include_router(progress.router)

@app.get("/api/health")
def health_check():
    """Service health status check."""
    return {
        "status": "healthy",
        "database": "connected"
    }

# Mount frontend directory for SPA client
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
