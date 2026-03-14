from fastapi import FastAPI
from app.api.router import router

app = FastAPI(
    title="Integration Service",
    root_path="/integration-service",
)

app.include_router(router)
