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

.claude/agents/
└── step-validator.md       단계별 검증 에이전트 (읽기 전용) · 모든 실험이 공유
                            기능 분석 단계의 확인 목록도 여기에 들어 있습니다

data/genesets/              기능 분석의 prior knowledge 캐시 · 공용 (커밋 필요)
```

기능 분석용 자산은 `parallel_lab/` 안에 있습니다.

| | |
|---|---|
| `CHEATSHEET.md` | decoupler 2.x API · **맨 앞이 1.x↔2.x 대응표** |
| `fetch_genesets.py` | Hallmark · Reactome · PROGENy · CollecTRI 를 `data/genesets/` 에 캐시 |
| `verify.py` | 패키지 · 캐시 · 입력 데이터 점검 |

실험별 진행 방식은 `setup.sh` 의 `rules_block()` 안에 있습니다.
방식을 바꾸고 싶으면 그 함수만 고치면 됩니다.

## 4. 설계 의도 — 다섯 가지

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
`setup.sh` 는 저장소를 통째로 복사하지 않습니다. `data/raw/` `data/genesets/` `mcp_lab/`
`parallel_lab/` `.devcontainer/` `.claude/agents/` `core_markers.xlsx` 는
**main 을 가리키는 심볼릭 링크**로 걸립니다. worktree 하나가 73MB → **17MB** 가 됩니다.

`data/genesets/`(기능 분석의 prior knowledge 캐시)를 공유하는 이유는 `.claude/agents/` 와 같습니다.
실험마다 다른 gene set 을 받아 오면 **"gene set 을 바꿨더니 결과가 달라졌다" 를 말할 수 없습니다.**
단, `link_shared.py` 가 `git ls-files` 로 추적되는 파일만 링크하므로
**강의 전에 `data/genesets/` 를 커밋해 두어야 합니다.**

`data/processed/` 는 **일부러 공유하지 않습니다.** `CLAUDE.md` 상 QC·정규화 중간 데이터가
쌓이는 곳이라, 공유하면 두 실험이 서로의 중간 파일을 덮어씁니다. 여기가 이 설계의
유일한 판단 지점이니 질문이 나오면 이걸로 답하세요.

**(5) 검증자는 실험 밖에 두고, 두 축으로 채점하게 한다.**
`.claude/agents/step-validator.md` 는 단계마다 **정확성**과 **완결성**을 1–5 점으로 매기는
읽기 전용 서브에이전트입니다. 실험 안이 아니라 **공용 경로에 두고 링크로 나눠 씁니다.**
채점 기준까지 실험마다 다르면 "A 점수가 더 높았다" 가 아무 의미도 없어지기 때문입니다.

채점표와 절차는 Biomni 논문 보충자료(Science 393, eadz4351)에서 가져왔습니다 —
Table S32–S33 의 완결성·정확성 1–5 루브릭, 그리고 Section I 의 두 가지 장치입니다.
**평가자를 출처에 블라인드로 두는 것**(채점 전에 진행 방식을 보지 않는다)과,
**발견이 데이터에서 나온 것인지 코드와 트레이스를 따라가며 확인하는 것**(수치 추적 최소 3건).
데이터에 없는 수치가 기록되어 있으면 정확성 1점입니다.

**정확성과 완결성을 나눈 것이 4번에서 쓸 재료입니다.** 두 실험의 정확성이 비슷한데
완결성만 갈렸다면 그것은 분석이 다른 게 아니라 **기록이 다른 것**입니다.

세션 A 는 프롬프트 `R4` 에 검증 호출이 규칙으로 박혀 있어 스스로 검증하고 스스로 반영합니다.
세션 B 는 수강생이 원할 때 부릅니다. **같은 검증 결과를 누가 읽느냐가 다시 한번 갈립니다.**

검증자도 Claude 라는 점을 4번에서 반드시 짚으세요. `PASS` 가 옳다는 뜻이 아닙니다.
세션 C 의 "검증자가 놓친 것을 찾아줘" 가 이 교시에서 가장 좋은 마무리 질문입니다.

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
| 시간 | A 가 단계마다 검증 에이전트를 부릅니다. 검증 7회 + resolution sweep 5회분이 더해지니 **드라이런에서 A 의 총 실행 시간을 반드시 다시 재세요** |

메모리가 빠듯해 보이면 3번에서 B 를 annotation 까지만 돌리게 하세요.

## 7. 강의 전날 점검

```bash
git status                       # 깨끗해야 함
bash parallel_lab/setup.sh
ls worktrees/plan-execute        # data/ CLAUDE.md EXPERIMENT.md .mcp.json
find worktrees/plan-execute -type l | wc -l     # 공용 링크 44개
                                               # gene set 넷을 다 받아 커밋했을 때.
                                               # data/genesets/ 미커밋이면 39개
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

## 8. 7단계 기능 분석 — 강사가 알고 있어야 할 것

**(1) 양성 대조가 내장되어 있다.** IFN-beta 자극이므로 인터페론 반응이 최상위여야 합니다.
앞 단계 파손 탐지(배치 보정으로 조건 효과를 지웠다면 여기서 드러납니다)와
환각 탐지를 동시에 합니다.

**다만 통과가 나머지를 보증하지 않습니다.** 4번에서 반드시 짚으세요 —
비교 프롬프트의 마지막 질문이 이걸 노립니다.

