# 환경 구축 — 강사용

> `isg-bspark/ajou-omics-env` 하나로 1일차(single-cell 분석)와
> 2일차 1교시(MCP 실습)를 **같은 Codespace 에서** 돌립니다.
> 별도 저장소·별도 컨테이너가 필요하지 않습니다.

---

## 1. 저장소 구조 — MCP 실습에 관련된 것만

```
ajou-omics-env/
├── .devcontainer/
│   ├── devcontainer.json      이미지 · 시크릿 · VS Code 설정 · PATH
│   ├── post-create.sh         설치와 점검을 전부 여기서 (6단계)
│   ├── requirements.txt       분석 패키지 + mcp[cli] + uv
│   └── tools.txt              uvx 로 미리 받아둘 MCP 서버
├── .mcp.json                  ← 반드시 저장소 루트. 비어 있는 채로 시작
├── README.md                  수강생 첫 화면
└── mcp_lab/
    ├── LAB.md                 수강생용 실습 안내 ★
    ├── INSTRUCTOR.md          당일 운영 · 대본
    ├── ENV_SETUP.md           이 문서
    ├── server.py              오믹스 서버 — 도구 2개 (③은 실습에서 추가)
    ├── verify.py              환경 점검 (post-create 마지막에 자동 실행)
    ├── check.py               서버 단독 점검
    ├── doctor.sh              안 될 때 진단
    └── reference/             정답본 · 단계별 .mcp.json
```

`mcp_lab/meeting.py` 는 **저장소에 없습니다.** 실습 ①에서 수강생이 직접 만듭니다.

---

## 2. 확인된 요구사항

| | |
|---|---|
| **Python** | **3.10 이상** — `mcp` 패키지 요구사항. 현재 이미지는 **3.11** |
| **패키지** | `mcp[cli]` · `uv` — `.devcontainer/requirements.txt` 에 포함 |
| **claude** | `npm install -g @anthropic-ai/claude-code` (post-create 4단계) |
| **인증** | `ANTHROPIC_API_KEY` 또는 `CLAUDE_CODE_OAUTH_TOKEN` (Codespaces 시크릿) |
| **머신** | 2코어 / 8GB — MCP 실습은 실제 계산을 하지 않습니다 |

`server.py` 는 `mcp` **1.x · 2.x import 를 둘 다** 받게 써두었습니다. 버전이 올라가도 안 깨집니다.

---

## 3. post-create.sh 가 하는 일 — 6단계

저장소가 `/workspaces` 에 마운트되고 Codespaces 시크릿이 환경변수로 들어온 **뒤에** 한 번 돕니다.

| | | 실패하면 |
|---|---|---|
| **1** | pip 업그레이드 + `requirements.txt` 설치 (분석 패키지 + `mcp[cli]` + `uv`) | 중단 |
| **2** | `tools.txt` 의 MCP 서버를 `uv tool install` 로 미리 받기 | **경고만** — 실습 때 uvx 가 다시 받습니다 |
| **3** | Jupyter 커널 `ajou-omics` 등록 | 중단 |
| **4** | Claude Code CLI 설치 (npm) | 중단 |
| **5** | `~/.claude-workshop.sh` 작성 · PATH · 인증 안내 | 중단 |
| **6** | `mcp_lab/verify.py` 실행 — **점검만** | **경고만** — Codespace 생성은 계속 |

1일차 환경(scanpy 스택)과 2일차 환경(mcp·uv)이 **같은 인터프리터**에 깔립니다.
`.mcp.json` 에 `"command": "python3"` 라고만 적으면 `mcp` 가 보이는 이유입니다.

### 왜 Dockerfile 이 아닌가

이 저장소는 처음부터 `image` + `post-create.sh` 구조입니다.
scanpy 스택 설치가 이미 post-create 에 있어서, MCP 쪽만 Dockerfile 로 빼면 설치 지점이 둘로 갈립니다.
**한 곳에 모으는 쪽**을 골랐습니다.

### ⚠ Prebuild 는 이 수업에 도움이 되지 않습니다

**켜지 마세요.** 스토리지 요금만 나가고 수강생은 아무 이득을 못 봅니다. 이유가 둘입니다.

**1. Prebuild 는 `postCreateCommand` 를 실행하지 않습니다.**

프리빌드 단계에서 도는 것은 `onCreateCommand` 와 `updateContentCommand` 뿐입니다.
이 저장소는 설치 전부가 `post-create.sh` 안에 있으므로, prebuild 를 켜도
**캐시되는 것은 베이스 이미지 pull 과 node feature 뿐**이고 pip 설치는 매번 그대로 돕니다.

**2. fork 는 upstream 의 prebuild 를 받지 못합니다.**

prebuild 는 저장소·브랜치 단위로 붙습니다. fork 는 별개 저장소라
**각자 자기 fork 에 따로 설정**해야 하고, 그 스토리지는 fork 한 사람 개인 계정에 청구됩니다.
수강생이 fork 하는 이 수업에서는 강사 저장소의 prebuild 가 수강생에게 닿지 않습니다.

> 참고 — prebuild 중에는 `ANTHROPIC_API_KEY` 같은 **user-level 시크릿을 쓸 수 없습니다.**
> 설치를 `onCreateCommand` 로 옮기더라도 인증 안내(5단계)와 `verify.py`(6단계)는
> postCreate 에 남아야 합니다.

### 그래서 최초 생성 시간은 그대로 듭니다

