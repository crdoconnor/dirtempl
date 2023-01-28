Quickstart:
  docs: quickstart
  about: |
    Template a folder.
  given:
    image file: src/subdir/example.png
    files:
      src/a.txt: a
      src/subdir/b.txt: |
        Title

        {{{{ snippet1 }}}}

        {{{{ snippet2 }}}}

      snippets/snippet1: snippet contents 1
      snippets/snippet2: snippet contents 1

  steps:
  - dirtempl:
      cmd: --snippets snippets/ src/ dest/
      output: |
        Templated 3 files.

  - file contains:
      filename: dest/a.txt
      contents: a

  - file contains:
      filename: dest/subdir/b.txt
      contents: |
        Title

        snippet contents 1

        snippet contents 1


  - image present: dest/subdir/example.png
