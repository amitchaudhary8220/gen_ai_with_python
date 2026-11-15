from curses.ascii import HT
from turtle import pos
from unittest.mock import Base

from pydantic import BaseModel, HttpUrl

print("start of main")


class Cart(BaseModel):
    user_id: int
    items: list[str]
    quantities: dict[str, int]


class BlogPost(BaseModel):
    title: str
    content: str
    image_url: str | None = None


cart_data = {
    "user_id": 123,
    "items": ["Laptop", "Mouse", "Keyboard"],
    "quantities": {"Laptop": 1, "Mouse": 2, "Keyboard": 1},
}

cart = Cart(**cart_data)
# print(cart)


class Image(BaseModel):
    name: str
    url: HttpUrl


class Post(BaseModel):
    name: str
    tags: set[str] = set()
    images: list[Image]


obj = {
    "name": "post1",
    "tags": [
        "treading",
        "fashion",
        "fashion",
        "fashion",
        "fashion",
    ],
    "images": [
        {"name": "img1", "url": "https://www.google.com"},
        {"name": "img2", "url": "https://www.amazon.com"},
    ],
}

post1 = Post(**obj)

print(post1)
