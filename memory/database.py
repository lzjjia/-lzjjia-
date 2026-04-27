"""
SQLite 持久化层
数据库文件保存在项目根目录的 atlas_memory.db
表结构：
  memories 表
    id          自增主键
    student     学生姓名（用来隔离不同用户）
    content     记忆内容（文本）
    memory_type 记忆类型：preference/progress/feedback
    created_at  创建时间
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "atlas_memory.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查询结果可以用列名访问
    return conn

def init_db():
    """初始化数据库，创建表（如果不存在）"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student     TEXT NOT NULL,
            content     TEXT NOT NULL,
            memory_type TEXT DEFAULT 'general',
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_memory(student: str, content: str, memory_type: str = "general"):
    """保存一条记忆"""
    init_db()
    conn = get_connection()
    conn.execute(
        "INSERT INTO memories (student, content, memory_type, created_at) VALUES (?, ?, ?, ?)",
        (student, content, memory_type, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_memories(student: str, limit: int = 10) -> list[dict]:
    """
    获取某个学生最近的记忆
    按时间倒序，取最新的 limit 条
    """
    init_db()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT content, memory_type, created_at 
        FROM memories 
        WHERE student = ? 
        ORDER BY created_at DESC 
        LIMIT ?
        """,
        (student, limit)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_memories_by_type(student: str, memory_type: str, limit: int = 5) -> list[dict]:
    """按类型获取记忆，比如只获取学习进度类的记忆"""
    init_db()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT content, memory_type, created_at 
        FROM memories 
        WHERE student = ? AND memory_type = ?
        ORDER BY created_at DESC 
        LIMIT ?
        """,
        (student, memory_type, limit)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_profile(profile: dict):
    """保存学生档案到数据库"""
    init_db()
    conn = get_connection()
    # 先建表（如果不存在）
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            student         TEXT PRIMARY KEY,
            learning_style  TEXT,
            energy_pattern  TEXT,
            current_courses TEXT,
            challenges      TEXT,
            updated_at      TEXT
        )
    """)
    conn.execute("""
        INSERT INTO profiles 
            (student, learning_style, energy_pattern, current_courses, challenges, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(student) DO UPDATE SET
            learning_style  = excluded.learning_style,
            energy_pattern  = excluded.energy_pattern,
            current_courses = excluded.current_courses,
            challenges      = excluded.challenges,
            updated_at      = excluded.updated_at
    """, (
        profile["name"],
        profile["learning_style"],
        profile["energy_pattern"],
        ",".join(profile["current_courses"]),
        ",".join(profile["challenges"]),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def load_profile(name: str) -> dict | None:
    """
    从数据库加载学生档案
    找不到返回 None
    """
    init_db()
    conn = get_connection()
    # 先确保表存在
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            student         TEXT PRIMARY KEY,
            learning_style  TEXT,
            energy_pattern  TEXT,
            current_courses TEXT,
            challenges      TEXT,
            updated_at      TEXT
        )
    """)
    row = conn.execute(
        "SELECT * FROM profiles WHERE student = ?", (name,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "name": row["student"],
        "learning_style": row["learning_style"],
        "energy_pattern": row["energy_pattern"],
        "current_courses": row["current_courses"].split(","),
        "challenges": row["challenges"].split(","),
    }
