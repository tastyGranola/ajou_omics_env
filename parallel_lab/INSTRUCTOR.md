# 강사용 — 2일차 2교시

> 수강생 안내서: [LAB.md](LAB.md) · 1교시: [../mcp_lab/INSTRUCTOR.md](../mcp_lab/INSTRUCTOR.md)

## 1. 실습 구성 · 50분

| | | 분 |
|---|---|---|
| 0 | 왜 worktree 인가 — 강사 화면으로 구조 한 장 | 2 |
| 1 | `setup.sh` 로 실험 두 개 생성 · 두 `CLAUDE.md` 비교 | 5 |
| 2 | 세션 A 띄우고 계획 승인 → **두고 나옴** | 10 |
| 3 | 세션 B 를 단계별로 진행 (A 는 그동안 계속 돔) | 20 |
| 4 | 세션 C 에서 비교 리포트 | 12 |
| 5 | 일반화 — 아이디어 N 개 · `setup.sh <이름>...` | 3 |

**이 교시의 뼈대는 2번 끝의 "두고 나옴" 입니다.** 여기서 기다리게 두면 실습이 무너집니다.
A 가 도는 것을 확인하는 즉시 새 터미널을 열게 하세요.

## 2. 밀릴 때 버릴 순서

1. 4번의 후속 질문들 → `comparison_report.html` 만 열고 끝
2. 5번 → 말로만 ("이름만 바꾸면 셋도 넷도 됩니다")
3. 3번의 단계를 6개 → 4개로 (annotation 까지만, DEG 생략)

**1번의 두 `CLAUDE.md` 비교와 3번의 배치 통합 갈림길은 못 버립니다.**
이 둘이 "무엇이 변수인가" 와 "왜 결과가 갈리는가" 를 각각 담당합니다.

## 3. 구조 — 무엇이 어디에 쓰이나

```
parallel_lab/
├── LAB.md                  수강생 안내서
├── INSTRUCTOR.md           이 파일
├── setup.sh                worktree + branch + CLAUDE.md + EXPERIMENT.md 생성
├── link_shared.py          공용 경로를 복사 대신 심볼릭 링크로 (setup.sh 가 부름)
├── status.sh               두 실험 상태를 한 표로
├── cleanup.sh              worktree/branch 제거 (comparison/ 은 남김)
├── metrics_template.json   비교를 가능하게 하는 공통 스키마
└── prompts/                수강생이 붙여 넣는 프롬프트 3개
```

실험별 진행 방식은 `setup.sh` 의 `rules_block()` 안에 있습니다.
방식을 바꾸고 싶으면 그 함수만 고치면 됩니다.

## 4. 설계 의도 — 세 가지

**(1) 격리는 worktree 가, 비교는 스키마가 한다.**
worktree 는 `results/` 충돌만 막아 줍니다. 비교가 되게 하는 것은
`results/summary/metrics.json` 의 **공통 키 이름**입니다.
`CLAUDE.example.md` 에 "정해진 키 이름을 바꾸지 않는다" 가 들어 있는 이유입니다.
이 약속이 없으면 세션 C 는 두 개의 서로 다른 리포트를 나열만 합니다.

**(2) `decided_by` 가 이 교시의 핵심 지표다.**
A 는 `claude`, B 는 `human` 이 대부분입니다. 같은 데이터·같은 질문인데
**결정의 주체가 다르면 결과가 갈린다** — 이게 수강생이 가져갈 문장입니다.
`status.sh` 의 `결정(사람/전체)` 열이 이걸 실습 중간에 계속 보여줍니다.

**(3) 실험 세션은 서로를 못 본다.**
`CLAUDE.md` 에 "다른 worktree 를 읽지 않는다 · branch 를 옮기지 않는다" 를 넣었습니다.
안 넣으면 B 가 A 의 결과를 참고해서 수렴해 버리고, 비교할 것이 없어집니다.

**(4) 공용 입력은 나눠 쓰고, 실험이 만드는 것만 가른다.**
`setup.sh` 는 저장소를 통째로 복사하지 않습니다. `data/raw/` `mcp_lab/` `parallel_lab/`
`.devcontainer/` `core_markers.xlsx` 는 **main 을 가리키는 심볼릭 링크**로 걸립니다.
worktree 하나가 73MB → **17MB** 가 됩니다.

