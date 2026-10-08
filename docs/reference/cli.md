# CLI reference

```text
torbox-cleaner [--delete-all] [--filter-size SIZE] [--filter-name TEXT]
               [--dry-run] [-y] [--type {torrents,usenet,webdl}]
               [--env-file PATH] [--version] [-h]
```

## Selection

At least one is required.

| Flag | Description |
| --- | --- |
| `--delete-all` | Select every item in the account. |
| `--filter-size SIZE` | Items strictly larger than `SIZE`, e.g. `50GB`, `500MB`, `1.5TiB`. |
| `--filter-name TEXT` | Items whose name contains `TEXT` (case-insensitive). Repeatable; any match. |

## Behaviour

| Flag | Description |
| --- | --- |
| `--dry-run` | List what would be deleted. Deletes nothing. |
| `-y`, `--yes` | Skip the interactive confirmation. |
| `--type TYPE` | Only fetch `torrents`, `usenet` or `webdl`. Repeatable. Default: all three. |
| `--env-file PATH` | `.env` file to read `TORBOX_API_KEY` from. Default: `./.env`. |
| `--version` | Print the version and exit. |
| `-h`, `--help` | Show help and exit. |

## Environment

| Variable | Description |
| --- | --- |
| `TORBOX_API_KEY` | Required. Your TorBox API key. Overrides the value in `.env`. |

## Output format

Each selected item is printed as one row:

```text
  <type>  <id>  <size>  <name>
```

Rows are sorted by type, then by size from largest to smallest.
