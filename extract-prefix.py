"""
    given a branch, and a path to a subdirectory, create a new branch
    with only the contents in that subdirectory

    skips over commits that are identical to their parent,
    or identical to all parents, and one parent is the common
    descendent of all.

"""

import collections
import os
import sys

import pygit2


GIT_EMPTY_DIR = pygit2.Oid(hex="4b825dc642cb6eb9a060e54bf8d69288fbee4904")
GIT_DIR_MODE = 0o040_000

def filter_tree(repo, tree, prefix):
    """
        given ["a","b", "c"] walk the tree objects in the repo
        and return the tree that represents a/b/c
    """

    for path in prefix:
        obj = repo.get(tree)
        new_tree = None
        for entry in obj:
            if entry.name == path and entry.filemode == GIT_DIR_MODE:
                new_tree = entry.id

        if new_tree is None:
            return GIT_EMPTY_DIR
        else:
            tree = new_tree

    return tree


def filter_branch(repo, head, prefix):
    commits = {}
    children = {}
    parents = {}
    trees = {}
    tails = set() # initial commits
    # first_parent = {}

    # walk the commits from head to tail

    search = collections.deque([head])
    walked = set(search)
    # first_parent[head] = 0

    while search:
        idx = search.popleft()
        c = repo.get(idx)

        commits[idx] = c
        parents[idx] = list(c.parent_ids)
        trees[idx] = filter_tree(repo, c.tree_id, prefix)

        if idx not in children:
            children[idx] = set()

        # fp = first_parent.get(idx)
        # if fp is not None and c.parent_ids:
        #    first_parent[c.parent_ids[0]] = fp + 1

        for p in c.parent_ids:
            if p not in children:
                children[p] = set()
            children[p].add(idx)

            if p not in walked:
                search.append(p)
                walked.add(p)
        if not c.parent_ids:
            tails.add(idx)


    # print("commits", len(commits))

    # walk the commits from tail to head
    # in topological order, and write new branch

    search = collections.deque(tails)
    counts = { idx: len(p) for idx, p in parents.items()}

    replaces = {}
    skipped = set()
    new_descendents = {}

    while search:
        idx = search.popleft()

        c = commits[idx]
        new_tree = trees[idx]
        new_parents = []

        unchanged_parent = None
        changed_parents = set()

        for old in parents[idx]:
            p = replaces[old]
            if p not in new_parents:
                new_parents.append(p)

            if trees[old] == new_tree:
                if unchanged_parent is None:
                    unchanged_parent = p
                elif p in new_descendents[unchanged_parent]:
                    pass
                elif unchanged_parent in new_descendents[p]:
                    unchanged_parents = p
                else:
                    changed_parents.add(p)
            else:
                changed_parents.add(p)

        if unchanged_parent is not None and changed_parents:
            if all(p in new_descendents[unchanged_parent] for p in changed_parents):
                changed_parents = set()

        if unchanged_parent is not None and not changed_parents:
            new_idx = unchanged_parent
            skipped.add(idx)
        else:

            new_idx = repo.create_commit(
                    None,  # ref name
                    c.author,
                    c.committer,
                    c.message,
                    new_tree,
                    new_parents,
            )

            d = set()
            for p in new_parents:
                d.add(p)
                d.update(new_descendents.get(p, ()))

            new_descendents[new_idx] = d

        replaces[idx] = new_idx

        # print("commit", idx, "->", new_idx)
        # print(d)

        for child in children[idx]:
            counts[child] -= 1
            if counts[child] == 0:
                search.append(child)

    print("skipped", len(skipped))
    return replaces[head]

def main(argv):
    repo_dir = os.getcwd()

    prefix = [p for p in argv[0].split("/") if p]
    new_branch = argv[1]

    print("opening repo", repo_dir)
    repo = pygit2.Repository(repo_dir)

    branch = repo.head
    head = branch.target

    print("splitting out", "/".join(prefix), "of", branch.shorthand)

    new_head = filter_branch(repo, head, prefix)

    print("old head", head)
    print("new head", new_head)

    repo.branches.create(new_branch, repo.get(new_head), force=True)

    print("overwrote branch", new_branch)

    return 0

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: extract-prefix path/path/path new_branch_name")
        sys.exit(-1)

    sys.exit(main(sys.argv[1:]) or 0)
