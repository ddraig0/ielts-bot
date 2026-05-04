import sqlite3
import datetime
from config import DB_PATH, TRIAL_DAYS

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            joined_at TEXT,
            trial_ends_at TEXT,
            subscription_ends_at TEXT,
            is_banned INTEGER DEFAULT 0
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            months INTEGER,
            confirmed_at TEXT,
            confirmed_by INTEGER
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            section TEXT,
            used_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def register_user(user_id: int, username: str, full_name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cur.fetchone()
    
    if not exists:
        trial_ends = (datetime.datetime.now() + datetime.timedelta(days=TRIAL_DAYS)).isoformat()
        cur.execute("""
            INSERT INTO users (user_id, username, full_name, joined_at, trial_ends_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, full_name, datetime.datetime.now().isoformat(), trial_ends))
        conn.commit()
        conn.close()
        return True  # new user
    conn.close()
    return False  # existing user

def get_user(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0], "username": row[1], "full_name": row[2],
            "joined_at": row[3], "trial_ends_at": row[4],
            "subscription_ends_at": row[5], "is_banned": row[6]
        }
    return None

def has_access(user_id: int) -> bool:
    user = get_user(user_id)
    if not user or user["is_banned"]:
        return False
    now = datetime.datetime.now()
    
    # Check active subscription
    if user["subscription_ends_at"]:
        sub_end = datetime.datetime.fromisoformat(user["subscription_ends_at"])
        if sub_end > now:
            return True
    
    # Check trial
    if user["trial_ends_at"]:
        trial_end = datetime.datetime.fromisoformat(user["trial_ends_at"])
        if trial_end > now:
            return True
    
    return False

def get_access_status(user_id: int) -> dict:
    user = get_user(user_id)
    if not user:
        return {"status": "not_registered"}
    if user["is_banned"]:
        return {"status": "banned"}
    
    now = datetime.datetime.now()
    
    if user["subscription_ends_at"]:
        sub_end = datetime.datetime.fromisoformat(user["subscription_ends_at"])
        if sub_end > now:
            remaining = (sub_end - now).days
            return {"status": "subscribed", "days_left": remaining, "ends_at": user["subscription_ends_at"]}
    
    if user["trial_ends_at"]:
        trial_end = datetime.datetime.fromisoformat(user["trial_ends_at"])
        if trial_end > now:
            remaining = (trial_end - now).days
            return {"status": "trial", "days_left": remaining}
        else:
            return {"status": "trial_expired"}
    
    return {"status": "no_access"}

def add_subscription(user_id: int, months: int, confirmed_by: int, amount: float):
    conn = get_conn()
    cur = conn.cursor()
    
    # Get current subscription end date
    cur.execute("SELECT subscription_ends_at FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    
    now = datetime.datetime.now()
    if row and row[0]:
        current_end = datetime.datetime.fromisoformat(row[0])
        start_from = max(now, current_end)
    else:
        start_from = now
    
    new_end = start_from + datetime.timedelta(days=30 * months)
    
    cur.execute("UPDATE users SET subscription_ends_at = ? WHERE user_id = ?",
                (new_end.isoformat(), user_id))
    cur.execute("""
        INSERT INTO payments (user_id, amount, months, confirmed_at, confirmed_by)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, months, now.isoformat(), confirmed_by))
    
    conn.commit()
    conn.close()
    return new_end

def log_usage(user_id: int, section: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO usage_stats (user_id, section, used_at) VALUES (?, ?, ?)",
                (user_id, section, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, full_name, subscription_ends_at, trial_ends_at, is_banned FROM users")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    
    now = datetime.datetime.now().isoformat()
    cur.execute("SELECT COUNT(*) FROM users WHERE subscription_ends_at > ?", (now,))
    active_subs = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE trial_ends_at > ? AND (subscription_ends_at IS NULL OR subscription_ends_at < ?)", (now, now))
    trials = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM payments")
    total_payments = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(amount) FROM payments")
    total_revenue = cur.fetchone()[0] or 0
    
    conn.close()
    return {
        "total_users": total, "active_subscriptions": active_subs,
        "trial_users": trials, "total_payments": total_payments,
        "total_revenue": total_revenue
    }

def ban_user(user_id: int, ban: bool = True):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (1 if ban else 0, user_id))
    conn.commit()
    conn.close()
