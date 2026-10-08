"""API key configuration: where the .env lives, validating keys, and interactive setup."""

from __future__ import annotations

import codecs
import os
import re
import sys
import tempfile
import webbrowser
from collections.abc import Callable
from pathlib import Path

APP_NAME = "torbox-cleaner"
ENV_KEY = "TORBOX_API_KEY"
SETTINGS_URL = "https://torbox.app/settings?section=account"

# RFC 9562 UUID, canonical 8-4-4-4-12 hex form: version 4 nibble, variant 1 (10xx -> 8, 9, a, b).
_UUID4_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", re.IGNORECASE)


def is_valid_api_key(key: str) -> bool:
    """True if ``key`` is a canonical-form version 4, variant 1 UUID, the format of TorBox API keys."""
    return _UUID4_RE.fullmatch(key) is not None


def project_root() -> Path | None:
    """The source checkout this package runs from (``uv run`` in a clone), or None when installed."""
    root = Path(__file__).resolve().parents[2]
    pyproject = root / "pyproject.toml"
    if pyproject.is_file() and f'name = "{APP_NAME}"' in pyproject.read_text():
        return root
    return None


def user_config_env() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / APP_NAME / ".env"


def default_env_file() -> Path:
    """``<clone>/.env`` when run from a clone, otherwise ``~/.config/torbox-cleaner/.env``."""
    root = project_root()
    return root / ".env" if root else user_config_env()


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines from ``path`` into os.environ without overriding existing values."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def write_env_key(path: Path, value: str, key: str = ENV_KEY) -> None:
    """Set ``key=value`` in the .env at ``path``, replacing any existing entry and keeping other lines.

    Creates the file (and its directory) if needed. The file is written atomically with mode 0600.
    """
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lines = path.read_text().splitlines() if path.exists() else []
    entry = re.compile(rf"\s*(export\s+)?{re.escape(key)}\s*=")
    out: list[str] = []
    replaced = False
    for line in lines:
        if entry.match(line):
            if not replaced:
                out.append(f"{key}={value}")
                replaced = True
            continue  # drop duplicate entries
        out.append(line)
    if not replaced:
        out.append(f"{key}={value}")

    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".env.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(out) + "\n")
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def read_masked(getch: Callable[[], str], write: Callable[[str], None]) -> str:
    """Read one line from ``getch``, echoing ``*`` per character. Handles backspace, Ctrl-U, Ctrl-C/D."""
    buf: list[str] = []
    while True:
        ch = getch()
        if ch in ("\r", "\n"):
            write("\r\n")
            return "".join(buf)
        if ch == "\x03":
            write("\r\n")
            raise KeyboardInterrupt
        if ch in ("\x04", ""):
            if not buf:
                write("\r\n")
                raise EOFError
            continue
        if ch in ("\x7f", "\x08"):
            if buf:
                buf.pop()
                write("\b \b")
            continue
        if ch == "\x15":  # Ctrl-U: clear the line
            write("\b \b" * len(buf))
            buf.clear()
            continue
        if ch == "\x1b":  # swallow escape sequences such as arrow keys
            nxt = getch()
            if nxt == "[":
                while not (c := getch()).isalpha() and c != "~" and c:
                    pass
            continue
        if ch.isprintable():
            buf.append(ch)
            write("*")


def masked_input(prompt: str) -> str:
    """Like input(), but echoes ``*`` for each character typed or pasted."""
    if not sys.stdin.isatty():
        sys.stdout.write(prompt)
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            raise EOFError
        return line.rstrip("\r\n")

    def write(s: str) -> None:
        sys.stdout.write(s)
        sys.stdout.flush()

    if os.name == "nt":
        import msvcrt

        write(prompt)
        return read_masked(msvcrt.getwch, write)

    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

    def getch() -> str:
        while True:
            b = os.read(fd, 1)
            if not b:
                return ""
            if ch := decoder.decode(b):
                return ch

    try:
        # Disable echo before showing the prompt so fast pastes are never echoed in clear text.
        tty.setraw(fd, termios.TCSAFLUSH)
        write(prompt)
        return read_masked(getch, write)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def run_setup(
    env_file: Path,
    *,
    open_browser: bool = True,
    prompt: Callable[[str], str] | None = None,
    out=None,
) -> str:
    """Walk the user through copying their API key, validate it, and save it to ``env_file``."""
    prompt = prompt or masked_input
    out = out or sys.stdout
    print("torbox-cleaner setup", file=out)
    print(file=out)
    print("1. Open your TorBox account settings:", file=out)
    print(f"   {SETTINGS_URL}", file=out)
    if open_browser:
        try:
            opened = webbrowser.open(SETTINGS_URL, new=2)
        except Exception:
            opened = False
        print("   (opened in your browser)" if opened else "   (couldn't open a browser; open the link yourself)", file=out)
    print('2. In the "API Key" section, click "Copy API Key".', file=out)
    print("3. Paste the key below. It is masked as you type.", file=out)
    print(file=out)

    while True:
        key = prompt("Paste API key here: ").strip().strip("'\"")
        if is_valid_api_key(key):
            break
        print(
            "That is not a valid TorBox API key. A key looks like "
            "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx. Try again.",
            file=out,
        )

    write_env_key(env_file, key)
    print(f"Saved {ENV_KEY} to {env_file}", file=out)
    return key
