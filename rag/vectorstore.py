import asyncio
from langchain_chroma import Chroma
from langchain_core.documents import Document
from rag.embeddings import get_embeddings

CHROMA_DIR = "chroma_db"

def get_textbook_store() -> Chroma:
    return Chroma(
        collection_name="atlas_textbooks",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )

def get_notes_store() -> Chroma:
    return Chroma(
        collection_name="atlas_notes",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )

async def add_textbook_chunks(chunks: list, course: str, filename: str) -> int:
    db = get_textbook_store()
    for chunk in chunks:
        chunk.metadata.update({"course": course, "source": filename, "type": "textbook"})
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, db.add_documents, chunks)
    return len(chunks)

async def add_note_to_vectorstore(content: str, course: str, title: str, filepath: str):
    db = get_notes_store()
    doc = Document(
        page_content=content,
        metadata={"course": course, "title": title, "filepath": filepath, "type": "note"}
    )
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, db.add_documents, [doc])

def search_textbooks(query: str, course: str = None, k: int = 4) -> list:
    db = get_textbook_store()
    filter_dict = {"course": course} if course else None
    try:
        return db.similarity_search(query, k=k, filter=filter_dict)
    except Exception:
        return []

def search_notes(query: str, course: str = None, k: int = 3) -> list:
    db = get_notes_store()
    filter_dict = {"course": course} if course else None
    try:
        return db.similarity_search(query, k=k, filter=filter_dict)
    except Exception:
        return []

def list_indexed_files(course: str = None) -> list:
    try:
        db = get_textbook_store()
        result = db.get()
        metadatas = result.get("metadatas", [])
        seen = set()
        files = []
        for m in metadatas:
            key = (m.get("course", ""), m.get("source", ""))
            if key not in seen and (not course or m.get("course") == course):
                seen.add(key)
                files.append({"course": m.get("course", ""), "filename": m.get("source", "")})
        return files
    except Exception:
        return []