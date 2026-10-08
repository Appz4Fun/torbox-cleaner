---
layout: home
hero:
  name: torbox-cleaner
  text: Clear out your TorBox cloud
  tagline: List and permanently delete torrents, usenet and web downloads from your account, by size, by name, or all at once.
  actions:
    - theme: brand
      text: Get started
      link: /guide/getting-started
    - theme: alt
      text: CLI reference
      link: /reference/cli
features:
  - title: One-step setup
    details: --setup opens your TorBox settings, then prompts for your API key with masked input and checks that it's valid.
  - title: Dry run first
    details: --dry-run lists exactly what would be deleted, with sizes and totals, and changes nothing.
  - title: Size and name filters
    details: --filter-size 50GB deletes only items above 50 GB. --filter-name framestor matches names case-insensitively.
  - title: No dependencies
    details: Uses only the Python standard library. Run it with uv run from a clone, or install it with uv tool install.
---
