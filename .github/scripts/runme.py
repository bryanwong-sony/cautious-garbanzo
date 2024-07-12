#!/usr/bin/env python3

import os
import subprocess
import git

__all__ = ["REPOSITORY_PATH", "REPO"]


def _get_repository_path() -> str:
    """
    Retrieve the top-level directory of the Git repository.

    Returns:
        str: Absolute path to the repository's top-level directory.

    Raises:
        RuntimeError: If unable to retrieve the git repository path.
    """
    current_dir = os.getcwd()
    try:
        # Execute the git command and capture the output
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        # Get the top-level directory from the output
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        raise RuntimeError("Unable to retrieve git repository path") from error
    finally:
        os.chdir(current_dir)


REPOSITORY_PATH = _get_repository_path()
REPO = git.Repo(REPOSITORY_PATH)

if __name__ == "__main__":
    base_commit = "HEAD~1" if os.environ["CI"] is "true" else "origin/HEAD"
    from_ref = REPO.commit(base_commit)
    index = from_ref.diff(None)

    print("DELETED:")
    for diff in index.iter_change_type("D"):
        print(diff.b_path)

    print("RENAMED:")
    for diff in index.iter_change_type("R"):
        print(diff.b_path)

    files = {diff.a_path for diff in index.iter_change_type("A")}
    files = files.union({diff.a_path for diff in index.iter_change_type("M")})
    files = files.union({diff.a_path for diff in index.iter_change_type("C")})

    print("EVERYTHING ELSE:")
    for file in files:
        print(file)

