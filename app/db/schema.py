CREATE_TABLES = [
    """
CREATE TABLE IF NOT EXISTS qywx_token (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    corp_id TEXT NOT NULL,
    corpsecret TEXT NOT NULL,
    access_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    created_at DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE TABLE IF NOT EXISTS alert_receive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE,
    data TEXT,
    receive_time DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE TABLE IF NOT EXISTS alert_send (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT,
    status TEXT,
    error TEXT,
    send_time DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE TABLE IF NOT EXISTS alert_silence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matcher TEXT,
    starts_at DATETIME DEFAULT (datetime('now', '+8 hours')),
    ends_at DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE TABLE IF NOT EXISTS silence_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT NOT NULL,
    duration_part TEXT NOT NULL,
    duration_display TEXT NOT NULL,
    origin TEXT DEFAULT 'duration',
    from_user TEXT NOT NULL,
    status TEXT DEFAULT 'awaiting_reason',
    created_at DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE TABLE IF NOT EXISTS silence_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT NOT NULL,
    duration_display TEXT NOT NULL,
    reason TEXT NOT NULL,
    from_user TEXT NOT NULL,
    created_at DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE INDEX IF NOT EXISTS idx_alert_receive_alert_id ON alert_receive(alert_id)
""",
    """
CREATE INDEX IF NOT EXISTS idx_silence_session_user_status ON silence_session(from_user, status)
""",
    """
CREATE INDEX IF NOT EXISTS idx_silence_info_alert_id ON silence_info(alert_id)
""",
    """
CREATE TABLE IF NOT EXISTS alert_response_code (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE NOT NULL,
    response_code TEXT NOT NULL,
    created_at DATETIME DEFAULT (datetime('now', '+8 hours'))
)
""",
    """
CREATE INDEX IF NOT EXISTS idx_alert_response_code_alert_id ON alert_response_code(alert_id)
""",
]
