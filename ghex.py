"""ghex, a command line Github explorer, that works like find(1)."""
from sys import exit, stderr  # pylint: disable=redefined-builtin
from re import compile as re_compile, Pattern
from subprocess import check_call
from itertools import chain
from functools import partial
from typing import Union, NewType, Optional, Any, Callable
from json import dumps

from click import Choice, command as click_command, argument, option, UsageError
from github import Github
from github.Repository import Repository
from github.NamedUser import NamedUser
from github.Gist import Gist

JSON = NewType("JSON", str)
Regex = NewType("Regex", str)


def try_exec(command: str, value: str):
    """Attempt to execute a command."""
    fmt = command.replace("{}", value)
    check_call(fmt, shell=True)


def maybe_match(pattern: Pattern, attr: str) -> Callable[[Any], bool]:
    """Produce a matching function for a pattern."""

    def try_match(obj: Any) -> bool:
        target = str(getattr(obj, attr))
        return pattern.match(target) is not None

    return try_match


def serialize(obj: Union[Repository, NamedUser, Gist]) -> JSON:
    """Serialize an object into JSON."""
    assert hasattr(obj, "raw_data")
    return dumps(obj.raw_data)


@click_command()
@argument("target", type=str, required=True)
@option("--type", "kind", type=Choice(["r", "repo", "g", "gist"]))
@option("--language", type=Regex)
@option("--name", type=Regex)
@option("--exec", "command", type=str)
@option("--access-token", envvar="GITHUB_ACCESS_TOKEN", type=str)
@option("-0", "--null-terminated", "null_terminated", is_flag=True)
@option("--has-issues", is_flag=True)
def main(  # pylint: disable=too-many-locals,too-many-branches
    *,
    target: Optional[str],
    kind: Optional[str],
    language: Optional[Pattern],
    name: Optional[Pattern],
    command: Optional[str],
    access_token: Optional[str],
    null_terminated: Optional[bool],
    has_issues: Optional[bool],
) -> None:
    """Application entry point."""

    # Parse arguments
    end = "\x00" if null_terminated else "\n"

    if command is not None:
        maybe_exec = partial(try_exec, command)
    else:
        maybe_exec = lambda value: value

    predicates = []

    if has_issues:
        if kind is not None and kind[0] != "r":
            raise UsageError(
                "--has-issues can only be used with repositories as a target type."
            )

        predicates.append((lambda obj: bool(obj.open_issues)))

    for pattern, attr in [(language, "language"), (name, "name")]:
        if pattern is not None:
            predicates.append(maybe_match(re_compile(pattern), attr))

    target = target.strip("/")

    if target.count("/") >= 2:
        print(f"Bad target {target!r}", file=stderr)
        exit(1)

    if "/" not in target:
        target += "/"

    username, reponame = target.split("/")

    # Fetch data
    github = Github(access_token)
    user = github.get_user(username)

    gists = []
    repos = []
    users = []

    if reponame:
        repos.append(user.get_repo(reponame))

    else:
        if kind is None or kind[0] == "g":
            gists.extend(user.get_gists())

        if kind is None or kind[0] == "r":
            repos.extend(user.get_repos())

    stream = chain(gists, repos, users)

    # Output data
    for part in stream:
        if not all(pred(part) for pred in predicates):
            continue

        fmt = maybe_exec(serialize(part))

        print(fmt, end=end)


if __name__ == "__main__":
    main()  # pylint: disable=missing-kwoa