**수강생 1인당 수 분**(이미지 pull + scanpy 스택 설치)입니다. 줄이려면 방법은 하나뿐입니다.

| | |
|---|---|
| **A · 현재** | 그냥 감수합니다. 사전배포에 *"최초 1회 3~5분"* 을 명시하고, 강의 시작 전에 미리 열어 두게 합니다 |
| **B** | 설치를 마친 **이미지를 GHCR 에 public 으로 올려두고** `devcontainer.json` 의 `"image"` 가 그것을 가리키게 합니다. 이미지는 저장소가 아니라 **주소**라서 **fork 에도 그대로 따라갑니다** — prebuild 와 달리 이 방법은 통합니다 |

**B 를 고르실 거면 강의 며칠 전에 하셔야 합니다.** 이미지를 굽고, GHCR 패키지를
**public 으로 바꾸고**(기본값은 private 입니다), 테스트 fork 에서 실제로 당겨봐야 합니다.
`requirements.txt` 가 바뀔 때마다 다시 굽는 것도 강사 몫이 됩니다.

### 사전 점검은 여전히 필요합니다

prebuild 를 안 켜면 *"설치가 깨졌는지"* 를 미리 알려주는 장치가 없습니다.
**강의 전에 테스트 Codespace 를 한 번 만들어** 6단계가 끝까지 도는지 보세요 (6절).

---

## 4. 사전배포 자료와의 관계

post-create 가 **Claude Code 를 자동 설치**합니다.
사전배포 **8장(`curl … install.sh | bash` 직접 입력)은 불필요**합니다.

*"자동으로 설치됩니다. 안 되면 이 명령"* 으로 바꾸시는 편이 낫습니다.
30명이 각자 `curl` 을 치는 시간이 사라집니다.

---

## 5. ⚠ Fork 타이밍

사전배포가 이미 나갔다면 수강생 일부가 **이미 fork** 했습니다.
그 뒤에 업스트림에 파일을 추가해도 **각자 fork 에는 들어가지 않습니다.**

| | |
|---|---|
| **A · 권장** | **지금 다 넣고 확정.** 이후 저장소를 건드리지 않습니다 |
| **B** | 당일 첫 순서로 GitHub **Sync fork** 안내 (스크린샷 한 장 필요) |

---

## 6. 구축 후 검증 — 이 순서로

### 테스트 코드스페이스에서

```bash
python3 mcp_lab/verify.py
```

앞의 네 항목이 모두 ✓ 여야 합니다. (뒤 두 개는 `·` 여도 됩니다)

```
✓ Python 3.10 이상        3.11.x
✓ mcp 패키지              v2.0.0
✓ uvx  (실습 ③ 용)        /usr/local/bin/uvx
✓ claude 명령             /usr/local/share/nvm/.../claude
· 바깥 인터넷 (실습 ③ 용)
· Claude Code 인증
```

### 그다음 서버 단독 점검

```bash
python3 mcp_lab/check.py mcp_lab/reference/meeting.py        # 도구 2개
python3 mcp_lab/check.py mcp_lab/reference/server_완성본.py   # 도구 3개
```

### 마지막으로 Claude Code 로

```bash
cp mcp_lab/reference/step3.mcp.json .mcp.json
cp mcp_lab/reference/meeting.py mcp_lab/meeting.py
claude
/mcp            # meeting · sc-omics · fetch · biocontext 넷 다 connected
```

```
이 데이터가 뭔지 알려줘
```

`dataset_overview` 가 불리고 **세포 12,000** 이 나오면 끝입니다.

**되돌리기를 잊지 마세요.**

```bash
git checkout .mcp.json
rm mcp_lab/meeting.py
```

---

## 7. 원격 서버 — 강의 전날 확인

실습 ③에 쓸 무인증 원격 서버입니다. **실제로 붙여보셔야 합니다.**

| | |
|---|---|
| **1안** | `https://biocontext-kb.fastmcp.app/mcp/` — 생명과학 DB 묶음. **사용량 제한 있음** |
| **2안** | `https://mcp.deepwiki.com/mcp` — GitHub 저장소 질문. 안정적 |

> **주소 주의.** `https://mcp.biocontext.ai/mcp/` 는 **301** 로 넘깁니다.
> `.mcp.json` 에는 최종 주소를 직접 적습니다.

조직 Codespaces 네트워크 정책으로 막힐 수 있으니 **테스트 코드스페이스 안에서** 확인하세요.
사용량 제한 때문에 **실습 ③의 원격 부분은 강사 시연으로만** 하시는 편이 안전합니다.

---

## 8. 체크리스트

- [ ] `mcp_lab/` · `.mcp.json` · `.devcontainer/tools.txt` 커밋
- [ ] `requirements.txt` 에 `mcp[cli]` · `uv` 들어갔는지
- [ ] `post-create.sh` 가 6단계인지
- [ ] Prebuild 는 켜지 않음 — fork 에 안 따라갑니다 (3절)
- [ ] 최초 생성 시간 대책 A/B 결정 (3절)
- [ ] 사전배포 8장 처리 결정 (4절)
- [ ] Fork 타이밍 결정 (5절)
- [ ] 테스트 코드스페이스에서 `verify.py` 통과
- [ ] `check.py` 로 정답본 두 개 확인
- [ ] `claude` → `/mcp` → 도구 호출까지 확인 후 **되돌리기**
- [ ] 원격 서버 두 개 중 최소 하나 확인
