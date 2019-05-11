import os

try:
    from aqt.qt import *
    from aqt import mw
    from aqt.utils import showText
    from anki.importing import TextImporter
    from anki.media import MediaManager
except ImportError:
    pass

from src.utils import get_urls, init_scrape

def import_data():
    # get urls from config
    urls = get_urls()
    # scrape urls, storing data, images in sqlite db
    init_scrape(urls)
    # parse scraped pages for flashcards

    # import scraped flashcards only if not already in anki

    # clean sqlite db, storing only required cache



try:
    mw
except:
    pass
else:
    action = QAction("Start HTML Importer", mw)
    action.triggered.connect(import_data)
    mw.form.menuTools.addAction(action)
