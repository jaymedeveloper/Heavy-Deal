import psycopg2

def db():
    return psycopg2.connect("postgresql://neondb_owner:npg_kNH9SLUqyTW0@ep-lingering-wildflower-am8r2086.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")