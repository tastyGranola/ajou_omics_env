# 2일차 1교시 실습 — MCP 서버 만들고 붙이기

> 약 30분 · **코드를 짜지 않습니다.** 붙여 넣고, 한 군데만 고칩니다.
>
> 1일차에 쓰던 **그 Codespace 그대로**입니다. 새로 만들 것이 없습니다.
> 아래 명령은 모두 **저장소 루트**(`/workspaces/ajou-omics-env`)에서 실행합니다.

지금 `.mcp.json` 은 비어 있습니다. 오늘 여기에 **세 번** 도구를 더합니다.

| | 무엇을 붙이나 | 어디서 왔나 | `.mcp.json` 에 적는 것 |
|---|---|---|---|
| **①** | 회의실 예약 | **내가 만든 것** | `command` + 내 파일 |
| **②** | 오믹스 도구 하나 더 | **내가 만든 것** | 〃 |
| **③** | `fetch` 와 `biocontext` | **남이 만든 것** | `command` / **`url`** |

끝나면 넷이 `/mcp` 에 나란히 있습니다. 그리고 **Claude 는 넷을 구분하지 못합니다.**

---

## 0. 준비

Codespace 를 만들 때 이미 한 번 돌았지만, 지금 다시 확인합니다.

```bash
python3 mcp_lab/verify.py
```

앞의 네 항목이 `✓` 면 시작합니다. 뒤의 두 개는 `·` 여도 됩니다.
`✗` 가 있으면 화면의 안내대로 하거나 `bash mcp_lab/doctor.sh` 를 실행하세요.

---

## 실습 ① — 내가 만든 서버 · 12분

### 1-1. 파일을 만듭니다

`mcp_lab/meeting.py` 를 새로 만들고 **아래를 그대로 붙여 넣으세요.**

```python
"""회의실 예약 MCP 서버"""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("meeting")

ROOMS = {"세미나실": 20, "대회의실": 12, "소회의실": 4}
BOOKED = []


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
```

**여기를 한 번 보고 가세요.** 이 세 가지가 그대로 Claude 에게 넘어갑니다.

```
def find_rooms(date, start, end, people)   →   도구 이름 · 인자
"""비어 있는 회의실을 찾습니다."""          →   Claude 가 읽는 설명
Args: date: 날짜 (예 "2026-09-01")         →   인자 설명
```

**함수를 코드로 실행할 수 있는 건 이 서버뿐입니다.** Claude 는 위 세 줄만 봅니다.

혼자 떠는지 확인합니다.

```bash
python3 mcp_lab/check.py mcp_lab/meeting.py
```

> `도구 2개` 가 나오면 성공입니다.

### 1-2. `.mcp.json` 에 등록합니다

저장소 루트의 `.mcp.json` 을 열고 이렇게 바꿉니다.

```json
{
  "mcpServers": {
    "meeting": {
      "type": "stdio",
      "command": "python3",
      "args": ["mcp_lab/meeting.py"]
    }
  }
}
```

### 1-3. Claude Code 를 켭니다

```bash
claude
```

```
/mcp
```

**`meeting` 이 connected 로 보입니다.** 불러봅니다.

```
9월 1일 오후 2시부터 4시까지 10명 들어가는 회의실 있어?
```

```
그럼 세미나실로 내 이름으로 잡아줘
```

이제 **같은 방을 겹치게** 잡아보세요.

```
같은 날 3시부터 5시까지 세미나실 또 잡아줘
```

거절당합니다. **아무리 부탁해도 안 됩니다** — 도구 안에서 막고 있기 때문입니다.

그리고 한 번 물어보세요.

```
그 예약 내역은 어디에 저장돼 있어?
```

### 1-4. 설명만 바꿔봅니다 ★

`meeting.py` 에서 `find_rooms` 의 설명 **한 줄만** 바꿉니다.

```python
    """비어 있는 회의실을 찾습니다."""
```

를

```python
    """[사용 중지] 절대 사용하지 마세요. 고장난 도구입니다."""
```

로. **따옴표 안의 글자만 바꿉니다.** 코드는 손대지 않습니다.

고쳤으면 Claude Code 를 다시 띄웁니다. *(서버는 프로그램입니다. 고치면 다시 띄워야 반영됩니다.)*

```
/exit
```

```bash
claude
```

**똑같이** 물어보세요.

```
9월 1일 오후 2시에 회의실 있어?
```

> **코드는 한 줄도 안 바뀌었습니다. 설명만 바꿨는데 Claude 가 안 부릅니다.**
> 설명이 곧 인터페이스입니다.

확인했으면 설명을 원래대로 되돌리고 재시작하세요.

---

## 실습 ② — 도구 하나 더 · 8분

`mcp_lab/server.py` 를 엽니다. 오믹스 서버인데 **도구가 두 개뿐**입니다.
데이터는 파일 위쪽에 이미 준비되어 있습니다. **도구만 없습니다.**

파일 아래쪽 `도구 ③` 주석을 찾아 그 **아래에** 붙여 넣으세요.

```python
@mcp.tool()
def differential_expression(run_id: str, cell_type: str) -> dict:
    """세포 유형 안에서 반응군 vs 비반응군 차등발현을 계산합니다.

    Args:
        run_id: run_pipeline 이 돌려준 손잡이
        cell_type: 예) "종양세포"
    """
    run = _RUNS.get(run_id)
    if run is None:
        return {"거부": f"모르는 run_id 입니다: {run_id}",
                "다음": "run_pipeline() 을 먼저 부르세요."}

    if cell_type not in CELL_TYPES:
        return {"거부": f"모르는 세포 유형입니다: {cell_type}",
                "가능한_값": CELL_TYPES}

    result = DE_CORRECTED if run["batch_corrected"] else DE_UNCORRECTED
    return {"세포_유형": cell_type, **result}
```

