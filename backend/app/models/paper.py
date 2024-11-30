from pydantic import BaseModel

class Paper(BaseModel):
    title: str
    abstract: str
    authors: str
    published: str
    link: str