`data/processed/` 는 **일부러 공유하지 않습니다.** `CLAUDE.md` 상 QC·정규화 중간 데이터가
쌓이는 곳이라, 공유하면 두 실험이 서로의 중간 파일을 덮어씁니다. 여기가 이 설계의
유일한 판단 지점이니 질문이 나오면 이걸로 답하세요.

수강생에게 보여줄 한 줄:

```bash
ls -l worktrees/plan-execute/data/raw/ worktrees/plan-execute/data/processed/
```

**화살표가 붙은 것은 공용, 실물인 것은 이 실험 것.** 파일 목록만 봐도 구분됩니다.

### 구현 — 물어보면

`git worktree add --no-checkout` → `read-tree` (index 만) → 공용 경로에 `--skip-worktree`
→ `checkout-index -a` (나머지만 실제로 꺼냄) → 파일 단위 상대 심볼릭 링크.

디렉토리째 링크하지 않고 **파일 단위**로 거는 이유는, 디렉토리를 링크하면 git 이 그것을
untracked 로 보고 `git status` 에 남기 때문입니다. 지금은 `git status` 가 `?? EXPERIMENT.md`
하나만 나옵니다 — 그래서 "이 실험이 만든 것" 이 한눈에 보입니다.

**`git worktree remove` 는 심볼릭 링크를 따라가지 않습니다** (확인함). 실험을 지워도
공용 데이터는 그대로입니다.

## 5. 예상 결과 — 미리 알고 계셔야 할 것

수치는 매번 달라집니다. **갈리는 자리**가 거의 고정입니다.

| 갈림길 | A 의 경향 | B 의 경향 |
|---|---|---|
| `n_genes` 상한 | 상한을 걸고 진행 (근거는 로그에 남김) | 잘려나가는 세포를 먼저 확인시킴 → 상한을 안 걸거나 완화 |
| `stim` 배치 보정 | **보정 쪽으로 기우는 편** — UMAP 이 깔끔해지므로 | 조건 효과가 지워질 위험을 지적받고 보정 없이 가는 경우가 많음 |
| clustering resolution | 기본값 근처에서 한 번에 결정 | 여러 값을 보고 고름 |

**배치 보정에서 갈리면 DEG 개수가 자릿수로 차이 납니다.** 1교시의
"미보정 4,231개 vs 보정 187개" 와 같은 종류의 현상입니다. 연결해서 설명하세요.

> A 와 B 가 우연히 똑같이 결정해서 결과가 거의 같게 나올 수도 있습니다.
> 그때는 **결정 로그를 여세요.** "결과는 같지만 이 결정을 아무도 검토하지 않았다" 가
> 오히려 더 좋은 재료입니다.

## 6. 자원 — 미리 확인할 것

| | |
|---|---|
| 디스크 | worktree 하나당 17MB (`data/processed/` 18MB 만 실물). 기본 2개 = +34MB |
| 메모리 | **8GB 에서 scanpy 세션 두 개가 동시에 돕니다.** 여기가 유일한 병목입니다 |
| 세션 | A 실행 · B 대화 · C 비교 — 터미널 3개 |

메모리가 빠듯해 보이면 3번에서 B 를 annotation 까지만 돌리게 하세요.

## 7. 강의 전날 점검

```bash
git status                       # 깨끗해야 함
bash parallel_lab/setup.sh
ls worktrees/plan-execute        # data/ CLAUDE.md EXPERIMENT.md .mcp.json
find worktrees/plan-execute -type l | wc -l     # 공용 링크 33개
git -C worktrees/plan-execute status --short    # ?? EXPERIMENT.md 하나만
du -sh worktrees/plan-execute    # 17M 안팎
tail -20 worktrees/plan-execute/CLAUDE.md      # 진행 방식 블록이 붙었는지
tail -20 worktrees/stepwise-hitl/CLAUDE.md     # 다른 내용인지
bash parallel_lab/status.sh      # 표가 "-" 로라도 뜨는지
bash parallel_lab/setup.sh test-idea            # 임의 이름도 되는지
bash parallel_lab/cleanup.sh                    # 목록만
bash parallel_lab/cleanup.sh --yes              # 정리
git worktree list                # main 하나만 남아야 함
git branch                       # exp/* 가 없어야 함
```

한 번은 **실제로 A 를 끝까지 돌려 보세요.** 8GB 에서 걸리는 시간을 알고 계셔야
3번의 20분을 배분할 수 있습니다.

## 8. 환경 — 1교시 Codespace 그대로 씁니다
