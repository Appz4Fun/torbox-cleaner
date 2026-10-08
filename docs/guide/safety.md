# Safety

::: danger Deletion is permanent
TorBox's `delete` operation removes the item from the download client **and**
your account. There is no trash or undo.
:::

torbox-cleaner has the following safeguards:

1. **No default action.** Running with no selection flag is an error. You must
   pass `--delete-all`, `--filter-size`, or `--filter-name`.
2. **Dry run.** `--dry-run` fetches and prints the selection, then exits
   without sending any delete requests.
3. **Typed confirmation.** Without `--yes`, you must type `yes` at the prompt.
   Anything else aborts.
4. **No silent non-interactive deletes.** If stdin isn't a terminal (cron, CI,
   pipes) and `--yes` is missing, the tool exits with code `2` and deletes nothing.
5. **Per-item deletes.** Items are deleted one at a time by ID, not with the
   API's `all: true` shortcut, so only the items you saw listed are touched.

## Rate limits

TorBox allows 300 requests per minute per API token. Deletes are spaced 250 ms
apart (about 240 per minute). HTTP 429 and 5xx responses are retried up to five
times with exponential backoff, honouring `Retry-After`.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, or nothing matched |
| `1` | API error, one or more deletes failed, or you aborted at the prompt |
| `2` | Usage error, or confirmation required in a non-interactive shell |
| `130` | You canceled setup |

## Protecting your API key

- `--setup` masks the key with asterisks as you type or paste it. Terminal echo
  is turned off before the prompt appears, so even an instant paste is never
  shown in plain text.
- The `.env` file is written atomically with permissions `0600`, so only your
  user can read it. The `~/.config/torbox-cleaner` folder is created with
  permissions `0700`.
- `.env` files are listed in `.gitignore`.
