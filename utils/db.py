import sqlite3
import datetime
import streamlit as st
import pandas as pd

DB_FILE = "resume_app.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            login_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_login(email):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        now = datetime.datetime.now()
        
        # Check if user exists
        c.execute('SELECT login_count FROM users WHERE email = ?', (email,))
        result = c.fetchone()
        
        if result:
            new_count = result[0] + 1
            c.execute('''
                UPDATE users 
                SET last_seen = ?, login_count = ? 
                WHERE email = ?
            ''', (now, new_count, email))
        else:
            c.execute('''
                INSERT INTO users (email, first_seen, last_seen, login_count) 
                VALUES (?, ?, ?, 1)
            ''', (email, now, now))
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Log Error: {e}")

def get_stats():
    try:
        conn = sqlite3.connect(DB_FILE)
        
        # Total users
        df = pd.read_sql_query("SELECT * FROM users", conn)
        total_users = len(df)
        
        # Active in last 24h
        time_threshold = datetime.datetime.now() - datetime.timedelta(days=1)
        active_users = len(df[pd.to_datetime(df['last_seen']) > time_threshold])
        
        conn.close()
        return {
            "total_users": total_users,
            "active_24h": active_users,
            "data": df
        }
    except Exception as e:
        return {"total_users": 0, "active_24h": 0, "data": pd.DataFrame()}
