# extract-prefix

```
$ python3 -m venv env
$ env/bin/pip3 install pygit2
$ env/bin/python3 ./extract-prefix.py PATH NAME
```

Creates a new git branch of NAME with only files found inside PATH.

Skips over commits that have an identical tree to their parent,
or identical to all parents, and they all descend from a single parent.

Should produce same output as `git subtree split --prefix PATH -b NAME`
