from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.demo import router as demo_router
from src.routes.sqlite import router as sqlite_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vue frontend running on this port
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(demo_router, prefix="/demo")
app.include_router(sqlite_router, prefix="/sqlite")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)