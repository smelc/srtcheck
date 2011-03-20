# srtcheck #

Check the syntax of .srt files (subtitles).

Useful, for example, to catch decoding errors when
transforming a utf-8 file to iso-8859-15 with
gnome-subtitles (to put subtitles on the freebox HD).

## Remarks ##

- Tested only on a system with utf-8 as the default encoding.
- script ./run-tests is for development purposes. Yet, you can try it
  to verify that srtcheck behaves as planned on your setup.

## Options ##

- "--verbose" : display checked lines.

- "--try-encoding blah" : srtcheck will try encoding blah if decoding fails with
  your system's default. This option is incompatible with option --only-encoding.

- "--only-encoding blah" : srtcheck will use exclusively encoding blah. By default,
  your system's default encoding is used. This option is incompatible is incompatible
  with option --try-encoding.

## Usage ##

    $ ./srtcheck.py tests/test1.shouldpass.withwarning.online.734.srt 
    Warning, on line 734,
    I've found subtitle number 14 while I was exepecting subtitle number 164.

    $ ./srtcheck.py tests/test2.shouldfail.online.406.srt 
    Error, on line 406, invalid syntax:
    regular expression (.*) --> (.*) did not match.

    $ ./srtcheck.py --try-encoding latin1 tests/test7.shouldpass.srt 
    Catched decoding error when reading the file supposing it was
    encoded in utf-8.
    Retrying with encoding latin1.
