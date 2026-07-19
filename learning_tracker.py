#!/usr/bin/env python3
"""A small SQLite learning-session tracker using only the standard library."""
from __future__ import annotations

import argparse
import csv
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_DB = Path(__file__).with_name("learns.db")
SCHEMA_FILE = Path(__file__).with_name("schema.sql")
SEED_FILE = Path(__file__).with_name("seed.sql")
KINDS = ("input", "practice", "project", "review", "test")

@dataclass(frozen=True)
class TopicSummary:
    topic: str
    sessions: int
    minutes: int
    average_confidence: float | None
    latest_date: str | None

def connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db(db_path: Path) -> None:
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"找不到 schema 文件：{SCHEMA_FILE}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as connection:
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

def seed_db(db_path: Path) -> None:
    init_db(db_path)
    if not SEED_FILE.exists():
        raise FileNotFoundError(f"找不到 seed 文件：{SEED_FILE}")
    with connect(db_path) as connection:
        connection.executescript(SEED_FILE.read_text(encoding="utf-8"))

def validate_iso_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"日期必须是 YYYY-MM-DD：{value}") from exc

def get_or_create_topic(connection: sqlite3.Connection, name: str) -> int:
    normalized = name.strip()
    if not normalized:
        raise ValueError("主题不能为空")
    connection.execute(
        "INSERT OR IGNORE INTO topics(name, category, status) VALUES (?, 'core', 'active')",
        (normalized,),
    )
    row = connection.execute("SELECT id FROM topics WHERE name = ?", (normalized,)).fetchone()
    if row is None:
        raise RuntimeError(f"无法创建或读取主题：{normalized}")
    return int(row["id"])

