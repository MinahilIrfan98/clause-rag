#indexing
# Answering questions from a PDF document using LangChain and Qdrant


from unittest import result

from langchain.chat_models import init_chat_model
from langchain_qdrant import QdrantVectorStore
from pydantic import BaseModel, Field

from app.core.config import get_settings, get_embeddings, get_qdrant_client

NO_ANSWER = "No relevant information found. The Clause shop handbook does not cover that topic."

class Source(BaseModel):
    source: str = Field(min_length=2)
    page: int | None = None
    score: float

class Answer(BaseModel):
    answer: str
    sources: list[Source]
        
class RAGService:
    def __init__(self)->None:
        self.settings = get_settings() #settings class object / instance
        self.client = get_qdrant_client(self.settings)

        if not self.client.collection_exists(collection_name=self.settings.collection):
            raise RuntimeError(f"Collection {self.settings.collection} does not exist")

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.settings.collection,
            embedding=get_embeddings(self.settings)
        )

        self.llm = init_chat_model(
            model=self.settings.chat_model,
            model_provider=self.settings.chat_provider,
            temperature=self.settings.chat_temperature
        )


    

    def ask(self, question: str):
        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty")

        results = [
    (doc, score)
    for doc, score in self.vector_store.similarity_search_with_score(question, k=4)
    if score >= 0.35  # tune this by printing scores for good and bad questions
]

        if not results:
            return Answer(answer=NO_ANSWER, sources=[]) #saves token
        context = "\n\n".join([doc.page_content for doc, score in results]) #string object

        message = [
            {"role": "system", "content": self.settings.system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        return Answer( #gives answer along with the score i.e citation
            answer=self.llm.invoke(input=message).text,
            sources=[
                Source(
                    source=doc.metadata.get("source", "Unknown"),
                    page=doc.metadata.get("page"),
                    score=round(number=score, ndigits=4)
                )
                for doc, score in results
            ]
        )
    def close(self) -> None:
        self.client.close()