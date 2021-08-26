from fastapi import FastAPI

app = FastAPI(title="FastAPI Template")


@app.get("/")
async def root():
    return {"message": "Hello World"}
