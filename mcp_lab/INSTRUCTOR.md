# 강사용 — 2일차 1교시

> 수강생 안내서: [LAB.md](LAB.md) · 환경 구축: [ENV_SETUP.md](ENV_SETUP.md)

## 1. 실습 구성 · 30분

| | | 분 | 재시작 |
|---|---|---|---|
| ① | 회의실 예약 서버 붙여넣기 → 등록 → 호출 → **설명만 바꿔서 다시** | 12 | 2 |
| ② | `server.py` 에 도구 하나 추가 → 등록 → 호출 | 8 | 1 |
| ③ | `fetch` + `biocontext` 를 **한 번에** 추가 | 8 | 1 |
| | 정리 — `/mcp` 에 넷이 나란히 | 2 | |

**재시작은 Claude Code 만입니다** (`/exit` → `claude`). 컨테이너는 건드리지 않습니다.

## 2. 밀릴 때 버릴 순서

1. ③의 `biocontext` → 강사 화면으로 대체
2. ①-4 설명 바꾸기 실험

**①의 등록과 ②의 도구 추가는 이 교시의 뼈대라 못 버립니다.**

## 3. 확인된 사실 (2026-08-28, 코드스페이스 안에서 측정)

| | |
|---|---|
| 조직 네트워크 정책 | **제약 없음** — pypi · npm 200, `api.anthropic.com` 401 |
| `biocontext` | **30/30 `200`** · `serverInfo: BC 2.13.1` |
| `deepwiki` | **30/30 `200`** — 백업용 |

> **주소 주의.** `https://mcp.biocontext.ai/mcp/` 는 **301** 로 넘깁니다.
> `.mcp.json` 에는 최종 주소 `https://biocontext-kb.fastmcp.app/mcp/` 를 직접 적습니다.
> 백업: `https://mcp.deepwiki.com/mcp`

## 4. 강의 전날 점검

```bash
python3 mcp_lab/verify.py                              # 환경 4항목
python3 mcp_lab/check.py mcp_lab/reference/meeting.py  # 도구 2개
python3 mcp_lab/check.py mcp_lab/reference/server_완성본.py   # 도구 3개
cp mcp_lab/reference/step3.mcp.json .mcp.json
cp mcp_lab/reference/meeting.py mcp_lab/meeting.py
claude          # /mcp 에서 넷 다 connected · 실제 도구 호출까지
git checkout .  # 되돌리기 — 반드시
```

**`tools/list` 와 실제 호출은 `claude` 로만 확인됩니다.** curl 은 `initialize` 까지가 한계입니다.

## 5. ②의 예상 결과 — 미리 알고 계셔야 할 숫자

```
미보정 run(r_raw) → 유의 4,231개 · 1위 MT-CYB, RPS27, MT-ATP6, MT-CO1, ACTB
보정   run(r_int) → 유의   187개 · 1위 IRF1, B2M, TAP1, CXCL10, GBP1
```

미보정 상위가 **미토콘드리아 · 리보솜**입니다. **1교시에서는 숫자가 달라진다는 것만** 보여주고,
*"이게 왜 문제인지"* 는 2교시로 넘기세요.

## 6. 환경 — 1일차 Codespace 그대로 씁니다

**따로 만들 것이 없습니다.** 1일차에 쓰던 Codespace 에서 바로 이어갑니다.
설치는 전부 `.devcontainer/post-create.sh` 가 생성 시점에 끝냈습니다.

```
.devcontainer/requirements.txt   분석 패키지 + mcp[cli]>=2.0 · uv>=0.5
.devcontainer/tools.txt          uvx 로 미리 받아둘 MCP 서버
.devcontainer/post-create.sh     위 둘을 읽어 설치 + Claude Code + verify.py
.mcp.json                        저장소 루트. 비어 있는 채로 시작합니다
mcp_lab/                         실습 코드 · 정답본
```

다른 환경(로컬 등)에 옮길 때는 이 두 줄이면 동일합니다.

```bash
python3 -m pip install -r .devcontainer/requirements.txt
sed -e 's/#.*//' -e '/^[[:space:]]*$/d' .devcontainer/tools.txt | xargs -r -n1 uv tool install
```

- **`mcp` 는 `python3` 가 가리키는 인터프리터**에 깔려야 합니다 (`pip` 이 아니라 `python3 -m pip`)
  — `.mcp.json` 에 `"command": "python3"` 라고 적기 때문입니다
- `claude` 는 pip 패키지가 아닙니다 — npm 으로 따로 깝니다
- `.mcp.json` 은 **반드시 저장소 루트**에 있어야 Claude Code 가 읽습니다

### ⚠ Prebuild 는 켜지 마세요 — 이 수업엔 안 통합니다

두 가지 때문입니다. 자세한 건 [ENV_SETUP.md](ENV_SETUP.md) 3절.

- prebuild 는 **`postCreateCommand` 를 실행하지 않습니다.** 설치가 전부 거기 있으므로 캐시될 게 없습니다
- **fork 는 upstream 의 prebuild 를 못 받습니다.** 수강생은 각자 fork 에서 Codespace 를 만듭니다

**1인당 수 분**(이미지 pull + scanpy 스택 설치)은 그대로 듭니다.
**1교시 시작 전에 미리 Codespace 를 열어 두게 하세요.** 2일차에 처음 여는 사람이 있으면
그 사람만 실습 ① 을 못 따라옵니다.

문제가 생기면:

```bash
bash mcp_lab/doctor.sh
```

## 7. Fork 타이밍

사전배포가 나갔다면 일부는 **이미 fork** 했습니다. 이후 추가한 파일은 각자 fork 에 안 들어갑니다.

| | |
|---|---|
| **A · 권장** | 지금 확정하고 더 안 건드립니다 |
| **B** | 당일 첫 순서로 GitHub **Sync fork** 안내 |

## 8. 자주 나올 질문

**"Bash 로 하면 되잖아요?"**
→ 됩니다. 다만 매번 다른 코드가 나오고, 데이터가 서버에만 있으면 못 합니다.

**"거부를 프롬프트로 우회할 수 있나요?"**
→ ①-3의 겹친 예약에서 직접 해보게 하세요. 부탁해도 안 됩니다.

**"계산을 진짜로 하나요?"**
→ 아닙니다. 미리 넣어둔 값입니다. **숨기지 말고 그대로 말하세요** —
   *"Claude 입장에서는 완전히 같습니다. 어차피 행렬을 못 보고 요약만 받으니까요."*

**"설명만 바꿨는데 왜 안 불러요?"** (①-4)
→ 그게 오늘의 핵심입니다. **Claude 가 보는 건 설명뿐**이라서 그렇습니다.
