# srtcheck #

Check the syntax of .srt files (subtitles).

## Usage ##

    $ ./srtcheck.py tests/test1.shouldpass.withwarning.online.14.srt 
    File tests/test1.shouldpass.withwarning.online.14.srt: Warning, on line 734, I've found subtitle number 14
    while I was exepecting subtitle number 164.

    $ ./srtcheck.py tests/test2.shouldfail.online.406.srt 
    File tests/test2.shouldfail.online.406.srt: Error, on line 406, invalid syntax: regular expression (.*) --> (.*) did not match.

    $ ./srtcheck.py tests/test3.shouldfail.online.92.srt 
    File tests/test3.shouldfail.online.92.srt: Error, on line 92, unexpected input : is a subtitle number missing (I was expecting #21) ?
