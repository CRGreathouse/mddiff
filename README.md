# mddiff: Markdown diff

Compare two Markdown files. Similar to git diff --word-diff=color, but comparing
on a section-by-section basis instead of line-by-line, and allowing for sections
that have moved.

----

    usage: mddiff [-h] [file_a] [file_b]
    
    Markdown-aware structural diff with block matching and word-level highlighting.
    
    positional arguments:
      file_a
      file_b
    
    options:
      -h, --help  show this help message and exit
