"""README 오목. 이슈 제목 `omok|move|h8` 또는 `omok|new` 를 받아 판을 갱신한다.

env: TITLE(이슈 제목), ACTOR(이슈 작성자). 결과 메시지는 msg.txt 에 쓴다.
이슈 제목은 아무나 넣을 수 있는 값이라 정규식으로만 해석한다.
"""
import json
import os
import re
from pathlib import Path

N = 15
COLS = "abcdefghijklmno"
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "games" / "omok.json"
README = ROOT / "README.md"
REPO = "dain77-d/dain77-d"
STONE = {0: "🟫", 1: "⚫", 2: "⚪"}
START, END = "<!-- OMOK:START -->", "<!-- OMOK:END -->"


def new_state():
    return {"board": [[0] * N for _ in range(N)], "turn": 1, "winner": 0, "moves": []}


def five(board, r, c):
    p = board[r][c]
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        n = 1
        for s in (1, -1):
            rr, cc = r + dr * s, c + dc * s
            while 0 <= rr < N and 0 <= cc < N and board[rr][cc] == p:
                n += 1
                rr, cc = rr + dr * s, cc + dc * s
        if n >= 5:
            return True
    return False


def play(state, title, actor):
    """state를 바꾸고 이슈에 남길 메시지를 돌려준다."""
    if title.strip().lower() == "omok|new":
        if not state["winner"] and state["moves"]:
            return "아직 게임이 진행 중이에요. 끝난 뒤에 새 게임을 시작할 수 있어요."
        state.clear()
        state.update(new_state())
        return "새 게임을 시작했어요! ⚫ 차례입니다."
    m = re.fullmatch(r"omok\|move\|([a-o])(1[0-5]|[1-9])", title.strip().lower())
    if not m:
        return "알 수 없는 명령이에요."
    if state["winner"]:
        return "게임이 이미 끝났어요. README의 '새 게임' 링크를 눌러주세요."
    c, r = COLS.index(m[1]), int(m[2]) - 1
    if state["board"][r][c]:
        return f"{m[1].upper()}{r + 1} 자리는 이미 돌이 있어요."
    p = state["turn"]
    state["board"][r][c] = p
    state["moves"].append({"who": actor, "at": f"{m[1].upper()}{r + 1}", "stone": p})
    if five(state["board"], r, c):
        state["winner"] = p
        return f"{STONE[p]} {m[1].upper()}{r + 1} — 오목 완성! {STONE[p]} 승리 🎉"
    if len(state["moves"]) == N * N:
        state["winner"] = -1
        return "판이 가득 찼어요. 무승부!"
    state["turn"] = 3 - p
    return f"{STONE[p]} {m[1].upper()}{r + 1} 에 두었어요. 다음은 {STONE[3 - p]} 차례!"


def link(title, text):
    return f"[{text}](https://github.com/{REPO}/issues/new?title={title.replace('|', '%7C')}&body=%EC%A0%9C%EC%B6%9C+%EB%B2%84%ED%8A%BC%EB%A7%8C+%EB%88%84%EB%A5%B4%EB%A9%B4+%EB%90%A9%EB%8B%88%EB%8B%A4)"


def render(state):
    b = state["board"]
    if state["winner"] == -1:
        status = "무승부! " + link("omok|new", "🔄 새 게임")
    elif state["winner"]:
        status = f"{STONE[state['winner']]} 승리! " + link("omok|new", "🔄 새 게임")
    else:
        status = f"**{STONE[state['turn']]} 차례** — 빈 칸을 눌러 이슈를 제출하면 돌이 놓여요."
    rows = ["| |" + "|".join(x.upper() for x in COLS) + "|", "|-" * (N + 1) + "|"]
    for r in range(N):
        cells = []
        for c in range(N):
            if b[r][c] or state["winner"]:
                cells.append(STONE[b[r][c]])
            else:
                cells.append(link(f"omok|move|{COLS[c]}{r + 1}", STONE[0]))
        rows.append(f"|**{r + 1}**|" + "|".join(cells) + "|")
    recent = "\n".join(
        f"- {STONE[m['stone']]} `{m['at']}` by @{m['who']}" for m in reversed(state["moves"][-5:])
    ) or "- 아직 아무도 두지 않았어요. 첫 수를 둬보세요!"
    return f"{START}\n{status}\n\n<div align=\"center\">\n\n" + "\n".join(rows) + f"\n\n</div>\n\n**최근 수**\n\n{recent}\n{END}"


def main():
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else new_state()
    msg = play(state, os.environ.get("TITLE", ""), os.environ.get("ACTOR", "someone"))
    STATE.write_text(json.dumps(state), encoding="utf-8")
    text = README.read_text(encoding="utf-8")
    i, j = text.index(START), text.index(END) + len(END)
    README.write_text(text[:i] + render(state) + text[j:], encoding="utf-8")
    (ROOT / "msg.txt").write_text(msg, encoding="utf-8")


if __name__ == "__main__":
    main()
