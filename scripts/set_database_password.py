"""Safely update DATABASE_URL in .env after an Aiven password reset.

Usage:
    uv run python scripts/set_database_password.py

Prompts for the new password (hidden input), percent-encodes it, rewrites
DATABASE_URL in .env (keeping user/host/port/dbname), backs up the old file,
and immediately tests the connection. Never prints the password.
"""

import os
import sys
from getpass import getpass
from pathlib import Path
from urllib.parse import quote, urlsplit

from dotenv import load_dotenv


def read_current_url() -> str:
    load_dotenv(".env", override=True)
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        sys.exit("ERROR: DATABASE_URL is not set in .env")
    return url


def mask(url: str) -> str:
    parts = urlsplit(url)
    return (
        f"{parts.scheme}://{parts.username}:***@{parts.hostname}:{parts.port}"
        f"{parts.path}"
    )


def main() -> None:
    env_path = Path(".env")
    current = read_current_url()
    parts = urlsplit(current)

    print(f"Current target: {mask(current)}")
    password = getpass("New database password (input hidden): ").strip()
    if not password:
        sys.exit("ERROR: empty password")

    encoded = quote(password, safe="")
    new_url = (
        f"{parts.scheme}://{parts.username}:{encoded}"
        f"@{parts.hostname}:{parts.port}{parts.path}"
    )

    backup = env_path.with_name(".env.bak.password")
    backup.write_text(env_path.read_text())
    lines = env_path.read_text().splitlines(keepends=True)
    replaced = False
    with env_path.open("w") as fh:
        for line in lines:
            if line.strip().startswith("DATABASE_URL="):
                fh.write(f"DATABASE_URL={new_url}\n")
                replaced = True
            else:
                fh.write(line)
    if not replaced:
        with env_path.open("a") as fh:
            fh.write(f"\nDATABASE_URL={new_url}\n")

    print(f".env updated (backup: {backup}). Testing connection...")

    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(new_url, connect_args={"connect_timeout": 10})
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
        print("SUCCESS:", (version or "")[:60])
        print("Now restart your server: it will boot with a working database.")
    except Exception as exc:  # noqa: BLE001
        print("FAILED:", type(exc).__name__)
        print(str(exc).splitlines()[0][:160])
        sys.exit(1)


if __name__ == "__main__":
    main()
