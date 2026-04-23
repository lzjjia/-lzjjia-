import os
import json
import aiofiles
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path("notes")
NOTES_DIR.mkdir(exist_ok=True)

async def save_note(course: str, title: str, content: str) -> str:
    """
    将笔记异步保存为 Markdown 文件
    文件名格式: notes/数学_2025-01-15.md
    """
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = NOTES_DIR / f"{course}_{date_str}.md"
    
    note_content = f"""# {title}
    **课程**: {course}  
    **时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}

    ---

    {content}

    ---
    *由 ATLAS 自动生成*
    """
    async with aiofiles.open(filename, "w", encoding="utf-8") as f:
        await f.write(note_content)
    
    return str(filename)

async def list_notes(course: str = None) -> list[dict]:
    """列出所有已保存的笔记"""
    notes = []
    pattern = f"{course}_*.md" if course else "*.md"
    for filepath in sorted(NOTES_DIR.glob(pattern)):
        notes.append({
            "filename": filepath.name,
            "path": str(filepath),
            "size": filepath.stat().st_size,
            "modified": datetime.fromtimestamp(
                filepath.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M")
        })
    return notes

async def read_note(filename: str) -> str:
    """读取一篇已有的笔记"""
    filepath = NOTES_DIR / filename
    if not filepath.exists():
        return f"找不到笔记文件: {filename}"
    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
        return await f.read()