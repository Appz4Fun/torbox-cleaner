"""Command-line interface for torbox-cleaner."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from torbox_cleaner import __version__
from torbox_cleaner.api import KINDS, Item, TorBoxClient, TorBoxError
from torbox_cleaner.config import (
    ENV_KEY,
    default_env_file,
    is_valid_api_key,
    load_dotenv,
    run_setup,
)
from torbox_cleaner.filters import format_size, parse_size, select

# TorBox allows 300 requests/min per token; stay comfortably under it.
DELETE_INTERVAL = 0.25

EPILOG = """\
examples:
  torbox-cleaner --setup                          save your API key (opens TorBox settings)
  torbox-cleaner --delete-all --dry-run           list everything that would be deleted
  torbox-cleaner --delete-all                     delete every item in the account
  torbox-cleaner --filter-size 50GB --dry-run     list items larger than 50 GB
  torbox-cleaner --filter-name framestor          delete items with "framestor" in the name
  torbox-cleaner --filter-size 50GB --filter-name framestor --yes

Filters combine with AND. Name matching is case-insensitive.
The API key is read from TORBOX_API_KEY in the environment, or from the
.env file: <clone>/.env when run with `uv run` from a clone, otherwise
~/.config/torbox-cleaner/.env. Run --setup to create or update it.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="torbox-cleaner",
        description="Delete cloud-stored items (torrents, usenet, web downloads) from your TorBox account.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--setup",
        action="store_true",
        help="open TorBox settings in your browser, then prompt for and save your API key",
    )
    p.add_argument("--no-browser", action="store_true", help="with --setup: print the settings link, don't open it")

    sel = p.add_argument_group("selection (one is required unless --setup)")
    sel.add_argument("--delete-all", action="store_true", help="select every item in the account")
    sel.add_argument(
        "--filter-size",
        metavar="SIZE",
        type=_size_arg,
        help="only items strictly larger than SIZE (e.g. 50GB, 500MB, 1.5TiB)",
    )
    sel.add_argument(
        "--filter-name",
        metavar="TEXT",
        action="append",
        help="only items whose name contains TEXT, case-insensitive (repeatable; any match)",
    )

    p.add_argument("--dry-run", action="store_true", help="list what would be deleted, delete nothing")
    p.add_argument("-y", "--yes", action="store_true", help="skip the interactive confirmation prompt")
    p.add_argument(
        "--type",
        dest="types",
        action="append",
        choices=sorted(KINDS),
        help="limit to an item type (repeatable; default: all types)",
    )
    p.add_argument(
        "--env-file",
        metavar="PATH",
        type=Path,
        help="the .env file to read and --setup to write "
        "(default: <clone>/.env from a clone, else ~/.config/torbox-cleaner/.env)",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def _size_arg(text: str) -> int:
    try:
        return parse_size(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e)) from None


def print_table(items: list[Item], out=sys.stdout) -> None:
    if not items:
        return
    id_w = max(len(str(i.id)) for i in items)
    for i in items:
        print(f"  {i.kind.label:<7}  {i.id:>{id_w}}  {format_size(i.size):>10}  {i.name}", file=out)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    has_selection = args.delete_all or args.filter_size is not None or args.filter_name
    if not (args.setup or has_selection):
        parser.error("choose what to delete: --delete-all, --filter-size and/or --filter-name (or run --setup)")

    env_file = args.env_file or default_env_file()

    if args.setup:
        try:
            api_key = run_setup(env_file, open_browser=not args.no_browser)
        except (KeyboardInterrupt, EOFError):
            print("Setup cancelled. Nothing was saved.", file=sys.stderr)
            return 130
        shell_key = os.environ.get(ENV_KEY)
        if shell_key and shell_key != api_key:
            print(f"Note: {ENV_KEY} is also set in your shell environment and takes precedence over {env_file}.")
        os.environ[ENV_KEY] = api_key
        if not has_selection:
            print()
            print("Next, preview what would be deleted:  torbox-cleaner --delete-all --dry-run")
            return 0
        print()

    load_dotenv(env_file)
    api_key = os.environ.get(ENV_KEY, "").strip()
    if not api_key:
        if not sys.stdin.isatty():
            parser.error(f"{ENV_KEY} is not set and {env_file} has no key; run: torbox-cleaner --setup")
        print(f"No TorBox API key found in {env_file}. Starting setup.\n")
        try:
            api_key = run_setup(env_file, open_browser=not args.no_browser)
        except (KeyboardInterrupt, EOFError):
            print("Setup cancelled. Nothing was saved.", file=sys.stderr)
            return 130
        print()
    if not is_valid_api_key(api_key):
        parser.error(f"{ENV_KEY} is not a valid TorBox API key; run: torbox-cleaner --setup")

    client = TorBoxClient(api_key)
    kinds = [KINDS[k] for k in (args.types or KINDS)]

    try:
        items: list[Item] = []
        for kind in kinds:
            found = client.list_items(kind)
            print(f"Fetched {len(found)} {kind.key} item(s)")
            items.extend(found)
    except TorBoxError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    targets = select(items, min_size=args.filter_size, names=args.filter_name)
    targets.sort(key=lambda i: (i.kind.key, -i.size))
    total = sum(i.size for i in targets)

    criteria = []
    if args.filter_size is not None:
        criteria.append(f"size > {format_size(args.filter_size)}")
    if args.filter_name:
        criteria.append("name contains " + " or ".join(repr(n) for n in args.filter_name))
    print(f"Selection: {' AND '.join(criteria) if criteria else 'everything'}")
    print()

    if not targets:
        print("Nothing matches. Nothing to delete.")
        return 0

    header = "Would delete" if args.dry_run else "Will delete"
    print(f"{header} {len(targets)} of {len(items)} item(s), {format_size(total)}:")
    print_table(targets)
    print()

    if args.dry_run:
        print(f"Dry run: {len(targets)} item(s), {format_size(total)} would be deleted. Nothing was changed.")
        return 0

    if not args.yes:
        if not sys.stdin.isatty():
            print("error: refusing to delete without confirmation; pass --yes in non-interactive use", file=sys.stderr)
            return 2
        answer = input(f"Permanently delete these {len(targets)} item(s)? Type 'yes' to continue: ")
        if answer.strip().lower() != "yes":
            print("Aborted. Nothing was deleted.")
            return 1

    failures = 0
    for n, item in enumerate(targets, 1):
        try:
            client.delete_item(item)
            print(f"[{n}/{len(targets)}] deleted {item.kind.label} {item.id}: {item.name}")
        except TorBoxError as e:
            failures += 1
            print(f"[{n}/{len(targets)}] FAILED {item.kind.label} {item.id}: {e}", file=sys.stderr)
        if n < len(targets):
            time.sleep(DELETE_INTERVAL)

    print()
    print(f"Done: {len(targets) - failures} deleted, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
