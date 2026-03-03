from fastapi import FastAPI

app = FastAPI(title="API Gateway")

@app.get("/health")
async def health():
    return {"status": "ok"}
