# Getting started

This page shows you how to save your TorBox API key, preview a deletion, and
then delete items from your TorBox cloud.

## Before you begin

You need the following:

- A TorBox account
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.10 or later. If you don't have it, uv installs it for you.

## Get the code

```bash
git clone https://github.com/xbmc4lyfe/torbox-cleaner.git
cd torbox-cleaner
```

## Save your API key

1. Run the setup command:

   ```bash
   uv run torbox-cleaner --setup
   ```

   The setup command opens
   [your TorBox account settings](https://torbox.app/settings?section=account)
   in your browser. If it can't open a browser, it prints the link instead.
   To print the link without trying to open a browser, add `--no-browser`.

2. In the **API Key** section, click **Copy API Key**.

   ![TorBox account settings. A red box and arrow highlight the Copy API Key button.](/images/torbox-api-key.png)

3. At the `Paste API key here:` prompt, paste your key and press **Enter**.

   ```text
   Paste API key here: ************************************
   Saved TORBOX_API_KEY to /path/to/torbox-cleaner/.env
   ```

The key appears as asterisks while you type. torbox-cleaner saves it in the
`.env` file at the root of the repository and sets the file's permissions to
`0600`. If the file already contains a `TORBOX_API_KEY`, the new key replaces
it, and the other lines in the file stay the same.

::: info Key validation
A TorBox API key is a version 4 UUID in standard canonical form: 32
hexadecimal digits, grouped `8-4-4-4-12`. The version digit is `4`, and the
variant digit is `8`, `9`, `a`, or `b`. If what you paste doesn't match this
format, torbox-cleaner prints `That is not a valid TorBox API key` and asks
you again.
:::

## Preview, then delete

1. Preview what would be deleted:

   ```bash
   uv run torbox-cleaner --dry-run --delete-all
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

2. When the list looks right, delete the items:

   ```bash
   uv run torbox-cleaner --delete-all
   ```

3. At the confirmation prompt, type `yes`. For more about the safeguards, see
   [Safety](./safety).

## Install the command

To run `torbox-cleaner` from any directory, without `uv run`, install it as a
uv tool.

1. From the root of the repository, run the following command:

   ```bash
   uv tool install .
   ```

   uv puts the `torbox-cleaner` command in `~/.local/bin`. If your shell can't
   find the command, run `uv tool update-shell` and open a new terminal.

2. Save your API key for the installed command:

   ```bash
   torbox-cleaner --setup
   ```

   The installed command saves the key in `~/.config/torbox-cleaner/.env`. If
   `XDG_CONFIG_HOME` is set, it uses `$XDG_CONFIG_HOME/torbox-cleaner/.env`
   instead. If you skip this step, torbox-cleaner starts setup automatically
   the first time you run it.

3. Run torbox-cleaner from any directory:

   ```bash
   torbox-cleaner --delete-all
   ```

::: tip Updating
The installed command is a copy of the code. After you pull changes, run
`uv tool install . --reinstall` to update it.
:::

## Next steps

- [Filter by size or name](./filtering)
- [Read the full CLI reference](../reference/cli)