**(2) pseudobulk 가 6단계의 미해결 항목을 푼다.**
6단계는 pseudoreplication 을 **한계로 적기만** 합니다. 도너가 8명, 조건마다 8명 전부
있으니 (도너 × 조건)으로 합치면 **8 대 8** 의 진짜 반복이 됩니다.
수강생이 두 DEG 개수를 나란히 놓게 하세요 — 대개 자릿수가 다릅니다.
1교시의 "미보정 4,231개 vs 보정 187개" 와 같은 종류의 장면이니 연결해서 설명하세요.

**(3) 한 실험 안에서 비교시킨다.** 프롬프트 7.4 가 gene set 을 둘 이상, 방법을 둘 이상
써서 일치도를 재게 합니다. 챕터의 결론(결과는 방법의 선택보다 gene set 의 선택에
더 민감하다 — Holland et al. 2020)을 **실험을 늘리지 않고** 확인하는 자리입니다.

세션 C 에서는 "**두 실험의 답이 서로 같은가**" 를 봅니다. 한 실험에서만 그렇게 나왔다면
자원의 성질이 아니라 그 실험의 다른 결정 때문일 수 있습니다.

**(4) 자원의 성격 차이가 수치로 보인다.** `fetch_genesets.py` 가 집합 크기 분포를
manifest 에 남깁니다. 아래는 실측값입니다.

| | 종류 | 집합 수 | 크기 (중앙값) | `tmin=15` 에서 |
|---|---|---|---|---|
| Hallmark | gene set | 50 | 32~200 (199) | **하나도 안 잘림** |
| Reactome | gene set | 2,105 | 5~2,613 (25) | **710개가 잘림** (3분의 1) |
| PROGENy | footprint | 14 | 202~500 (499) | 안 잘림 (`top=500` 이라) |
| CollecTRI | footprint | 1,185 | 1~1,304 (9) | **716개가 잘림 — 걸면 안 됨** |

마지막 줄이 중요합니다 — `tmin` 은 gene set 에 거는 것이지 footprint 에 거는 것이 아닙니다.
CollecTRI 에 `tmin=15` 를 걸면 TF 의 60%가 조용히 사라지고, **그래도 STAT1 은 남아서
양성 대조는 통과합니다.** 양성 대조가 못 잡는 오류의 좋은 예입니다.

**(5) decoupler 2.x 를 쓰는 것 자체가 실습 장치다.**
decoupler 는 2.0 에서 API 가 전면 개편됐습니다 (`dc.run_ulm` → `dc.mt.ulm`).
LLM 이 학습한 코드 대부분은 1.x 이므로 **Claude 가 1.x 코드를 쓸 가능성이 높습니다.**

버그가 아니라 **오늘 반드시 보게 해야 할 장면**입니다. `AttributeError` 가 났을 때
Claude 가 스스로 `CHEATSHEET.md` 를 보고 고치는지 지켜보세요. 못 고치고 다른 1.x 함수로
바꿔 가며 시도하면, 그때 "설치된 버전의 문서를 확인해" 라고 개입하는 것이
이 교시에서 가장 좋은 개입입니다.

### 실측 결과 — 미리 알고 계셔야 할 것

전체 세포를 (도너 × 조건)으로 pseudobulk 해서 실제로 돌려 본 값입니다
(세포 타입을 나누지 않은 것이라 수강생 결과와 정확히 같지는 않습니다).

```
pseudobulk       16 표본 (ctrl 8 · stim 8) · filter_by_expr 후 5,969 유전자
pydeseq2         padj < 0.05 인 유전자 1,821개
Hallmark GSEA    1. INTERFERON_ALPHA_RESPONSE   2.65
                 2. INTERFERON_GAMMA_RESPONSE   2.60
                 3. KRAS_SIGNALING_DN           1.83
PROGENy ULM      JAK-STAT 47.1  ·  NFkB 11.4  ·  TNFa 6.2
```

| 항목 | 예상 |
|---|---|
| 상위 1·2위 | 어떤 자원·방법으로도 인터페론. **여기는 안 갈립니다** |
| 3위 이하 | `KRAS_SIGNALING_DN` 처럼 해석하기 난감한 것이 섞입니다. **여기가 갈립니다** |
| 세포 타입 순서 | 단핵구 계열(CD14+ · FCGR3A+)에서 IFN 반응이 가장 강한 경향 |
| PROGENy | `JAK-STAT` 이 압도적 (다음 항목의 4배) |
| CollecTRI | `STAT1` · `STAT2` · `IRF9` · `IRF1` |
| DC · Megakaryocyte | 세포가 적어 pseudobulk 표본이 얇음. 저신뢰 표시되는지 확인 |

### 자원

**세포 수준 점수를 Reactome 전체(2,105개 집합)로 돌리게 하지 마세요.** 8GB 에서 버겁습니다.
세포 수준은 Hallmark(50개)나 PROGENy(14개)로, Reactome 은 조건 대비(행 몇 개)에만
쓰는 것이 맞습니다. 계획 단계에서 봐 주세요.

세포 타입 8개에 pydeseq2 를 도는 것이 7단계에서 가장 오래 걸립니다.

## 9. 환경 — 1교시 Codespace 그대로 씁니다
