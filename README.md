# mddiff: Markdown diff

Compare two Markdown files. Similar to git diff --word-diff=color, but comparing
on a section-by-section basis instead of line-by-line, and allowing for sections
that have moved.

----

  usage: mddiff [-h] [-i] [-s] [-c] [-C CONTEXT] [--match-threshold MATCH_THRESHOLD] [--shortstat] [file_a] [file_b]
  
  positional arguments:
    file_a
    file_b
  
  options:
    -h, --help            show this help message and exit
    -i, --ignore-case
    -s, --report-identical-files
    -c                    show context (default 3)
    -C CONTEXT, --context CONTEXT
                          context blocks
    --match-threshold MATCH_THRESHOLD
                          minimum word overlap percentage (default 35)
    --shortstat           show only summary statistics
