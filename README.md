# HTML Importer

## Goals

The goals of this plugin is to provide a simple interface to importing custom flashcards that are written and organized outside of Anki.

This is because the editing interface for editing large amounts of cards is not intuitive enough, and other external tools are more than capable of editing content better and faster than one could ever dream of in Anki.

A common workflow for this plugin would be to edit content within a markdown file, generate a html file using a static site generator, then pointing this plugin to scrape that the url provided.

### Flashcard Formats Supported

#### 2-Col Table Format

#### Details-Summary Format

## Developer Notes

_If you are an end user of this plugin, you can stop reading here now._

### Dependency Vendoring

All dependencies are vendored to the `/vendor` folder. This is a requirement for Anki addons.

In development, it is recommended to use Pipenv to manage dependencies.

To install a new dependency (with Pipenv):

```bash
# 1. Install to pipenv
pipenv install my_addon_name

# 2. Freeze to vendor folder
pipenv run pip freeze | sed 's/-e //'> requirements.txt && pipenv run pip install -t vendor -r requirements.txt --upgrade
```

To copy to the anki addons folder:

```
rm -rf ~/.local/share/Anki2/addons21/html_importer-testing && cp -a ./. ~/.local/share/Anki2/addons21/html_importer-testing
```

### Testing

To run tests:

```bash
# Single run
pipenv run pytest

# In watch mode
pipenv run pytest --looponfail
```
