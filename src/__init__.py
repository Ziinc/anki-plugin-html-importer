# -*- coding: utf-8 -*-

import os
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import csv
from BeautifulSoup import BeautifulSoup

from aqt.qt import *
from aqt import mw
from aqt.utils import showText
from anki.importing import TextImporter
from anki.media import MediaManager
import tempfile
import urllib.parse
import string


import re

from ClaSS2Style import ClaSS2Style

GOOGLE_SHEETS_URL = ""


def _strip_newlines(string):
    return string.replace('\n', '').replace('\r', '')


def parse_html(soup):
    output = ''

    # Write tables content to html file
    for table in soup.findAll('table'):

        for row in table.findAll('tr', recursive=True):
            # showText(str(row))
            tds = [td for td in row.findAll(recursive=False, limit=2)]
            question = _strip_newlines(tds[0].renderContents())
            answer = _strip_newlines(tds[1].renderContents())

            if question.find("font-weight:700") != -1:
                output += '%s\t%s\n' % (question, answer)

            elif question.find("font-weight: 700") != -1:
                output += '%s\t%s\n' % (question, answer)
            else:
                continue

    # Write styles to html file

    return output


def write_img_to_media_col(output, doc_url):
    # get media directory
    media_dir = os.path.join(mw.pm.profileFolder(), "collection.media")
    pattern = re.compile(r'src\s*=\s*"(.+?)"')
    # showText(str(re.findall(pattern, output)))
    for img_url in re.findall(pattern, output):

        doc_path = urllib.parse.urlparse(doc_url).path
        to_rep = ['document', 'pub', 'd/e']
        for ch in to_rep:
            doc_path = doc_path.replace(ch, "")

        im_parse = urllib.parse.urlparse(img_url)
        im_name = im_parse.path + im_parse.params + im_parse.query + im_parse.fragment

        im_name = im_name.replace(
            "cht=tx&amp;chf=bg,s,FFFFFF00&amp;chco=000000&amp;", "")

        # hash the path
        prime = 1
        im_list = []
        doc_list = []
        for i in im_name:
            if i.isalnum():
                im_list.append(i)
            else:
                r = int(ord(i))*prime
                im_list.append(str(r))
        for i in doc_path:
            if i.isalnum():
                doc_list.append(i)
            else:
                r = int(ord(i))*prime
                doc_list.append(str(r))
        im_name = ''.join(im_list)
        doc_path = ''.join(doc_list)

        fname = "img-" + doc_path[:10] + '-' + \
            str(im_name)[:20] + '-' + str(im_name)[-10:] + ".jpg"
        img_path = os.path.join(media_dir, fname)
        # img_url = urllib.quote(img_url)
        img_src = img_url.replace('&amp;', '&')
        if not os.path.isfile(img_path):
            urllib.request.urlretrieve(img_src, img_path)
            # resource = urllib.urlopen(img_url)
            # content = open(img_path,"wb")
            # content.write(resource.read())
            # content.close()
        # Check if image exists in collection.media
        # if os.path.exists(fname):
        #     continue
        # with open(img_path, 'w+') as new_img:
        #     new_img.write(content)

        # replace img src
        url_to_replace = r'"' + img_url + r'"'
        output = output.replace(url_to_replace, r'"' + fname + r'"')

    return output


def write_output_to_html_file(output):
    temp_dir = tempfile.mkdtemp()
    path_to_html = os.path.join(temp_dir, 'import.html')
    with open(path_to_html, 'w+') as html:
        html.write(output)
    return path_to_html


def updated_oldest_card_and_remove_new_duplicates():
    delete_log = ''
    delete_cnt = 0
    # find duplicates
    dupes = mw.col.findDupes("Front")

    # define regex for finding sound tags
    pattern = re.compile(r'\[sound:(.*?)\]')
    if dupes:
        # iterate through each duplicate note found
        for s, nidlist in dupes:
            unsorted_list = []
            for id in nidlist:
                # grab all duplicates of same card and put in list
                for (flds, mod) in mw.col.db.execute("select flds, mod from notes where id= ?", id):
                    note = {'id': id, 'flds': flds, 'mod': mod}
                    unsorted_list.append(note)
            # Find oldest note
            sorted_oldest_first = sorted(
                unsorted_list, key=lambda d: d['id'], reverse=False)
            # oldest note found, with review history
            oldest_note = sorted_oldest_first[0]

            # Find the newest modified note
            sorted_newest_modified_first = sorted(
                unsorted_list, key=lambda d: d['id'], reverse=True)
            # newest note added, that was modified in google docs
            newest_mod_note = sorted_newest_modified_first[0]

            # Finds the new deck id associated with cards from the newest notes added.
            # Find cards of the old note id assigned to the old deck id, and update these cards with the new deck id
            (new_did,) = mw.col.db.execute("""
                SELECT did 
                FROM cards 
                WHERE nid= ?
                LIMIT 1
            """, newest_mod_note['id']).fetchone()
            (old_did,) = mw.col.db.execute("""
                SELECT did 
                FROM cards 
                WHERE nid= ?
                LIMIT 1
            """, oldest_note['id']).fetchone()
            mw.col.db.execute("""
                UPDATE cards 
                SET did=?, usn=?
                WHERE nid= ? AND did=?
            """, new_did, mw.col.usn(), oldest_note['id'], old_did)

            # update data associated with the oldest note to the new data from the newest modified note
            if oldest_note['flds'] != newest_mod_note['flds']:

                # check if the oldest note has a sound tag in it
                search = pattern.search(oldest_note['flds'])
                if search:
                    sound_tag = search.group(0)
                    sep_pos = oldest_note['flds'].find("\x1f")
                    tag_pos = oldest_note['flds'].find(sound_tag)

                    if tag_pos > sep_pos:
                        # runs if tag is on back of card, append to back
                        newest_mod_note['flds'] = newest_mod_note['flds'] + \
                            "\n" + sound_tag

                # assign values to be updated
                new_flds = newest_mod_note['flds']
                new_mod = newest_mod_note['mod']
                old_id = oldest_note['id']
                new_usn = mw.col.usn()
                mw.col.db.execute(
                    "update notes set flds=?,mod=?, usn=? where id=?", new_flds, new_mod, new_usn, old_id)

            # Delete all notes except for the oldest note
            for id in nidlist:
                if id != oldest_note['id']:
                    # mw.col.db.execute("delete from notes where id=?",id)
                    # Remove notes
                    ls = []
                    ls.append(id)
                    mw.col.remNotes(ls)
                else:
                    continue
    mw.col.setMod()
    mw.col.save()
    mw.col.reset()
    mw.reset()
    delete_log += str(delete_cnt) + \
        " cards has been deleted" + "\n\n"
    return delete_log


