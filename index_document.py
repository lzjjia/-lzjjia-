"""
教材上传脚本
用法：
  python index_document.py --file 线性代数.pdf --course 数学
  python index_document.py --list
"""
import argparse
import asyncio
import sys
from pathlib import Path

async def index_file(filepath: str, course: str, chunk_size: int, chunk_overlap: int):
    from rag.document_loader import load_and_split
    from rag.vectorstore import add_textbook_chunks

    path = Path(filepath)
    if not path.exists():
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    print(f"\n📄 处理: {path.name}  课程: {course}")
    print("   解析中...", end="", flush=True)
    chunks = load_and_split(filepath, chunk_size, chunk_overlap)
    print(f"\r   解析完成，共 {len(chunks)} 个文本块")
    print("   存入向量库...", end="", flush=True)
    count = await add_textbook_chunks(chunks, course, path.name)
    print(f"\r   ✅ 成功存入 {count} 个文本块")
    print(f"\n🎉 完成！现在可以问 ATLAS 关于《{path.name}》的问题了。")

def list_files(course: str = None):
    from rag.vectorstore import list_indexed_files
    files = list_indexed_files(course)
    if not files:
        print("向量库为空，请先上传教材。")
        return
    print("\n📚 已索引教材：")
    for f in files:
        print(f"  · [{f['course']}] {f['filename']}")

def main():
    parser = argparse.ArgumentParser(description="ATLAS 教材索引工具")
    parser.add_argument("--file", "-f", type=str, help="文件路径（PDF/TXT/MD）")
    parser.add_argument("--course", "-c", type=str, help="课程名称")
    parser.add_argument("--list", "-l", action="store_true", help="列出已索引文件")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    args = parser.parse_args()

    if args.list:
        list_files(args.course)
        return
    if not args.file:
        parser.print_help()
        return
    if not args.course:
        args.course = Path(args.file).stem.split("_")[0]
        print(f"⚠️  未指定课程名，使用: 「{args.course}」")

    asyncio.run(index_file(args.file, args.course, args.chunk_size, args.chunk_overlap))

if __name__ == "__main__":
    main()