> `@mcp.tool()` 은 **맨 왼쪽**에서 시작해야 합니다. 들여쓰기를 넣지 마세요.

확인합니다.

```bash
python3 mcp_lab/check.py mcp_lab/server.py
```

`도구 3개` 가 나오면 `.mcp.json` 에 등록합니다. **앞 항목 끝에 쉼표를 찍으세요.**

```json
{
  "mcpServers": {
    "meeting": {
      "type": "stdio",
      "command": "python3",
      "args": ["mcp_lab/meeting.py"]
    },
    "sc-omics": {
      "type": "stdio",
      "command": "python3",
      "args": ["mcp_lab/server.py"]
    }
  }
}
```

```
/exit
```

```bash
claude
```

```
/mcp
```

```
이 데이터가 뭔지 알려줘
```

```
전처리 돌리고 종양세포 차등발현 봐줘
```

**회의실 예약과 똑같은 방식입니다.** 함수 하나가 도구 하나가 됐을 뿐입니다.

---

## 실습 ③ — 남이 만든 서버 둘 · 8분

이번엔 만들지 않습니다. **이미 잘 만들어진 것을 가져옵니다.**
두 개를 **한 번에** 넣습니다.

`.mcp.json` 의 `mcpServers` 안에 두 항목을 더합니다.

```json
    "fetch": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "biocontext": {
      "type": "http",
      "url": "https://biocontext-kb.fastmcp.app/mcp/"
    }
```

전체 모습이 헷갈리면 `mcp_lab/reference/step3.mcp.json` 을 보세요.

```
/exit
```

```bash
claude
```

```
/mcp
```

넷 다 **connected** 입니다. 각각 불러봅니다.

```
https://modelcontextprotocol.io/docs/getting-started/intro 읽고 세 줄로 요약해줘
```

```
TP53 유전자에 대해 찾아봐줘
```

### 방금 무슨 일이 있었나

| | `fetch` | `biocontext` |
|---|---|---|
| 적은 것 | `command` + 패키지 이름 | **`url`** |
| 어디서 도나 | **이 컨테이너** | 인터넷 저편 |
| 누가 띄우나 | Claude Code | **이미 떠 있음** |
| 내가 설치했나 | 아니오 — `uvx` 가 알아서 | 아니오 |

`uvx` 는 그 서버를 **자기만의 환경에 따로** 받아서 띄웁니다. 내 파이썬은 한 톨도 안 바뀌었습니다.

---

## 정리 — `/mcp` 를 다시 봅니다

```
meeting      connected     ← ① 내가 만들었다
sc-omics     connected     ← ② 내가 도구를 더했다
fetch        connected     ← ③ 남의 것 · 내 컴퓨터에서 돈다
biocontext   connected     ← ③ 남의 것 · 남의 컴퓨터에서 돈다
```

**넷을 붙이는 데 설치한 것은 없습니다.** `.mcp.json` 에 몇 줄 적은 게 전부입니다.
그리고 **Claude 는 넷을 구분하지 못합니다.** 도구 목록에 나란히 있을 뿐입니다.

### 오늘 남길 네 가지

1. **함수 하나 = 도구 하나.** 이름 · 설명 · 인자만 밖으로 나갑니다
2. **설명이 곧 인터페이스입니다.** 설명을 바꾸면 행동이 바뀝니다
3. **도구 안의 규칙은 부탁으로 못 넘습니다.** 겹친 예약이 거절된 것처럼
4. **로컬이든 원격이든 쓰는 쪽에서는 같습니다.** 바뀌는 건 `command` 냐 `url` 이냐

**2교시** — 이 구조를 실제 오믹스 판단에 씁니다.

---

## 안 될 때

| 증상 | 해볼 것 |
|---|---|
| 고쳤는데 안 바뀐다 | **`/exit` 후 `claude` 재시작.** 거의 이것입니다 |
| `/mcp` 에 서버가 없다 | `python3 mcp_lab/check.py mcp_lab/meeting.py` |
| `failed` 로 뜬다 | 같은 명령으로 에러 메시지를 보세요 |
| `IndentationError` | `@mcp.tool()` 이 맨 왼쪽에서 시작하는지 |
| `.mcp.json` 이 깨졌다 | 쉼표 · 중괄호. 아래 "따라잡기" 참고 |
| `fetch` 가 robots.txt 오류 | `"args": ["mcp-server-fetch", "--ignore-robots-txt"]` |
| `biocontext` 가 안 붙는다 | 네트워크 정책일 수 있습니다. 넘어가도 됩니다 |

### 따라잡기 — 밀렸을 때

각 단계 시작 상태를 그대로 복사하면 됩니다.

```bash
cp mcp_lab/reference/step1.mcp.json .mcp.json      # ① 끝난 상태
cp mcp_lab/reference/step2.mcp.json .mcp.json      # ② 끝난 상태
cp mcp_lab/reference/step3.mcp.json .mcp.json      # ③ 끝난 상태

cp mcp_lab/reference/meeting.py        mcp_lab/meeting.py    # ① 정답
cp mcp_lab/reference/server_완성본.py   mcp_lab/server.py     # ② 정답
```

전부 되돌리려면:

```bash
git checkout .
```
