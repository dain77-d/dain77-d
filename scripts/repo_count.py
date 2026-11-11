"""내 소유 레포를 public/private 로 세어 README 뱃지를 갱신한다.

env REPO_COUNT_TOKEN: fine-grained 토큰 (All repositories, Metadata: Read-only).
레포 이름은 어디에도 쓰지 않고 개수만 남긴다.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- REPOS:START -->", "<!-- REPOS:END -->"


def fetch_counts(token):
    pub = priv = 0
    page = 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/user/repos?affiliation=owner&per_page=100&page={page}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        )
        repos = json.load(urllib.request.urlopen(req))
        if not repos:
            return pub, priv
        for r in repos:
            if r["private"]:
                priv += 1
            else:
                pub += 1
        page += 1


def badge(label, n, color):
    return f'<img src="https://img.shields.io/badge/{label}-{n}-{color}?style=for-the-badge" />'


def main():
    token = os.environ.get("REPO_COUNT_TOKEN")
    if not token:
        sys.exit("REPO_COUNT_TOKEN 시크릿이 없어서 건너뜀")
    pub, priv = fetch_counts(token)
    block = f"{START}\n  {badge('Public_Repos', pub, '4facfe')} {badge('Private_Repos', priv, '7f5af0')}\n  {END}"
    text = README.read_text(encoding="utf-8")
    README.write_text(re.sub(re.escape(START) + ".*?" + re.escape(END), block, text, flags=re.S), encoding="utf-8")
    print(f"public={pub} private={priv}")


if __name__ == "__main__":
    main()
