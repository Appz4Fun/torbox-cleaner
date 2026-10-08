# API endpoints

All calls go to `https://api.torbox.app/v1/api` with
`Authorization: Bearer $TORBOX_API_KEY`. See the
[official TorBox API docs](https://api-docs.torbox.app/).

## Listing

| Type | Endpoint |
| --- | --- |
| Torrents | `GET /torrents/mylist?bypass_cache=true&offset=N&limit=1000` |
| Usenet | `GET /usenet/mylist?bypass_cache=true&offset=N&limit=1000` |
| Web downloads | `GET /webdl/mylist?bypass_cache=true&offset=N&limit=1000` |

`bypass_cache=true` makes sure the list is current. Without it, the torrent list
can be up to 10 minutes stale. Pages are requested until one returns fewer than
1000 items.

## Deleting

| Type | Endpoint | Body |
| --- | --- | --- |
| Torrents | `POST /torrents/controltorrent` | `{"torrent_id": 123, "operation": "delete"}` |
| Usenet | `POST /usenet/controlusenetdownload` | `{"usenet_id": 123, "operation": "delete"}` |
| Web downloads | `POST /webdl/controlwebdownload` | `{"webdl_id": 123, "operation": "delete"}` |

## Response envelope

Every response follows TorBox's standard shape:

```json
{ "success": true, "error": null, "detail": "Torrent deleted.", "data": null }
```

A response with `success: false` raises an error that shows `error` and `detail`.
