# Debian Index Analyser

Helper tool for extracting statistics com Debian Index file. 

## How to use the tool

For using the tool, a sort help is provided when using the program switch ```-h``` or ```--help```, as follows:

```
❯ python .\debindex.py -h
Usage: debindex.py <options> <architecture>

  Command for extracting the number of entries per package from the Debian
  index file, from the selected repository and architecture.

Options:
  -h, --help                      Show this message and exit.
  -b, --baseurl <url>             Base debian mirror URL  [default: http://ftp
                                  .uk.debian.org/debian/dists/stable/main]

  -d, --download                  Download index file from remote URL
                                  [default: False]

  -l, --log_level <level>         Logging level  [default: info]
  -o, --output <filename>         Optional output file. If not specified, the
                                  output is printed on stdout.

  -n, --number_of_elements <number>
                                  Number of elements to be printed on stdout
```

The minimal required parameter is the **architecture** name string, and the command can be used as follows:

```
❯ python .\debindex.py ppc64el
Debian Index Statistics Tool "debindex.py"
2021-05-02 23:34:43,454 :: I :: debindex.py :: Reading index file from "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-ppc64el.gz" ...
2021-05-02 23:35:20,225 :: I :: debindex.py :: Reading finished.
2021-05-02 23:35:20,228 :: I :: debindex.py :: Counting index entries occurrences" ...
2021-05-02 23:35:20,946 :: I :: debindex.py :: Counting finished.
------------------------------------------------------------------------------
  Top 10 packages with more files associated:
------------------------------------------------------------------------------
fonts/fonts-cns11643-pixmaps    110999
x11/papirus-icon-theme           69475
fonts/texlive-fonts-extra        65577
games/flightgear-data-base       62458
devel/piglit                     49913
doc/trilinos-doc                 49591
x11/obsidian-icon-theme          48829
games/widelands-data             34984
doc/libreoffice-dev-doc          33666
misc/moka-icon-theme             33326
------------------------------------------------------------------------------
Finished.

```
