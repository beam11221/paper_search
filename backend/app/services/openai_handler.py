from typing import List
import openai
from backend.app.core.config import settings

class OpenAIHandler:
    # Initialize OpenAI API key at class level
    openai.api_key = settings.OPENAI_API_KEY

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = openai.Embedding.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")