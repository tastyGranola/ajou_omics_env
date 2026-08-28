"""회의실 예약 MCP 서버 — 실습 ① 정답본"""
try:
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("meeting")

ROOMS = {"세미나실": 20, "대회의실": 12, "소회의실": 4}
BOOKED: list[dict] = []


@mcp.tool()
def find_rooms(date: str, start: str, end: str, people: int = 1) -> dict:
    """비어 있는 회의실을 찾습니다.

    Args:
        date: 날짜 (예 "2026-09-01")
        start: 시작 시각 (예 "14:00")
        end: 끝 시각 (예 "16:00")
        people: 참석 인원
    """
    busy = {b["room"] for b in BOOKED
            if b["date"] == date and not (b["end"] <= start or b["start"] >= end)}
    free = [r for r, cap in ROOMS.items() if r not in busy and cap >= people]
    return {"날짜": date, "시간": f"{start}~{end}", "빈방": free}


@mcp.tool()
def book_room(room: str, date: str, start: str, end: str, who: str) -> dict:
    """회의실을 예약합니다.

    Args:
        room: 방 이름
        date: 날짜
        start: 시작 시각
        end: 끝 시각
        who: 예약자
    """
    if room not in ROOMS:
        return {"거부": f"없는 방입니다: {room}", "가능한_방": list(ROOMS)}
    if any(b["room"] == room and b["date"] == date
           and not (b["end"] <= start or b["start"] >= end) for b in BOOKED):
        return {"거부": f"{room} 은 그 시간에 이미 예약되어 있습니다."}
    BOOKED.append({"room": room, "date": date, "start": start, "end": end, "who": who})
    return {"확정": room, "날짜": date, "시간": f"{start}~{end}", "예약자": who}


if __name__ == "__main__":
    mcp.run()
