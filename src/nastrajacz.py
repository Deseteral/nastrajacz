#!/usr/bin/env python3

import os
import shutil
import tomllib
import argparse
from typing import Any

HELP_APPLY = 'apply configuration stored in the repository'
HELP_FETCH = 'fetch actual configuration and store it in the repository'
HELP_SELECT = 'comma separated list of fragments to operate on, or all fragments when omited'
HELP_LIST = 'list fragments present in configuration file'


def main():
    args = parse_args()

    cwd = os.getcwd()
    data = read_fragments_config(cwd)
    if data is None:
        return

    config_fragments = set(data.keys())
    fragments = config_fragments
    if args.select is not None:
        fragments = config_fragments & args.select

    if len(fragments) == 0:
        print('Cannot perform operations without selected fragments.')
        return

    if args.fetch:
        fetch_fragments(data, fragments)
    elif args.apply:
        apply_fragments(data, fragments)
    elif args.list:
        list_fragments(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', help=HELP_APPLY, action='store_true')
    group.add_argument('--fetch', help=HELP_FETCH, action='store_true')
    group.add_argument('--list', help=HELP_LIST, action='store_true')
    group.required = True

    parser.add_argument('--select', help=HELP_SELECT, type=str)

    args = parser.parse_args()

    if args.select is not None:
        args.select = set([s.strip() for s in args.select.split(',')])

    return args


def fetch_fragments(data: dict[str, Any], fragments: set[str]) -> None:
    print(f'Performing fetch for {', '.join(fragments)} fragments.')

    mkdir('./fragments')

    for fragment in fragments:
        for target in data[fragment]['targets']:
            src = os.path.expanduser(target['src'])
            basename = os.path.basename(src)
            target_dir = os.path.join('.', 'fragments', fragment)

            if 'dir' in target:
                subdir = os.path.expanduser(target['dir'])
                target_dir = os.path.join(target_dir, subdir)

            if os.path.isdir(src):
                target_dir = os.path.join(target_dir, basename)

            mkdir(target_dir)
            copy(src, target_dir)


def apply_fragments(data: dict[str, Any], fragments: set[str]) -> None:
    print(f'Performing apply for {', '.join(fragments)} fragments.')

    for fragment in fragments:
        for target in data[fragment]['targets']:
            src = os.path.expanduser(target['src'])
            target_dir = os.path.join('.', 'fragments', fragment)

            if 'dir' in target:
                subdir = os.path.expanduser(target['dir'])
                target_dir = os.path.join(target_dir, subdir)

            basename = os.path.basename(src)
            target_dir = os.path.join(target_dir, basename)

            copy(target_dir, src)


def list_fragments(data: dict[str, Any]) -> None:
    fragments = ', '.join(data.keys())
    print('Fragments defined in configuration file:')
    print(fragments)


def read_fragments_config(working_dir_path: str) -> dict[str, Any] | None:
    fragments_path = os.path.join(working_dir_path, 'fragments.toml')

    if not os.path.isfile(fragments_path):
        print('There is no fragments file at this location.')
        return None

    try:
        f = open(fragments_path, mode='rb')
        data = tomllib.load(f)
        f.close()
        return data
    except Exception:
        print('Could not read fragments config file.')
        return None


def mkdir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def copy(src: str, dst: str) -> None:
    print(f'Copying "{src}" to "{dst}"...', end='')
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print('  Done.')
    elif os.path.isfile(src):
        shutil.copy2(src, dst)
        print('  Done.')
    else:
        print('  Skipped...')


if __name__ == '__main__':
    main()
