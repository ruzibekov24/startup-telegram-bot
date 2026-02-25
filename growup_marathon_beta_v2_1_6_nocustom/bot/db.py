import aiosqlite
from datetime import datetime

DB_PATH = "growup.sqlite3"

# v2 schema: score is set by moderators, not auto.
SCHEMA_V2 = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  username TEXT,
  full_name TEXT,
  joined_at TEXT,
  is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS season (
  id INTEGER PRIMARY KEY CHECK (id=1),
  name TEXT,
  start_date TEXT,
  end_date TEXT,
  is_registration_open INTEGER DEFAULT 1,
  is_running INTEGER DEFAULT 0
);
INSERT OR IGNORE INTO season (id, name, start_date, end_date, is_registration_open, is_running)
VALUES (1, 'Grow Up Marathon Beta', NULL, NULL, 1, 0);

-- New submissions table for v2
CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  day_index INTEGER NOT NULL,
  file_id TEXT NOT NULL,
  duration_sec INTEGER NOT NULL,
  submitted_at TEXT NOT NULL,

  status TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected
  score INTEGER,                           -- NULL until rated
  rated_by INTEGER,
  rated_at TEXT,
  comment TEXT,

  UNIQUE(user_id, day_index)
);

CREATE TABLE IF NOT EXISTS warnings (
  user_id INTEGER PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eliminations (
  user_id INTEGER PRIMARY KEY,
  eliminated_at TEXT NOT NULL,
  reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS announcements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  created_by INTEGER NOT NULL,
  text TEXT NOT NULL,
  button_text TEXT,
  button_url TEXT,
  channel_message_id INTEGER
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # If old v1 schema exists, migrate submissions table.
        await _maybe_migrate_submissions(db)
        await db.executescript(SCHEMA_V2)
        await db.commit()

async def _maybe_migrate_submissions(db: aiosqlite.Connection):
    # If submissions table exists and has NOT NULL score (v1), rebuild it.
    cur = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='submissions'")
    if await cur.fetchone() is None:
        return

    cur = await db.execute("PRAGMA table_info(submissions)")
    cols = await cur.fetchall()
    # cols: (cid, name, type, notnull, dflt_value, pk)
    col_map = {c[1]: c for c in cols}
    if "score" in col_map and int(col_map["score"][3]) == 1:  # notnull==1 in v1
        await db.execute("ALTER TABLE submissions RENAME TO submissions_v1")
        await db.commit()

        await db.executescript("""
        CREATE TABLE submissions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          day_index INTEGER NOT NULL,
          file_id TEXT NOT NULL,
          duration_sec INTEGER NOT NULL,
          submitted_at TEXT NOT NULL,

          status TEXT NOT NULL DEFAULT 'approved',
          score INTEGER,
          rated_by INTEGER,
          rated_at TEXT,
          comment TEXT,

          UNIQUE(user_id, day_index)
        );
        """)
        # migrate old rows as already approved (score preserved)
        await db.execute("""
            INSERT INTO submissions(id, user_id, day_index, file_id, duration_sec, submitted_at, status, score)
            SELECT id, user_id, day_index, file_id, duration_sec, submitted_at, 'approved', score
            FROM submissions_v1
        """)
        await db.execute("DROP TABLE submissions_v1")
        await db.commit()

async def upsert_user(user_id: int, username: str | None, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users(user_id, username, full_name, joined_at, is_active)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
              username=excluded.username,
              full_name=excluded.full_name,
              is_active=1
            """,
            (user_id, username, full_name, datetime.utcnow().isoformat()),
        )
        await db.commit()

async def get_season():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT name, start_date, end_date, is_registration_open, is_running FROM season WHERE id=1"
        )
        return await cur.fetchone()

async def set_season_dates(start_date: str, end_date: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE season SET start_date=?, end_date=? WHERE id=1", (start_date, end_date))
        await db.commit()

async def set_registration(open_: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE season SET is_registration_open=? WHERE id=1", (1 if open_ else 0,))
        await db.commit()

async def set_running(running: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE season SET is_running=? WHERE id=1", (1 if running else 0,))
        await db.commit()

async def is_eliminated(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM eliminations WHERE user_id=?", (user_id,))
        return await cur.fetchone() is not None

# --------- Submissions (v2) ---------

async def create_submission(user_id: int, day_index: int, file_id: str, duration_sec: int, submitted_at: str) -> int | None:
    """Create a pending submission. Returns submission_id or None if already submitted that day."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cur = await db.execute(
                """
                INSERT INTO submissions(user_id, day_index, file_id, duration_sec, submitted_at, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
                """,
                (user_id, day_index, file_id, duration_sec, submitted_at),
            )
            await db.commit()
            return int(cur.lastrowid)
        except aiosqlite.IntegrityError:
            return None

async def set_submission_rating(submission_id: int, score: int, rated_by: int, comment: str | None = None) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            UPDATE submissions
            SET status='approved', score=?, rated_by=?, rated_at=?, comment=?
            WHERE id=? AND status='pending'
            """,
            (score, rated_by, datetime.utcnow().isoformat(), comment, submission_id),
        )
        await db.commit()
        return cur.rowcount > 0

async def reject_submission(submission_id: int, rated_by: int, comment: str | None = None) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            UPDATE submissions
            SET status='rejected', score=NULL, rated_by=?, rated_at=?, comment=?
            WHERE id=? AND status='pending'
            """,
            (rated_by, datetime.utcnow().isoformat(), comment, submission_id),
        )
        await db.commit()
        return cur.rowcount > 0

async def get_submission(submission_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT id, user_id, day_index, file_id, duration_sec, submitted_at, status, score, rated_by, rated_at, comment
            FROM submissions WHERE id=?
            """,
            (submission_id,),
        )
        return await cur.fetchone()

async def get_pending_submissions(limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT id, user_id, day_index, duration_sec, submitted_at
            FROM submissions
            WHERE status='pending'
            ORDER BY submitted_at ASC
            LIMIT ?
            """,
            (limit,),
        )
        return await cur.fetchall()

async def get_total_score(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COALESCE(SUM(score),0) FROM submissions WHERE user_id=? AND status='approved' AND score IS NOT NULL",
            (user_id,),
        )
        (s,) = await cur.fetchone()
        return int(s)

async def get_pending_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(1) FROM submissions WHERE user_id=? AND status='pending'", (user_id,))
        (c,) = await cur.fetchone()
        return int(c)

async def get_leaderboard(limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT u.user_id, u.full_name, COALESCE(SUM(s.score),0) AS total
            FROM users u
            LEFT JOIN submissions s ON s.user_id=u.user_id AND s.status='approved' AND s.score IS NOT NULL
            LEFT JOIN eliminations e ON e.user_id=u.user_id
            WHERE u.is_active=1 AND e.user_id IS NULL
            GROUP BY u.user_id
            ORDER BY total DESC, u.user_id ASC
            LIMIT ?
            """,
            (limit,),
        )
        return await cur.fetchall()

# --------- Warnings / Eliminations ---------

async def get_warning_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT count FROM warnings WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return int(row[0]) if row else 0

async def inc_warning(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.utcnow().isoformat()
        await db.execute(
            """
            INSERT INTO warnings(user_id, count, updated_at) VALUES (?, 1, ?)
            ON CONFLICT(user_id) DO UPDATE SET count=count+1, updated_at=excluded.updated_at
            """,
            (user_id, now),
        )
        await db.commit()
    return await get_warning_count(user_id)

async def eliminate(user_id: int, reason: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO eliminations(user_id, eliminated_at, reason) VALUES (?, ?, ?)",
            (user_id, datetime.utcnow().isoformat(), reason),
        )
        await db.commit()

# --------- Announcements ---------

async def create_announcement(created_by: int, text: str, button_text: str | None, button_url: str | None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO announcements(created_at, created_by, text, button_text, button_url) VALUES (?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), created_by, text, button_text, button_url),
        )
        await db.commit()
        return int(cur.lastrowid)

async def set_announcement_message_id(ann_id: int, channel_message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE announcements SET channel_message_id=? WHERE id=?",
            (channel_message_id, ann_id),
        )
        await db.commit()
