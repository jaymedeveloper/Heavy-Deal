import psycopg2

def db():
    """Returns a database connection with IST timezone"""
    conn = psycopg2.connect(
        "postgresql://neondb_owner:npg_kNH9SLUqyTW0@ep-lingering-wildflower-am8r2086.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )
    # ✅ Set timezone to IST for this connection
    cur = conn.cursor()
    cur.execute("SET timezone = 'Asia/Kolkata'")
    cur.close()
    return conn
