# torbox-cleaner

Bulk-delete cloud-stored items from your [TorBox](https://torbox.app/dashboard) account
(torrents, usenet downloads and web downloads) through the
[TorBox API](https://api-docs.torbox.app/).

> [!WARNING]
> Deletion is permanent. TorBox removes the item from the download client and your
> account. Always run with `--dry-run` first.

Full documentation lives in [`docs/`](docs/) and is built with VitePress
(`npm run docs:dev`).

## Requirements

- Python 3.10+ (no third-party runtime dependencies)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A TorBox API key from <https://torbox.app/settings>

## Setup

```bash
git clone <this repo> && cd torboxapp_delete_all_in_clouud
cp .env.example .env        # then put your key in TORBOX_API_KEY
uv sync
```

`.env` is git-ignored. `TORBOX_API_KEY` can also be exported in the environment,
which takes precedence over the file.

## Usage

```bash
uv run torbox-cleaner --help
```

| Option | Description |
| --- | --- |
| `--delete-all` | Select every item in the account. |
| `--filter-size SIZE` | Only items **strictly larger** than `SIZE` (`50GB`, `500MB`, `1.5TiB`). |
| `--filter-name TEXT` | Only items whose name contains `TEXT`, case-insensitive. Repeatable (any match). |
| `--dry-run` | List what would be deleted; delete nothing. |
| `-y`, `--yes` | Skip the interactive `yes` confirmation. |
| `--type {torrents,usenet,webdl}` | Restrict to one item type. Repeatable. Default: all. |
| `--env-file PATH` | Alternate `.env` path (default `./.env`). |

At least one of `--delete-all`, `--filter-size` or `--filter-name` is required.
Filters combine with **AND**. `KB/MB/GB/TB` are decimal (×1000, matching the TorBox
dashboard); `KiB/MiB/GiB/TiB` are binary (×1024).

### Examples

```bash
# Preview deleting everything
uv run torbox-cleaner --delete-all --dry-run

# Delete everything (asks you to type "yes")
uv run torbox-cleaner --delete-all

# Everything above 50 GB
uv run torbox-cleaner --filter-size 50GB --dry-run

# Anything with "framestor" in the name (FraMeSToR, FRAMESTOR, ...)
uv run torbox-cleaner --filter-name framestor --dry-run

# Both: FraMeSToR releases above 50 GB, no prompt
uv run torbox-cleaner --filter-size 50GB --filter-name framestor --yes
```

## How it works

1. `GET /v1/api/{torrents,usenet,webdl}/mylist?bypass_cache=true`, paginated 1000 at a time.
2. Applies the size/name filters locally.
3. For each match, `POST /v1/api/torrents/controltorrent` (or the usenet/webdl equivalent)
   with `{"<type>_id": id, "operation": "delete"}`. Requests are spaced 250 ms apart to
   stay under the 300 req/min limit; 429/5xx responses are retried with backoff.

Exit codes: `0` success, `1` API error / some deletes failed / aborted, `2` usage error
or confirmation required in a non-interactive shell.

## Development

```bash
uv run pytest          # unit tests (no network)
npm install && npm run docs:dev   # docs at http://localhost:5173
```

## License

MIT
