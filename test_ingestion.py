from app.ingest.ingest import ingest_documents

print("Starting document ingestion...")

vector_store = ingest_documents()

print("Document ingestion completed successfully!")
print(vector_store)