from langchain.tools import tool
from rag.vectorstore import search_textbooks, search_notes

@tool
def search_textbook(query: str, course: str = "") -> str:
    """
    从用户上传的教材原文中检索相关内容。
    需要基于教材生成笔记、或查找教材中某个知识点的原始定义时调用。
    比网络搜索更准确，因为来自用户自己的教材。

    Args:
        query: 搜索关键词，如"特征值的定义"
        course: 可选，限定课程，如"线性代数"
    """
    docs = search_textbooks(query, course=course if course else None, k=4)
    if not docs:
        return "教材中没有找到相关内容。提示：先运行 python index_document.py 上传教材。"

    results = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        page = meta.get("page", "")
        page_info = f" 第{page+1}页" if page != "" else ""
        results.append(
            f"【教材片段{i}】{meta.get('source', '')}{page_info}\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(results)

@tool
def search_my_notes(query: str, course: str = "") -> str:
    """
    在学生已保存的历史笔记中语义检索。
    需要回顾已学内容、或避免重复记笔记时调用。

    Args:
        query: 搜索关键词
        course: 可选，限定课程
    """
    docs = search_notes(query, course=course if course else None, k=3)
    if not docs:
        return "笔记中没有找到相关内容。"

    results = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        results.append(
            f"【笔记{i}】{meta.get('title', '')}（{meta.get('course', '')}）\n"
            f"{doc.page_content[:600]}"
        )
    return "\n\n---\n\n".join(results)