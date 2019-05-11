import requests
import json
import sqlite3
import os

def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_urls():
    with open("config.json") as cfg:
        data = json.load(cfg)
    return data["data_sources"]


def init_scrape(urls):
    db_path = os.path.join(os.getcwd(), "user_files", "cache.db")


    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # check if there is the scrape_results table
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scrape_results'")
    if c.fetchone() is None:
        c.execute("CREATE TABLE IF NOT EXISTS scrape_results (url TEXT PRIMARY KEY, data TEXT)")
        conn.commit()
    conn.close()