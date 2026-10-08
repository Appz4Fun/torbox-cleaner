# CLI reference

```text
torbox-cleaner [--setup] [--no-browser]
               [--delete-all] [--filter-size SIZE] [--filter-name TEXT]
               [--dry-run] [-y] [--type {torrents,usenet,webdl}]
               [--env-file PATH] [--version] [-h]
```

## Setup

| Flag | Description |
| --- | --- |
| `--setup` | Open your TorBox account settings, prompt for your API key with masked input, check that it's valid, and save it. |
| `--no-browser` | With `--setup`, print the settings link instead of opening a browser. |

If you use `--setup` without a selection flag, torbox-cleaner exits after it
saves your key. If you also use a selection flag, it saves your key and then
continues, for example with `--setup --delete-all --dry-run`.

If no key is configured when you run a command, and stdin is a terminal,
torbox-cleaner starts setup automatically. If stdin isn't a terminal,
torbox-cleaner exits with code `2` and asks you to run `--setup`.

## Selection

Unless you use `--setup`, you must use at least one of these flags.

| Flag | Description |
| --- | --- |
| `--delete-all` | Select every item in your account. |
| `--filter-size SIZE` | Select only items larger than `SIZE`, such as `50GB`, `500MB`, or `1.5TiB`. |
| `--filter-name TEXT` | Select only items whose name contains `TEXT`. Matching ignores case. You can repeat this flag; an item matches if it contains any of the values. |

## Behavior

| Flag | Description |
| --- | --- |
| `--dry-run` | List what would be deleted, without deleting anything. |
| `-y`, `--yes` | Skip the interactive confirmation. |
| `--type TYPE` | Fetch only `torrents`, `usenet`, or `webdl` items. You can repeat this flag. The default is all three types. |
| `--env-file PATH` | Read the key from `PATH`, and with `--setup`, write it there. |
| `--version` | Print the version and exit. |
| `-h`, `--help` | Show help and exit. |

## API key lookup

torbox-cleaner checks these places in order and uses the first key it finds:

1. The `TORBOX_API_KEY` environment variable
2. The file passed with `--env-file`
3. `<repository>/.env`, when you run it with `uv run` from a clone
4. `$XDG_CONFIG_HOME/torbox-cleaner/.env`, or
   `~/.config/torbox-cleaner/.env` if `XDG_CONFIG_HOME` isn't set, when you
   run the command installed with `uv tool install`

If the key isn't a valid TorBox API key (a canonical version 4 UUID),
torbox-cleaner exits with an error and asks you to run `--setup`.

## Output format

torbox-cleaner prints one row for each selected item:

```text
  <type>  <id>  <size>  <name>
```

Rows are sorted by type, and then by size from largest to smallest. If TorBox
hasn't finished reading an item's metadata, its size appears as `?`.
