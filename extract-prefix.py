import collections
import os
import sys

import pygit2


def filter_tree(repo, tree):
    return tree


def filter_branch(repo, head):
    commits = {}
    children = {}
    parent_count = {}

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

        parent_count[idx] = len(c.parent_ids)


    print("commits", len(commits))

    search = collections.deque(tails)
    counts = dict(parent_count)

    replaces = {}

    while search:
        idx = search.popleft()
        
        print("commit", idx)

        c = commits[idx]

        new_parents = [replaces[p] for p in c.parent_ids]
        new_tree = filter_tree(repo, c.tree_id)

        new_idx = repo.create_commit(
                None, 
                c.author, 
                c.committer, 
                c.message,
                new_tree,
                new_parents,
        )

        replaces[idx] = new_idx

        for child in children[idx]:
            counts[child] -= 1
            if counts[child] == 0:
                search.append(child)

    return replaces[head]


def main():
    repo_dir = os.getcwd()

    print("Opening git repo in", repo_dir)
    repo = pygit2.Repository(repo_dir)

    branch = repo.head
    print("Branch", branch.shorthand)

    head = branch.target

    print("Head", head)

    new_head = filter_branch(repo, head)

    print("new head", new_head)

    return 0

if __name__ == '__main__':
    sys.exit(main() or 0)
