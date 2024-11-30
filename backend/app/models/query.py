from pydantic import BaseModel

class Query(BaseModel):
    query_text: str
    top_k: int = 2