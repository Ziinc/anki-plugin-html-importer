# Google Sheets/Docs Anki Importer

Anki shared addon: https://ankiweb.net/shared/info/2012433609

A script to load published HTML google doc files into anki. Each table row in a google docs file will become an anki note. Anki card customization is not supported with this plugin, hence it assumes that it is a conventional 2 sided flashcard, 1 side for the question/prompt and the other for the answer.

Note:

- Only data included in tables will be imported.
- Nested tables are currently not supported, use at your own risk. Table formatting may get messed up if you do so.
- Left column specifies the prompt, and the right column specifies the answer.
- To flag out to the script that you want to import that particular row, the left column must contain something that is bolded. If no text bolding is detected, it will not be imported. Note that only Google Docs default text bolding weight is supported, customization to the bolding weight is not supported.
- Images are supported, as well as google docs equations.

How to use:
0.1: Create a Google Docs, with a two-column table format. Publish this as a HTML.
0.2: Create a new Google Sheets, with the following columns in order: Deck Name, Document Title, Import Flag, To Import URL - Deck Name: Specifies the destination deck for the google docs cards.. Allows Hierarchy. E.g. for a deck called "Business" with a sub-deck called "Marketing" and "Operations", use the following:
Business::Marketing
Business::Operations - Document Title: For easier reference, use a sheets formula =importxml(D2,"//title/text()") , where the D2 is the reference to that row's "To Import Url". What this formula does is that it checks the title of the html page, and shows the title. - Import Flag: a True or False flag, that is checked by the script. If false, the html file is not imported. - To Import URL: the url to the HTML google docs that you intend to import.

1. Open up plugins folder
2. Open up the following file in notepad: gsheets_importer/**init**.py
3. Copy and paste your published google sheets CSV file into the empty string, called GOOGLE_SHEETS_URL
4. Save the file.
5. Restart Anki.

## Developer Notes

_If you are an end user of this plugin, you can stop reading here now._

### Dependency Vendoring

All dependencies are vendored to the `/vendor` folder. This is a requirement for Anki addons.

To install a new dependency:

```
pip install -t vendor my_addon_name
```

To upgrade a dependency:

```
pip upgrade -t vendor my_addon_name
```
