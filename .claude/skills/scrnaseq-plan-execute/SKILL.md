---
name: scrnaseq-plan-execute
description: 단일세포 RNA-seq 분석을 Biomni 형식(Task/Objective/Dataset/Path + 번호 붙은 단계 + 결정 로그 + step-validator 검증)으로 계획하고 실행한다. 연구 질문만 받아서 Task/Objective/Dataset/Path 를 코드베이스 탐색과 질문으로 채운 뒤, 체크박스 계획을 사용자 승인받고 끝까지 실행한다. 트리거: "단일세포 분석해줘", "scRNA-seq 분석", "/scrnaseq-plan-execute".
---

이 스킬은 매번 프롬프트를 복사-붙여넣기 하지 않고도 같은 형식의 분석을 시작할 수 있게
만든 것이다. **형식(Task/Objective/Dataset/Path 머리말, Rules R1–R6, 번호 붙은 단계,
step-validator 검증)은 고정**이지만, **내용(무엇을 묻고 어떤 데이터로 답할지)은 이 세션의
실제 연구 질문에 맞춰 채운다.** `scrnaseq-stepwise-hitl` 은 같은 형식에 진행 방식만
바꾼 짝이다 — 자율 실행 대신 단계별 개입을 원하면 그쪽을 쓴다. annotation·DEG 단계의
그림 규격은 `scrnaseq-visualization-spec` 스킬에 있다 (R6).

## 0. 작업 트리 준비

이 스킬은 자기 실험용 git worktree 를 **스스로 만들고 그 안으로 들어간다.** 사용자가
`setup.sh` 를 미리 실행해 두었을 필요가 없다. 순서는 이렇다.

```
연구 질문(Task) 확보 → worktree 생성·진입 → Dataset·Objective·Path → 계획
```

Task 를 먼저 받는 이유는 `EXPERIMENT.md` 의 목표 줄을 실제 연구 질문으로 채우기
위해서다. 나머지를 worktree 안에서 채우는 이유는 Path 와 `data/processed/` 가 처음부터
그 worktree 기준으로 잡히게 하기 위해서다.

1. **연구 질문을 확보한다.** 대화에 이미 나왔으면 그대로 쓰고, 없으면 먼저 묻는다.
   (이것이 1단계의 Task 다 — 여기서 받아 두고 1단계에서 다시 묻지 않는다.)
2. **세팅 스크립트를 실행한다.** 실험 이름은 이 스킬 이름을 따라 `plan-execute` 를
   기본값으로 쓴다. 사용자가 다른 이름을 줬으면 그 이름을 쓴다.

   ```bash
   ROOT="$(git worktree list --porcelain | sed -n '1s/^worktree //p')"
   bash "$ROOT/.claude/scripts/worktree_init.sh" plan-execute \
        --mode plan-execute --goal "<1에서 확보한 연구 질문>"
   ```

   이 스크립트가 공유 경로 심볼릭 링크 · `CLAUDE.md` · `.mcp.json` · `EXPERIMENT.md` 를
   모두 처리한다. 무엇을 공유하고 무엇을 실험마다 따로 두는지는 그 스크립트 안에
   주석으로 적혀 있다 — **여기서 git 명령을 직접 쓰지 않는다.**
3. **마지막 줄을 보고 분기한다.** 스크립트는 마지막 줄로 상태 하나를 출력한다.

   | 마지막 줄 | 해야 할 일 |
   |---|---|
   | `WORKTREE <경로>` | `EnterWorktree` 도구를 `path: <경로>` 로 호출해 세션을 그 안으로 옮긴다 |
   | `EXISTS <경로>` | 같은 이름의 실험이 이미 있다. 이어서 할지 다른 이름으로 새로 만들지 사용자에게 묻고, 이어서 하면 똑같이 `EnterWorktree` 로 진입한다 |
   | `ALREADY_IN_WORKTREE <경로>` | 이미 실험 worktree 안에서 세션이 떠 있다. 세팅도 진입도 하지 않고 그대로 1단계로 간다 |
   | exit 2 (커밋 안 된 변경) | 스크립트가 출력한 두 선택지(지금 커밋 / `--ignore-dirty`)를 사용자에게 그대로 제시하고 **답을 기다린다.** 스스로 커밋하지 않는다 |

   `EnterWorktree` 로 진입한 뒤에는 `pwd` 로 위치를 확인하고, 이후 모든 경로를 그
   worktree 기준으로 쓴다. 진입에 실패하면 사용자에게 `cd <경로> && claude` 로 새
   터미널에서 열어 달라고 안내하고 멈춘다.
