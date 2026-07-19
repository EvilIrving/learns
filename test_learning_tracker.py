from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import learning_tracker as tracker

class LearningTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db = self.root / "test.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_init_creates_expected_tables(self) -> None:
        tracker.init_db(self.db)
        with tracker.connect(self.db) as connection:
            names = {row["name"] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertTrue({"topics", "sessions", "goals", "artifacts", "reviews"} <= names)

    def test_add_session_creates_topic_and_record(self) -> None:
        session_id = tracker.add_session(self.db, topic="Python", minutes=45,
            kind="project", result="完成测试", session_date="2026-07-19", confidence=4)
        self.assertGreater(session_id, 0)
        rows = tracker.list_sessions(self.db)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["topic"], "Python")
        self.assertEqual(rows[0]["minutes"], 45)

    def test_invalid_date_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            tracker.add_session(self.db, topic="SQL", minutes=30, kind="practice",
                result="查询练习", session_date="2026-99-99")

    def test_summary_aggregates_sessions(self) -> None:
        tracker.add_session(self.db, topic="Python", minutes=20, kind="practice",
            result="练习一", session_date="2026-07-18", confidence=3)
        tracker.add_session(self.db, topic="Python", minutes=40, kind="project",
            result="练习二", session_date="2026-07-19", confidence=5)
        summary = tracker.get_summary(self.db, days=10000)
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0].sessions, 2)
        self.assertEqual(summary[0].minutes, 60)
        self.assertEqual(summary[0].average_confidence, 4.0)

    def test_export_csv(self) -> None:
        tracker.add_session(self.db, topic="英语", minutes=25, kind="input",
            result="完成听力", session_date="2026-07-19", confidence=2)
        output = self.root / "sessions.csv"
        count = tracker.export_csv(self.db, output)
        self.assertEqual(count, 1)
        with output.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["topic"], "英语")
        self.assertEqual(rows[0]["result"], "完成听力")

if __name__ == "__main__":
    unittest.main()
