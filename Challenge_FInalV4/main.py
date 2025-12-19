from fastapi import FastAPI
from app.api.chat import router as chat_router
# Import other routers as needed, e.g., from .api.other import router as other_router

# Create FastAPI app
app = FastAPI(
    title="Pi-eza Dental API",
    description="API for Pi-eza Dental clinic chatbot",
    version="1.0.0"
)


# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
# app.include_router(other_router, prefix="/api", tags=["other"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Pi-eza Dental API"}

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    import uvicorn
    # Change 'main:app' to 'app.main:app'
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)