4. **worktree 를 원하지 않는 경우.** 사용자가 "worktree 없이 여기서 그냥 하자"고 하면
   0단계를 건너뛰고 현재 디렉토리에서 진행한다. 이때는 결과가 main 작업 트리에 쌓이므로
   `scrnaseq-compare-experiments` 로 다른 실험과 비교할 수 없다는 점을 한 줄로 알린다.

병렬 비교를 하려면 터미널을 두 개 열고 각각 저장소 루트에서 `claude` 를 띄운 뒤,
한쪽에서 이 스킬을, 다른 쪽에서 `scrnaseq-stepwise-hitl` 을 부르면 된다 — 각 세션이
자기 worktree 를 만들어 들어간다.

## 0.5 전제 확인

worktree 안으로 들어온 뒤 `.claude/agents/step-validator.md` 가 있는지 확인한다. 없으면
사용자에게 알리고 계속할지 묻는다 — R4(단계별 검증 호출)를 못 지키게 된다.
`.claude/` 는 main 을 가리키는 심볼릭 링크이므로, 없다면 그 파일이 **git 에 커밋되지
않았다는 뜻**이다 (`link_shared.py` 가 `git ls-files` 로 공유 목록을 뽑는다). 같은 이유로
`data/genesets/` 나 참조 스킬이 비어 있을 수도 있으니, 없는 것은 없다고 알린다.

## 1. Task / Objective / Dataset / Path 를 채운다

**사용자의 연구 질문이 곧 Task 다.** 0단계에서 이미 받았으므로 그것을 그대로 쓴다.
그 다음 아래 순서로 나머지를 채운다 — 추측으로 채우지 않는다.

1. **Dataset**: 코드베이스를 탐색한다 (`data/`, `data/processed/`, `*.h5ad` 글롭,
   `EXPERIMENT.md`, 최근 커밋 메시지). `.h5ad` 를 찾으면 `obs` 컬럼, `.X` 가 raw count 인지,
   세포/유전자 수를 실제로 읽어 확인한다 — 짐작해서 적지 않는다. 후보가 여럿이거나
   하나도 없으면 사용자에게 묻는다.
2. **Objective**: Task(연구 질문)를 "유전자 수준" / "경로·전사인자 수준" 처럼 어떤 축에서
   답할 것인지로 한 단계 구체화한다. 이 프로젝트의 스타일을 따라 1–2문장으로 적는다.
3. **Path**: 입력 데이터 경로, 참조 자료(`data/genesets/`, `core_markers.xlsx` 같은 검증용
   파일이 있으면), 작업 디렉토리(0단계에서 진입한 worktree)를 채운다.
   참조 자료가 이 프로젝트에 없으면 그 줄은 뺀다 — 없는 파일을 있는 것처럼 적지 않는다.
4. 네 항목을 표로 사용자에게 보여주고 **맞는지 확인받는다.** 여기서 틀리면 아래 8단계
   전체가 잘못된 데이터/질문에 답하게 된다.

## 2. 8단계 분석 계획을 이 연구 질문에 맞게 조립한다

아래 구조(QC → 정규화/HVG → 배치 통합 → clustering → annotation → 조건 간 차등발현 →
조건 간 기능 분석 → REPORT)는 이 저장소의 **PBMC IFN-beta 자극** 데이터셋을 예시로 삼아
정리된 것이다. 조건 비교가 들어간 scRNA-seq 분석이면 대체로 재사용 가능하지만,
**조건·유전자·마커 이름은 이 Dataset 에 맞게 다시 채운다.** 기계적으로 복사하지 않는다.

- Dataset 의 `obs` 에 조건 변수가 있는가 (예시의 `stim`/`ctrl` 에 대응하는 것). 없다면
  3·6·7 단계에서 "조건 간" 이라는 틀 자체가 안 맞을 수 있다 — 그때는 무엇을 비교하는
  구조인지 사용자와 먼저 정한다.
- 3.2 의 원칙(**관심 조건을 통계 검정의 batch_key 로 지우지 않는다. 단, clustering/
  annotation 목적이라면 조건에 따른 표현형 이동을 보정하는 것은 맞는 선택일 수 있다** —
  `.claude/agents/step-validator.md` 의 배치 통합 채점 기준과 같은 원칙이다)은 조건
  변수의 이름이 바뀌어도 그대로 유지한다.
- 7 단계(기능 분석)는 `data/genesets/` 나 그에 준하는 gene set 자료가 이 프로젝트에
  없으면 통째로 뺀다 — 없는 자료를 있다고 가정한 단계를 넣지 않는다.
- 5.4 의 "기대되는 주요 타입" 목록은 이 Dataset 의 조직/세포 종류에 맞게 다시 정한다
  (PBMC 가 아니면 CD4 T/CD8 T/B/NK/... 목록이 안 맞는다).
- 7.5 같은 "양성 대조" 항목은 이 자극/조건에 대해 통용되는 마커/경로로 바꾼다. 무엇이
  양성 대조인지 모르면 사용자에게 묻거나, 모른다고 적고 단계를 뺀다.
