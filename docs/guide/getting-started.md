# Getting started

## Before you begin

You need:

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) (or pip)
- A TorBox API key from [torbox.app/settings](https://torbox.app/settings)

## Install

```bash
git clone <this repo>
cd torboxapp_delete_all_in_clouud
uv sync
```

## Configure your API key

Copy the example file and add your key:

```bash
cp .env.example .env
```

```ini
TORBOX_API_KEY=your-key-here
```

::: tip
`.env` is listed in `.gitignore`, so the key never gets committed. A
`TORBOX_API_KEY` exported in your shell takes precedence over the file.
:::

## Preview, then delete

Always start with a dry run:

```bash
uv run torbox-cleaner --delete-all --dry-run
```

```text
Fetched 555 torrents item(s)
Fetched 0 usenet item(s)
Fetched 0 webdl item(s)
Selection: everything

Would delete 555 of 555 item(s), 21.43 TB:
  torrent  85472971     1.09 TB  Game of Thrones (2011) [2160p] ...
  ...

Dry run: 555 item(s), 21.43 TB would be deleted. Nothing was changed.
```

When the list looks right, drop `--dry-run`:

```bash
uv run torbox-cleaner --delete-all
```

You are asked to type `yes` before anything is deleted. See [Safety](./safety).

## Next steps

- [Filter by size or name](./filtering)
- [Full CLI reference](../reference/cli)
