#!/usr/bin/env python3

import argparse
import os
import shutil
import tomllib
from dataclasses import dataclass
from typing import Any

HELP_APPLY = "apply configuration stored in the repository"
HELP_FETCH = "fetch actual configuration and store it in the repository"
HELP_SELECT = (
    "comma separated list of fragments to operate on, or all fragments when omited"
)
HELP_LIST = "list fragments present in configuration file"


@dataclass
class Target:
    src: str
    dir: str | None


@dataclass
class Fragment:
    name: str
    targets: list[Target]


@dataclass
class FragmentsConfig:
    fragments: dict[str, Fragment]

    def names(self) -> list[str]:
        return sorted(self.fragments.keys())

    def as_list(self) -> list[Fragment]:
        return list(map(lambda name: self.fragments[name], self.names()))


def main():
    args = parse_args()

    cwd = os.getcwd()
    all_fragments_config = read_fragments_config(cwd)
    if all_fragments_config is None:
        return

    selected_fragment_names = set(all_fragments_config.names())
    if args.select is not None:
        selected_fragment_names = selected_fragment_names & args.select

    if len(selected_fragment_names) == 0:
        print("Cannot perform operations without selected fragments.")
        return

    selected_fragments = {}
    for fragment_name in selected_fragment_names:
        selected_fragments[fragment_name] = all_fragments_config.fragments[
            fragment_name
        ]
    selected_fragments_config = FragmentsConfig(selected_fragments)

    if args.fetch:
        fetch_fragments(selected_fragments_config)
    elif args.apply:
        apply_fragments(selected_fragments_config)
    elif args.list:
        list_fragments(all_fragments_config)


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


def fetch_fragments(fragments: FragmentsConfig) -> None:
    print(f"Performing fetch for {', '.join(fragments.names())} fragments.")

    mkdir("./fragments")

    for fragment in fragments.as_list():
        for target in fragment.targets:
            src_path = os.path.expanduser(target.src)
            src_basename = os.path.basename(src_path)
            fragment_path = os.path.join(".", "fragments", fragment.name)

            if target.dir is not None:
                subdir = os.path.expanduser(target.dir)
                fragment_path = os.path.join(fragment_path, subdir)

            if os.path.isdir(src_path):
                fragment_path = os.path.join(fragment_path, src_basename)

            mkdir(fragment_path)
            copy(src_path, fragment_path)


def apply_fragments(fragments: FragmentsConfig) -> None:
    print(f"Performing apply for {', '.join(fragments.names())} fragments.")

    for fragment in fragments.as_list():
        for target in fragment.targets:
            src_path = os.path.expanduser(target.src)
            src_basename = os.path.basename(src_path)
            fragment_path = os.path.join(".", "fragments", fragment.name)

            if target.dir is not None:
                subdir = os.path.expanduser(target.dir)
                fragment_path = os.path.join(fragment_path, subdir)

            target_path = os.path.join(fragment_path, src_basename)

            src_parent_dir = os.path.dirname(src_path)
            if src_parent_dir:
                mkdir(src_parent_dir)

            copy(target_path, src_path)


def list_fragments(fragments_config: FragmentsConfig) -> None:
    fragments = ", ".join(sorted(fragments_config.names()))
    print("Fragments defined in configuration file:")
    print(fragments)


def read_fragments_config(working_dir_path: str) -> FragmentsConfig | None:
    fragments_path = os.path.join(working_dir_path, "fragments.toml")

    if not os.path.isfile(fragments_path):
        print("There is no fragments file at this location.")
        return None

    try:
        f = open(fragments_path, mode="rb")
        data = tomllib.load(f)

        fragments = {}
        fragment_names = set(data.keys())
        for name in fragment_names:
            targets = []
            for target in data[name]["targets"]:
                dir = None
                if "dir" in target:
                    dir = target["dir"]

                targets.append(Target(src=target["src"], dir=dir))

            fragment = Fragment(name=name, targets=targets)
            fragments[name] = fragment

        f.close()
        return FragmentsConfig(fragments=fragments)
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
