"""Exercise the local SQLite boundary described in PAY-06, without provider claims."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path


SCHEMA = """
CREATE TABLE attempts (id TEXT PRIMARY KEY, state TEXT NOT NULL);
CREATE TABLE reversal_intents (
    original_operation_id TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL
);
"""


def queue_reversal(conn: sqlite3.Connection, operation_id: str, *, fail_before_insert=False):
    conn.execute("BEGIN")
    try:
        updated = conn.execute(
            "UPDATE attempts SET state = 'REVERSAL_PENDING' "
            "WHERE id = ? AND state = 'UNKNOWN'", (operation_id,)
        ).rowcount
        if updated != 1:
            raise ValueError("attempt is not UNKNOWN")
        if fail_before_insert:
            raise RuntimeError("simulated process failure before outbox insert")
        conn.execute(
            "INSERT INTO reversal_intents(original_operation_id, state) "
            "VALUES (?, 'PENDING')", (operation_id,)
        )
        conn.commit()
    except BaseException:
        conn.rollback()
        raise


class PaymentOutboxTransactionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "journal.db"
        self.conn = sqlite3.connect(self.path, isolation_level=None)
        self.conn.executescript(SCHEMA)
        self.conn.execute("INSERT INTO attempts VALUES ('op-42', 'UNKNOWN')")

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_failure_between_local_writes_rolls_back_status(self):
        with self.assertRaises(RuntimeError):
            queue_reversal(self.conn, "op-42", fail_before_insert=True)
        self.assertEqual("UNKNOWN", self.conn.execute(
            "SELECT state FROM attempts WHERE id = 'op-42'"
        ).fetchone()[0])
        self.assertEqual(0, self.conn.execute("SELECT count(*) FROM reversal_intents").fetchone()[0])

    def test_committed_pair_is_recoverable_after_connection_restart(self):
        queue_reversal(self.conn, "op-42")
        self.conn.close()
        self.conn = sqlite3.connect(self.path, isolation_level=None)
        self.assertEqual("REVERSAL_PENDING", self.conn.execute(
            "SELECT state FROM attempts WHERE id = 'op-42'"
        ).fetchone()[0])
        self.assertEqual([("op-42", "PENDING")], self.conn.execute(
            "SELECT original_operation_id, state FROM reversal_intents"
        ).fetchall())

    def test_duplicate_attempt_does_not_create_another_intent(self):
        queue_reversal(self.conn, "op-42")
        with self.assertRaises(ValueError):
            queue_reversal(self.conn, "op-42")
        self.assertEqual(1, self.conn.execute("SELECT count(*) FROM reversal_intents").fetchone()[0])


if __name__ == "__main__":
    unittest.main()
