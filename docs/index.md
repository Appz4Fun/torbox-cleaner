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
  - title: Dry run first
    details: --dry-run lists exactly what would be deleted, with sizes and totals, and changes nothing.
  - title: Size and name filters
    details: --filter-size 50GB deletes only items above 50 GB. --filter-name framestor matches names case-insensitively.
  - title: No dependencies
    details: Pure Python standard library. Paginates, respects the 300 req/min rate limit, and retries 429/5xx.
---
