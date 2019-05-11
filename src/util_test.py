from unittest.mock import MagicMock
import os
import json
from src.utils import get_urls, init_scrape
import sqlite3

# def get_html_returns_data_test():
#     """
#     Tests whether requests are made correctly.    
#     """
#     class Object(object):
#         pass

#     obj = Object()
#     obj.status_code = 200

#     requests.get = MagicMock(return_value = {
#         "status": 200,
#         "data": '<html></html>'
#     })
#     data = get_html("my_url")
#     requests.get.assert_called_with("my_url")
#     assert data == '<html></html>'

def get_urls_fetches_urls_from_config_json_test():
    mock_config = {
        "data_sources": ["url1", "url2"]
    }
    json.load = MagicMock(return_value = mock_config)
    urls = get_urls()
    assert urls == mock_config["data_sources"]
    assert len(urls) == 2


def init_scrape_creates_sqlite_db_in_user_files_test():
    db = os.path.join(os.getcwd(), "user_files", "cache.db")
    if os.path.isfile(db):
        os.remove(db)
    init_scrape([])
    assert os.path.isfile(db)

    # test if scrape_results table is created
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scrape_results'")
    res = c.fetchone()
    assert res is not None
    conn.close()

    