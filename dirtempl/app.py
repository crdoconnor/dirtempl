from os import walk, makedirs
from pathlib import Path
from copy import copy
import click
import sys
import re


SNIPPET_REGEX = re.compile(r"\{\{\{\{(.*?)\}\}\}\}")


def snippet_replace(filetext, snippet_dir):
    new_text = copy(filetext)
    for found_match in re.finditer(SNIPPET_REGEX, filetext):
        new_text = new_text.replace(
            found_match.group(0),
            snippet_dir.joinpath(found_match.group(1).strip()).read_text(),
        )
    return new_text


@click.command()
@click.argument("src")
@click.argument("dest")
@click.option(
    "--snippets",
    "snippets",
    help="Specify snippets folder",
)
def main(src, dest, snippets):
    src = Path(src)
    dest = Path(dest)
    snippets = Path(snippets)

    if dest.exists():
        click.echo(f"{dest} must be deleted before running dirtempl.", err=True)
        sys.exit(1)
    dest.mkdir()

    filecount = 0

    for dirpath, dirnames, shortfilenames in walk(src):
        for shortfilename in shortfilenames:
            filepath = Path(dirpath).joinpath(shortfilename).relative_to(src)
            srcpath = Path(src).joinpath(filepath)
            destpath = dest.joinpath(filepath)

            if not destpath.parent.exists():
                makedirs(destpath.parent)

            try:
                text = srcpath.read_text()
                contents = snippet_replace(text, snippets).encode("utf8")
            except UnicodeDecodeError:
                contents = srcpath.read_bytes()

            destpath.write_bytes(contents)
            filecount += 1
    print("Templated {} files.".format(filecount))
