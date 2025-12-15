"""
Simple test to check if the auth router is working
"""
from fastapi import FastAPI
from app.routers.auth_router_simple import router as auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)