from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split(filepath: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    """加载文件并切分为 chunks，支持 PDF / TXT / MD"""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        docs = PyPDFLoader(filepath).load()
    elif suffix in (".txt",):
        from langchain_community.document_loaders import TextLoader
        docs = TextLoader(filepath, encoding="utf-8").load()
    elif suffix in (".md", ".markdown"):
        from langchain_community.document_loaders import TextLoader
        docs = TextLoader(filepath, encoding="utf-8").load()
    else:
        raise ValueError(f"不支持的格式: {suffix}，支持 PDF / TXT / MD")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    return splitter.split_documents(docs)