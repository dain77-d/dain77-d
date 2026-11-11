from omok import new_state, play, render

s = new_state()
assert "알 수 없는" in play(s, "omok|move|z99", "a")
assert "알 수 없는" in play(s, "omok|move|a1; rm -rf /", "a")
# 흑 a1..a4, 백 b1..b4 번갈아 둔 뒤 흑 a5 로 세로 오목
for i in range(1, 5):
    play(s, f"omok|move|a{i}", "p1")
    play(s, f"omok|move|b{i}", "p2")
assert "이미" in play(s, "omok|move|a1", "p1")
assert "승리" in play(s, "omok|move|a5", "p1") and s["winner"] == 1
assert "이미 끝" in play(s, "omok|move|c1", "p2")
assert "새 게임" in play(s, "OMOK|new", "p2") and not s["moves"]
assert "omok%7Cmove%7Ca1" in render(s)
print("ok")
