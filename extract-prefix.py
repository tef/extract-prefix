import pygit2
import os

repo_dir = os.getcwd()

print("Opening git repo in", repo_dir)
repo = pygit2.Repository(repo_dir)

branch = repo.head
print("Branch", branch.shorthand)

head = branch.target

print("Head", head)


commits = {}
children = {}

search = [head]
walked = set(search)

while search:
    idx = search.pop(0)

    c = repo.get(idx)
    commits[idx] = c

    for p in c.parent_ids:
        if p not in children:
            children[p] = set()
        children[p].add(idx)

        if p not in walked:
            search.append(p)
            walked.add(p)


print("commits", len(commits))




