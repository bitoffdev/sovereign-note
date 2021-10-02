import os

def get_child_paths(root: str):
    """
    Return the paths of all files contained by root relative to the root
    directory path
    """
    paths = []
    for parent, _, filenames in os.walk(root):
        relative_parent = os.path.relpath(parent, root)
        for filename in filenames:
            paths.append(os.path.join(relative_parent, filename))
    return paths

