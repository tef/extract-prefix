import collections
import os

import pygit2

repo_dir = os.getcwd()

print("Opening git repo in", repo_dir)
repo = pygit2.Repository(repo_dir)

branch = repo.head
print("Branch", branch.shorthand)

head = branch.target

print("Head", head)


commits = {}
children = {}
parents = {}

search = collections.deque([head])
walked = set(search)
tails = set()

while search:
    idx = search.popleft()

    c = repo.get(idx)
    commits[idx] = c
    if idx not in children:
        children[idx] = set()

    if not c.parent_ids:
        tails.add(idx)

    for p in c.parent_ids:
        if p not in children:
            children[p] = set()
        children[p].add(idx)

        if p not in walked:
            search.append(p)
            walked.add(p)

    parents[idx] = list(c.parent_ids)


print("commits", len(commits))

search = collections.deque(tails)
counts = {k:len(v) for k,v in parents.items()}

while search:
    idx = search.popleft()
    
    print("commit", idx)

    for c in children[idx]:
        counts[c] -= 1
        if counts[c] == 0:
            search.append(c)

