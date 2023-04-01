from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Order(BaseModel):
    top_color: str
    bottom_color: str
    top_fuse: bool
    bottom_fuse: bool
    top_hole: bool
    bottom_hole: bool


app = FastAPI()
origins = [
    "http://localhost:5173/",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
def read_order(order: Order):
    print(order)
    return {"Status": "success"}
