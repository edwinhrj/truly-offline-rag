from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.sqlite_routes import router as sqlite_router
from src.routes.query_routes import router as query_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # vue frontend running on this port
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(sqlite_router, prefix="/sqlite")
app.include_router(query_router, prefix="/query")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)