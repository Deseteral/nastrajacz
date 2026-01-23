#!/usr/bin/env python3

import argparse
import os
import shutil
import tomllib
from typing import Any

HELP_APPLY = "apply configuration stored in the repository"
HELP_FETCH = "fetch actual configuration and store it in the repository"
HELP_SELECT = (
    "comma separated list of fragments to operate on, or all fragments when omited"
)
HELP_LIST = "list fragments present in configuration file"


def main():
    args = parse_args()

    cwd = os.getcwd()
    data = read_fragments_config(cwd)
    if data is None:
        return

    config_fragments = set(data.keys())
    selected_fragments = config_fragments
    if args.select is not None:
        selected_fragments = config_fragments & args.select

    if len(selected_fragments) == 0:
        print("Cannot perform operations without selected fragments.")
        return

    if args.fetch:
        fetch_fragments(data, selected_fragments)
    elif args.apply:
        apply_fragments(data, selected_fragments)
    elif args.list:
        list_fragments(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", help=HELP_APPLY, action="store_true")
    group.add_argument("--fetch", help=HELP_FETCH, action="store_true")
    group.add_argument("--list", help=HELP_LIST, action="store_true")
    group.required = True

    parser.add_argument("--select", help=HELP_SELECT, type=str)

    args = parser.parse_args()

    if args.select is not None:
        args.select = set([s.strip() for s in args.select.split(",")])

    return args


def fetch_fragments(data: dict[str, Any], selected_fragments: set[str]) -> None:
    sorted_fragments = sorted(selected_fragments)
    print(f"Performing fetch for {', '.join(sorted_fragments)} fragments.")

    mkdir("./fragments")

    for fragment in sorted_fragments:
        for target in data[fragment]["targets"]:
            src_path = os.path.expanduser(target["src"])
            src_basename = os.path.basename(src_path)
            fragment_path = os.path.join(".", "fragments", fragment)

            if "dir" in target:
                subdir = os.path.expanduser(target["dir"])
                fragment_path = os.path.join(fragment_path, subdir)

            if os.path.isdir(src_path):
                fragment_path = os.path.join(fragment_path, src_basename)

            mkdir(fragment_path)
            copy(src_path, fragment_path)


def apply_fragments(data: dict[str, Any], selected_fragments: set[str]) -> None:
    sorted_fragments = sorted(selected_fragments)
    print(f"Performing apply for {', '.join(sorted_fragments)} fragments.")

    for fragment in sorted_fragments:
        for target in data[fragment]["targets"]:
            src_path = os.path.expanduser(target["src"])
            src_basename = os.path.basename(src_path)
            fragment_path = os.path.join(".", "fragments", fragment)

            if "dir" in target:
                subdir = os.path.expanduser(target["dir"])
                fragment_path = os.path.join(fragment_path, subdir)

            target_path = os.path.join(fragment_path, src_basename)

            src_parent_dir = os.path.dirname(src_path)
            if src_parent_dir:
                mkdir(src_parent_dir)

            copy(target_path, src_path)


def list_fragments(data: dict[str, Any]) -> None:
    fragments = ", ".join(data.keys())
    print("Fragments defined in configuration file:")
    print(fragments)


def read_fragments_config(working_dir_path: str) -> dict[str, Any] | None:
    fragments_path = os.path.join(working_dir_path, "fragments.toml")

    if not os.path.isfile(fragments_path):
        print("There is no fragments file at this location.")
        return None

    try:
        f = open(fragments_path, mode="rb")
        data = tomllib.load(f)
        f.close()
        return data
    except Exception:
        print("Could not read fragments config file.")
        return None


def mkdir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def copy(src: str, dst: str) -> None:
    print(f'Copying "{src}" to "{dst}"...', end="")
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print("  Done.")
    elif os.path.isfile(src):
        shutil.copy2(src, dst)
        print("  Done.")
    else:
        print("  Skipped...")


if __name__ == "__main__":
    main()
