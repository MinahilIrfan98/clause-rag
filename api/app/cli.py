from services.ingestion import ingest
from services.chat import RAGService


# print(f"Ingested {ingest()} chunks")


def main():
    rag_service = RAGService()
    try:
        query = input("You: ").strip()
        result = rag_service.ask(question=query)
        print(f"AI: {result.answer}")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        rag_service.close()

if __name__ == "__main__":
    main()