def add_session(db_path: Path, *, topic: str, minutes: int, kind: str, result: str,
                session_date: str | None = None, confidence: int | None = None,
                source: str = "own") -> int:
    if minutes <= 0:
        raise ValueError("分钟数必须大于 0")
    if kind not in KINDS:
        raise ValueError(f"kind 必须是：{', '.join(KINDS)}")
    if confidence is not None and not 1 <= confidence <= 5:
        raise ValueError("confidence 必须在 1 到 5 之间")
    normalized_result = result.strip()
    if not normalized_result:
        raise ValueError("result 不能为空")
    init_db(db_path)
    actual_date = validate_iso_date(session_date or date.today().isoformat())
    with connect(db_path) as connection:
        topic_id = get_or_create_topic(connection, topic)
        cursor = connection.execute(
            """INSERT INTO sessions(topic_id, session_date, minutes, kind, result, confidence, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (topic_id, actual_date, minutes, kind, normalized_result, confidence, source.strip() or "own"),
        )
        return int(cursor.lastrowid)

def get_summary(db_path: Path, *, days: int = 30) -> list[TopicSummary]:
    if days <= 0:
        raise ValueError("days 必须大于 0")
    init_db(db_path)
    modifier = f"-{days - 1} days"
    with connect(db_path) as connection:
        rows = connection.execute(
            """SELECT t.name AS topic, COUNT(s.id) AS session_count,
                      COALESCE(SUM(s.minutes), 0) AS total_minutes,
                      AVG(s.confidence) AS average_confidence,
                      MAX(s.session_date) AS latest_date
               FROM topics t
               LEFT JOIN sessions s ON s.topic_id = t.id
                 AND s.session_date >= date('now', ?)
               GROUP BY t.id, t.name
               HAVING COUNT(s.id) > 0
               ORDER BY total_minutes DESC, t.name""",
            (modifier,),
        ).fetchall()
    return [TopicSummary(
        topic=str(row["topic"]), sessions=int(row["session_count"]),
        minutes=int(row["total_minutes"]),
        average_confidence=float(row["average_confidence"]) if row["average_confidence"] is not None else None,
        latest_date=str(row["latest_date"]) if row["latest_date"] is not None else None,
    ) for row in rows]

def list_sessions(db_path: Path, *, limit: int = 20) -> list[sqlite3.Row]:
    if limit <= 0:
        raise ValueError("limit 必须大于 0")
    init_db(db_path)
    with connect(db_path) as connection:
        return connection.execute(
            """SELECT s.id, s.session_date, t.name AS topic, s.minutes, s.kind,
                      s.result, s.confidence, s.source
               FROM sessions s JOIN topics t ON t.id = s.topic_id
               ORDER BY s.session_date DESC, s.id DESC LIMIT ?""", (limit,)
        ).fetchall()

def export_csv(db_path: Path, output_path: Path) -> int:
    rows = list_sessions(db_path, limit=1_000_000)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "session_date", "topic", "minutes", "kind", "result", "confidence", "source"]
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row[name] for name in fieldnames})
    return len(rows)

def format_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    materialized = [[str(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in materialized:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    def render(row: Sequence[str]) -> str:
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))
    line = "  ".join("-" * width for width in widths)
    return "\n".join([render(list(headers)), line, *(render(row) for row in materialized)])

def print_summary(db_path: Path, *, days: int) -> None:
    summaries = get_summary(db_path, days=days)
    if not summaries:
        print(f"最近 {days} 天没有学习记录。")
        return
    rows = []
    for item in summaries:
        confidence = f"{item.average_confidence:.2f}" if item.average_confidence is not None else "-"
        rows.append((item.topic, item.sessions, item.minutes, confidence, item.latest_date or "-"))
    print(f"最近 {days} 天：")
    print(format_table(("主题", "次数", "分钟", "平均信心", "最近日期"), rows))

def print_sessions(db_path: Path, *, limit: int) -> None:
    rows = list_sessions(db_path, limit=limit)
    if not rows:
        print("没有学习记录。")
        return
    print(format_table(("日期", "主题", "分钟", "方式", "信心", "结果"), (
        (row["session_date"], row["topic"], row["minutes"], row["kind"],
         row["confidence"] if row["confidence"] is not None else "-", row["result"])
        for row in rows
    )))

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="个人学习记录工具")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"SQLite 路径，默认：{DEFAULT_DB.name}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="初始化数据库")
    subparsers.add_parser("seed", help="加载可重复演示数据")
    add_parser = subparsers.add_parser("add", help="增加学习记录")
    add_parser.add_argument("--topic", required=True)
    add_parser.add_argument("--minutes", type=int, required=True)
    add_parser.add_argument("--kind", choices=KINDS, required=True)
    add_parser.add_argument("--result", required=True)
    add_parser.add_argument("--date", dest="session_date")
    add_parser.add_argument("--confidence", type=int, choices=range(1, 6))
    add_parser.add_argument("--source", default="own")
    summary_parser = subparsers.add_parser("summary", help="按主题汇总")
    summary_parser.add_argument("--days", type=int, default=30)
    list_parser = subparsers.add_parser("list", help="列出最近记录")
    list_parser.add_argument("--limit", type=int, default=20)
    export_parser = subparsers.add_parser("export", help="导出 CSV")
    export_parser.add_argument("--output", type=Path, required=True)
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init_db(args.db); print(f"数据库已初始化：{args.db}")
        elif args.command == "seed":
            seed_db(args.db); print(f"演示数据已加载：{args.db}")
        elif args.command == "add":
            session_id = add_session(args.db, topic=args.topic, minutes=args.minutes,
                kind=args.kind, result=args.result, session_date=args.session_date,
                confidence=args.confidence, source=args.source)
            print(f"已增加学习记录 #{session_id}")
        elif args.command == "summary":
            print_summary(args.db, days=args.days)
        elif args.command == "list":
            print_sessions(args.db, limit=args.limit)
        elif args.command == "export":
            count = export_csv(args.db, args.output); print(f"已导出 {count} 条记录：{args.output}")
    except (FileNotFoundError, RuntimeError, sqlite3.Error, ValueError) as exc:
        parser.exit(2, f"错误：{exc}\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
