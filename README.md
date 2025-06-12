# extract-prefix

```
$ python3 -m venv env
$ env/bin/pip3 install pygit2
$ env/bin/python3 ./extract-prefix.py PATH NAME
```

Creates a new git branch of NAME with only files found inside PATH.

Does not skip over commits if they are empty / have no files in PATH.