- 5단계(annotation)는 marker 점수 최댓값 할당이 아니라 **celltypist** 로 수행하고,
  6·7단계(DEG·기능분석)의 그림은 `scrnaseq-visualization-spec` 스킬의 규격(celltype DEG
  패널·조건 DEG 패널을 서로 다른 임베딩 위에 그리는 것 등)을 따른다 — R6 참고.

## 3. Rules 는 그대로 가져간다

R1–R6 는 방법론이 아니라 **진행 방식**이므로 고정이다.

```
R1  전체 계획을 체크박스 목록으로 먼저 보여주고 승인을 받는다.
    승인 후에는 묻지 않고 끝까지 실행하며, 한 단계를 끝낼 때마다 목록을 갱신한다.
    계획을 벗어나야 하면 멈추지 말고 [✗] 와 이유를 적은 뒤 수정된 단계를 넣고 간다.
R2  판단이 갈리는 지점을 만나면 스스로 정하고, 무엇을 왜 골랐는지와 고르지 않은 대안을
    EXPERIMENT.md 결정 로그와 metrics.json 의 decisions 에 항목 번호와 함께 남긴다.
R3  수치를 지어내지 않는다. 없으면 없다고 적는다. 추정치를 실측치처럼 쓰지 않는다.
    단계마다 무엇을 했고 어떤 값이 나왔는지 print 한다. 그림은 절대 경로를 print 한다.
R4  각 단계가 끝나면 step-validator 서브에이전트를 부른다.
    결과를 results/validation/<번호>_<단계>.md 에 저장하고 metrics.json 에 점수를 누적한다.
    FAIL 이면 다음으로 가지 말고 고친 뒤 다시 검증한다.
R5  기능 분석(GSEA·pathway) 단계가 있다면 코드를 짜기 전에 `decoupler-cheatsheet`
    스킬을 읽는다 — 이 환경의 decoupler 는 2.x 이고 1.x 와 함수 이름이 다르다.
R6  annotation·DEG·기능분석 단계의 그림을 그리기 전에 `scrnaseq-visualization-spec`
    스킬을 읽는다. annotation 은 celltypist 로 수행하고 cluster marker dotplot으로
    분리도를 검증하며, DEG 그림은 celltype DEG 패널(post-integration UMAP + scatter)과
    조건 DEG 패널(pre-integration UMAP + volcano)을 구분해서 그린다. 기능 분석은
    pathway 활성 scatter(비보정 UMAP)와 ctrl/stim 구분 stacked violin을 추가로 그리고,
    그림 텍스트에 한글 폰트 깨짐이 없게 한다.
```

`metrics.json` 키는 `metrics_template.json` 이 저장소 루트에 있으면 그 이름을 그대로 쓴다.
없으면 이 규칙을 계획에서 빼고 사용자에게 알린다.

## 4. 계획을 세우고 승인받는다

1–3에서 채운 Task/Objective/Dataset/Path/Rules/번호 단계를 합쳐 R1 형식의
**체크박스 실행 계획**으로 사용자에게 보여준다. 각 단계에서 스스로 정해야 하는 판단이
무엇이고 어떤 선택지가 있는지도 계획에 같이 적는다. **여기서 실행을 시작하지 않는다.**

계획을 보여줄 때, 결과를 가장 크게 좌우하는 지점(배치 통합의 batch_key 선택,
resolution 선택 근거, pseudobulk 표본 단위, 조건 대비를 위한 표/heatmap 구성 등)을
따로 짚어서 사용자가 검토하기 쉽게 한다.

## 5. 승인 후 실행

승인을 받으면 그 다음부터는 묻지 않고 끝까지 실행한다. 각 단계가 끝날 때마다:

1. 체크박스 목록을 갱신한다 (계획을 벗어났으면 `[✗]` 와 이유, 수정된 단계를 넣는다).
2. `step-validator` 서브에이전트를 호출해 그 단계를 채점한다 (Agent 도구, R4).
3. FAIL 이면 멈추고 고친 뒤 다시 검증한다. WARN 이면 이유를 적고 계속한다.

## 6. 끝났을 때

`results/summary/metrics.json` 과 `EXPERIMENT.md` 결정 로그가 채워졌는지 확인하고
빠진 항목을 채운다. 그 다음 아래를 표로 정리해서 사용자에게 보여준다.

1. 스스로 정한 판단들 — 항목 번호 · 무엇을 골랐나 · 고르지 않은 대안
2. 단계별 검증 점수(정확성·완결성)와 WARN 으로 남겨 둔 것, 왜 고치지 않았는지
3. (기능 분석을 했다면) 어떤 선택이 결과를 가장 크게 바꿨는지
