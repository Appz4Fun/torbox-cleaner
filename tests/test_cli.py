import pytest

from torbox_cleaner import cli
from torbox_cleaner.api import KINDS, Item
from torbox_cleaner.filters import format_size, parse_size, select

T = KINDS["torrents"]


def item(id, name, size, kind=T):
    return Item(kind, id, name, size)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("50GB", 50 * 1000**3),
        ("50gb", 50 * 1000**3),
        ("1.5 TiB", int(1.5 * 1024**4)),
        ("500MB", 500 * 1000**2),
        ("1024", 1024),
    ],
)
def test_parse_size(text, expected):
    assert parse_size(text) == expected


@pytest.mark.parametrize("bad", ["", "GB", "50XB", "-5GB", "5 G B"])
def test_parse_size_rejects(bad):
    with pytest.raises(ValueError):
        parse_size(bad)


def test_format_size():
    assert format_size(512) == "512 B"
    assert format_size(59_321_825_797) == "59.32 GB"
    assert format_size(-1) == "?"


def test_select_size_is_strictly_greater():
    items = [item(1, "a", 50 * 1000**3), item(2, "b", 50 * 1000**3 + 1)]
    assert [i.id for i in select(items, min_size=parse_size("50GB"))] == [2]


def test_select_name_case_insensitive():
    items = [item(1, "Movie.REMUX-FraMeSToR", 1), item(2, "other", 1)]
    assert [i.id for i in select(items, names=["framestor"])] == [1]
    assert [i.id for i in select(items, names=["FRAMESTOR"])] == [1]


def test_select_filters_and_together():
    items = [
        item(1, "big FraMeSToR", 60 * 1000**3),
        item(2, "small FraMeSToR", 1),
        item(3, "big other", 60 * 1000**3),
    ]
    assert [i.id for i in select(items, min_size=parse_size("50GB"), names=["framestor"])] == [1]


def test_select_no_filters_returns_all():
    items = [item(1, "a", 1), item(2, "b", 2)]
    assert select(items) == items


class FakeClient:
    def __init__(self, items):
        self.items = items
        self.deleted = []

    def list_items(self, kind):
        return [i for i in self.items if i.kind is kind]

    def delete_item(self, i):
        self.deleted.append(i.id)


@pytest.fixture
def fake(monkeypatch, tmp_path):
    client = FakeClient([item(1, "Big FraMeSToR", 60 * 1000**3), item(2, "small", 10)])
    monkeypatch.setattr(cli, "TorBoxClient", lambda key: client)
    monkeypatch.setattr(cli, "DELETE_INTERVAL", 0)
    monkeypatch.setenv("TORBOX_API_KEY", "3f2c8a1e-9b7d-4c5e-a1f0-6d2b9e8c7a41")
    monkeypatch.setattr(cli, "default_env_file", lambda: tmp_path / ".env")
    monkeypatch.chdir(tmp_path)
    return client


def test_requires_a_selection(fake):
    with pytest.raises(SystemExit) as e:
        cli.main(["--dry-run"])
    assert e.value.code == 2


def test_dry_run_deletes_nothing(fake, capsys):
    assert cli.main(["--delete-all", "--dry-run"]) == 0
    assert fake.deleted == []
    out = capsys.readouterr().out
    assert "Would delete 2 of 2" in out
    assert "Nothing was changed" in out


def test_delete_all_with_yes(fake):
    assert cli.main(["--delete-all", "--yes"]) == 0
    assert sorted(fake.deleted) == [1, 2]


def test_filter_name_delete(fake):
    assert cli.main(["--filter-name", "framestor", "--yes"]) == 0
    assert fake.deleted == [1]


def test_filter_size_delete(fake):
    assert cli.main(["--filter-size", "50GB", "--yes"]) == 0
    assert fake.deleted == [1]


def test_refuses_without_confirmation_when_not_a_tty(fake, monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert cli.main(["--delete-all"]) == 2
    assert fake.deleted == []


def test_load_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("TORBOX_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("# comment\nexport TORBOX_API_KEY='abc'\n")
    cli.load_dotenv(env)
    import os

    assert os.environ["TORBOX_API_KEY"] == "abc"
