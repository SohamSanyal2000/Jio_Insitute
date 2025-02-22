from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import search_and_rerank
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# app = FastAPI()

# @app.get("/rerank/")

# def rerank(query:str = "testvalue",count: int = 5):
#     return JSONResponse(content=search_and_rerank.rerank_for_query(query, count))

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class Item(BaseModel):
    query: str
    count: int

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def index():
    return FileResponse('static/index.html', media_type='text/html')


@app.post("/rerank/")
def rerank(item: Item):
    return JSONResponse(content=search_and_rerank.rerank_for_query(item.query, item.count))