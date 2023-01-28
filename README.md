# DirTempl

DirTempl templates a whole directory, letting you swap out individual snippets
for the contents of files in the snippets directory.

## Install

DirTempl is typically best installed by installing [pipx](https://pypa.github.io/pipx/)
and then installing dirtempl using pipx.

```bash
pipx install dirtempl
```

## Example Usage

```bash
dirtempl input/ snippets/ output/
```

Anything in input folder containing {{{{ my_snippet }}}} will replace
the contents with the corresponding file in snippets/ - e.g. my_snippet.

## Why not use jinja2?

Too complicated.