def delete_empty_cards():
    delete_log = ''
    delete_cnt = 0

    # build blanks list
    search = ''
    blanks = []
    for (sfld, flds, id) in mw.col.db.execute("select sfld, flds, id from notes where sfld= ?", search):
        blanks.append(id)

    # delete all blanks
    for id in blanks:
        # Remove notes
        ls = []
        ls.append(id)
        mw.col.remNotes(ls)
        delete_cnt += 1

    delete_log = str(delete_cnt) + " blank cards has been deleted" + "\n\n"
    return delete_log


def import_data():
    mw.progress.start(immediate=True)
    mw.checkpoint(_("Importing..."))
    txt = ''
    url = GOOGLE_SHEETS_URL
    response = urllib.request.urlopen(url)
    data = csv.reader(response)

    for entry in data:
        deck_name, doc_title, import_flag, doc_url = entry
        # Exclude header
        if (deck_name == 'Deck Name') or (import_flag == 'FALSE'):
            continue

        # Update progress
        mw.checkpoint(_("Importing " + str(deck_name)))

        request = urllib.request.urlopen(doc_url)
        soup = BeautifulSoup(request)
        # remove scripts
        for script in soup.findAll('script'):
            script.extract()
        # showText(unicode(soup))
        # inline_unicode_html = pynliner.fromString(str(soup))
        inline_html = ClaSS2Style(str(soup)).transform()

        # #replace undesirable style that hides bullet points
        # undesirable = "list-style-type:none"
        # cleaned_inline_html = string.replace(inline_unicode_html, undesirable , "")

        # clean html stling
        inline_soup = BeautifulSoup(inline_html)
        # showText(unicode(inline_soup))
        output = parse_html(inline_soup)

        if output.find("\t") == -1:
            # runs if there are no card rows detected for importing
            continue

        # Write media to collection, write output to temp file
        output = write_img_to_media_col(output, doc_url)
        temp_html_path = write_output_to_html_file(output)

        # select deck by name
        deck_id = mw.col.decks.id(deck_name)
        mw.col.decks.select(deck_id)

        # set model id
        model = mw.col.models.byName("Basic")
        deck = mw.col.decks.get(deck_id)
        deck['mid'] = model['id']
        mw.col.decks.save(deck)

        # import into the collection

        ti = TextImporter(mw.col, temp_html_path)
        ti.delimiter = '\t'
        ti.allowHTML = True
        ti.importMode = 2
        mw.pm.profile['importMode'] = 2

        # #check if deck model and TextImporter model matches
        if deck_id != ti.model['did']:
            ti.model['did'] = deck_id
            mw.col.models.save(ti.model)
        # run text importer
        ti.initMapping()
        ti.run()
        txt += "Import Complete for " + deck_name + ".\n"
        if ti.log:
            # manipulate log to show only necessary fields

            for i in ti.log:
                if i.find("added") != -1:
                    txt += i + "\n\n"
            # txt +=  "".join(ti.log) + "\n"

        # Cleanup
        os.remove(temp_html_path)
        temp_dir = os.path.dirname(temp_html_path)
        os.rmdir(temp_dir)
        mw.col.save()
        mw.reset()
    del_log = ''
    del_log += updated_oldest_card_and_remove_new_duplicates()
    del_log += delete_empty_cards()
    txt += del_log
    mw.progress.finish()
    showText(txt)

    mw.reset()


# import_data()
action = QAction("Import from G-Drive", mw)
mw.connect(action, SIGNAL("triggered()"), import_data)
mw.form.menuTools.addAction(action)
