# Filtering

Instead of `--delete-all`, you can select a subset of items. Filters are applied
locally after the full list is fetched.

## By size

`--filter-size SIZE` keeps items **strictly larger** than `SIZE`.

```bash
uv run torbox-cleaner --filter-size 50GB --dry-run
```

| Unit | Meaning | Example |
| --- | --- | --- |
| `B` or none | bytes | `1048576` |
| `KB`, `MB`, `GB`, `TB` | decimal, ×1000 (matches the TorBox dashboard) | `50GB` = 50,000,000,000 bytes |
| `KiB`, `MiB`, `GiB`, `TiB` | binary, ×1024 | `50GiB` = 53,687,091,200 bytes |

Units are case-insensitive and decimals are allowed (`1.5TB`).

## By name

`--filter-name TEXT` keeps items whose name contains `TEXT`. Both sides are
lowercased before comparison, so `framestor` matches `FraMeSToR`, `FRAMESTOR`,
and `framestor`.

```bash
uv run torbox-cleaner --filter-name framestor --dry-run
```

Repeat the flag to match any of several strings:

```bash
uv run torbox-cleaner --filter-name framestor --filter-name remux --dry-run
```

## Combining filters

Different filters combine with **AND**:

```bash
# FraMeSToR releases larger than 50 GB
uv run torbox-cleaner --filter-size 50GB --filter-name framestor --dry-run
```

Adding `--delete-all` alongside a filter doesn't widen the selection. The filters
still apply.

## By type

`--type` limits which item types are fetched at all:

```bash
uv run torbox-cleaner --delete-all --type usenet --type webdl --dry-run
```
