from pydantic import BaseModel


class Comment(BaseModel):
    id: int
    content: str
    replies: list["Comment"] | None = (
        None  # here comment is the class itself, it is self referencing itself
    )


Comment.model_rebuild()  # this is required after self referencing model


comment = Comment(
    id=1,
    content="First comment",
    replies=[
        Comment(id=2, content="Reply of first comment"),
        Comment(
            id=3,
            content="2nd reply of first comment",
            replies=[
                Comment(id=4, content="inner reply of 2nd reply of first comment")
            ],
        ),
        Comment(id=5, content="3rd reply of first comment"),
    ],
)

# print(comment)


# Optional nested model


class Address(BaseModel):
    street: str
    city: str
    postal_code: str


class Company(BaseModel):
    name: str
    address: Address | None = None


class Employee(BaseModel):
    name: str
    company: Company | None = None


class TextContent(BaseModel):
    text: str = "text"
    content: str


class ImageContent(BaseModel):
    type: str = "Image"
    url: str
    alt_text: str


class Article(BaseModel):
    titlte: str
    sections: list[TextContent | ImageContent]
