# 2일차 2교시 실습 — 아이디어 둘을 동시에 돌리고 비교하기

> 약 50분 · **1교시에 쓰던 그 Codespace 그대로**입니다. 새로 만들 것이 없습니다.
> 아래 명령은 특별한 말이 없으면 **저장소 루트**(`/workspaces/ajou-omics-env`)에서 실행합니다.

연구를 하다 보면 한 목표를 두고 시험해 보고 싶은 방식이 여러 개 있습니다.
보통은 하나를 고르고, 나머지는 "나중에" 로 미룹니다.

오늘은 **둘 다 돌립니다. 동시에.** 그리고 무엇이 갈렸는지 봅니다.

| | 실험 | branch | 진행 방식 |
|---|---|---|---|
| **A** | `plan-execute` | `exp/plan-execute` | 계획을 먼저 세우고 한 번 승인받은 뒤 **끝까지 자율 실행** |
| **B** | `stepwise-hitl` | `exp/stepwise-hitl` | 한 단계씩 가고 갈림길마다 **멈춰서 사람에게 물음** |

**데이터도 같고 질문도 같습니다.** 다른 것은 진행 방식뿐입니다.

---

## 0. 왜 worktree 인가 · 2분

같은 저장소에서 두 분석을 동시에 돌리면 `results/` 가 서로 덮어씁니다.
`git checkout` 으로 오가면 한 번에 하나밖에 못 봅니다.

`git worktree` 는 **branch 하나마다 디렉토리 하나**를 줍니다.
`.git` 은 하나를 같이 쓰고, 작업 폴더만 따로 생깁니다.

```
/workspaces/ajou-omics-env/        ← main · 여기서 비교한다
├── data/raw/  mcp_lab/            공용 — 실험들이 나눠 쓴다
├── comparison/                     비교 결과가 여기 쌓인다
└── worktrees/
    ├── plan-execute/               ← 세션 A 가 사는 곳
    │   ├── data/raw/ → 공유         (심볼릭 링크)
    │   ├── data/processed/          이 실험의 중간 데이터
    │   ├── scripts/  results/  figures/
    │   └── EXPERIMENT.md
    └── stepwise-hitl/              ← 세션 B 가 사는 곳
        └── (같은 구조 · 완전히 별개)
```

**두 실험의 `results/` 는 서로 다른 디렉토리입니다.** 부딪히지 않습니다.

### 나눠 쓰는 것과 따로 갖는 것

`setup.sh` 는 저장소를 통째로 복사하지 않습니다. **실험이 만들지 않는 것은 공유**합니다.

| | 무엇 | 왜 |
|---|---|---|
| **공유** (심볼릭 링크) | `data/raw/` · `mcp_lab/` · `parallel_lab/` · `.devcontainer/` · `core_markers.xlsx` | 실험이 읽기만 하는 공용 입력·도구. 복사하면 55MB 씩 늘어날 뿐입니다 |
| **따로** (실물) | `scripts/` · `notebooks/` · `data/processed/` · `results/` · `figures/` · `EXPERIMENT.md` | 실험이 **만드는** 것. 섞이면 안 됩니다 |

`data/processed/` 가 따로인 이유는 여기가 QC·정규화 중간 데이터가 쌓이는 곳이기 때문입니다.
공유했다면 두 실험이 서로의 중간 파일을 덮어썼을 겁니다.

worktree 하나가 17MB 입니다. 통째로 복사했다면 73MB 였습니다.

```bash
ls -l worktrees/plan-execute/data/raw/ | head -3     # → 화살표가 보입니다
ls -l worktrees/plan-execute/data/processed/         # → 실물입니다
```

> **화살표(`→`)가 붙은 파일에는 쓰지 마세요.** main 과 옆 실험까지 같이 바뀝니다.
> 읽기 전용 입력이라 실제로 쓸 일은 없습니다.

---

## 1. 실험 두 개 만들기 · 5분

먼저 1일차·1교시 작업을 커밋합니다. worktree 는 **마지막 커밋을 출발점**으로 삼기 때문입니다.

```bash
git add -A && git commit -m "병렬 실험 출발점"
```

```bash
bash parallel_lab/setup.sh
```

```
✓ worktrees/plan-execute    (branch exp/plan-execute ← main)
✓ worktrees/stepwise-hitl   (branch exp/stepwise-hitl ← main)
```

각 worktree 안에 세 가지가 준비됩니다.

| | |
|---|---|
| `CLAUDE.md` | 공통 지침 **+ 이 실험의 진행 방식** 이 덧붙어 있습니다 |
| `EXPERIMENT.md` | 아이디어 · **결정 로그** · 진행 체크리스트 |
| `.mcp.json` | 1교시에서 붙인 MCP 서버가 그대로 따라옵니다 |

`worktrees/plan-execute/CLAUDE.md` 를 열어 **맨 아래**를 한 번 보세요.
세션 B 의 것과 비교해 보면, 오늘 바뀌는 게 정확히 무엇인지 한눈에 보입니다.

---

## 2. 세션 A 를 띄웁니다 · 10분

VS Code 에서 터미널을 하나 엽니다.

```bash
cd worktrees/plan-execute && claude
```

여는 프롬프트는 [prompts/01_plan-execute.md](prompts/01_plan-execute.md) 에 있습니다. 붙여 넣으세요.

계획이 나오면 읽고 승인합니다.

```
좋아. 이대로 진행해.
```

### ★ 여기서 기다리지 마세요

실행이 도는 채로 **그냥 두고 다음으로 넘어갑니다.**
VS Code 터미널 패널의 `+` 로 **새 터미널**을 엽니다. (`⌃⇧5` 로 화면을 나란히 쪼갤 수 있습니다)

---

## 3. 세션 B 를 띄웁니다 · 20분

새 터미널에서:

```bash
cd worktrees/stepwise-hitl && claude
```

여는 프롬프트는 [prompts/02_stepwise-hitl.md](prompts/02_stepwise-hitl.md) 입니다.

이제 **왼쪽에서는 A 가 혼자 돌고, 오른쪽에서는 B 가 나에게 묻습니다.**

B 는 단계마다 멈추고 선택지를 줍니다. 고르기 전에 되물어 보세요.

```
2번을 고르면 뒤 단계에서 뭐가 달라져?
```

고른 다음:

```
2번으로 가자. 그리고 이 결정 EXPERIMENT.md 에 남겨줘 — 내가 골랐다고.
```

### ★ 3단계, 배치 통합에서 한 번 멈추세요

`stim` 을 배치로 보고 보정하면 **보려던 조건 효과가 같이 지워질 수 있습니다.**
A 는 이 갈림길에서 혼자 결정했습니다. B 에서는 여러분이 결정합니다.

**두 실험이 여기서 갈릴 가능성이 가장 높습니다.**

### 중간에 A 를 확인하고 싶으면

세 번째 터미널에서:

```bash
bash parallel_lab/status.sh
```

```
실험           단계        체크  세포수  클러스터  세포타입  결정(사람/전체)  산출물  report
------------------------------------------------------------------------------------------
plan-execute   deg         6/8   11240   11        8         0/7              24      있음
stepwise-hitl  clustering  4/8   11402   9         -         5/6              11      -
```

**`결정(사람/전체)` 열을 보세요.** 같은 분석인데 결정한 사람이 다릅니다.

---

## 4. 비교합니다 · 12분

A 가 끝났으면 (`status.sh` 의 `report` 가 `있음`), **저장소 루트**에서 세 번째 세션을 띄웁니다.

```bash
cd /workspaces/ajou-omics-env && claude
```

프롬프트는 [prompts/03_compare.md](prompts/03_compare.md) 입니다.

`comparison/comparison_report.html` 이 만들어지면 VS Code 에서 열어 보세요.
(파일 우클릭 → `Open with Live Preview`, 없으면 `Open Preview`)

### 이걸 보게 됩니다

| | |
|---|---|
| 같은 데이터인데 | 세포 수 · 클러스터 수 · 세포 타입 수가 다릅니다 |
| 같은 질문인데 | DEG 개수와 상위 유전자가 다릅니다 |
| 어디서 갈렸나 | 대개 **QC 컷오프**와 **배치 보정 여부** 두 군데입니다 |
| 누가 결정했나 | A 는 거의 전부 `claude`, B 는 절반 이상 `human` |

---

## 5. 이게 왜 중요한가 · 3분

오늘 한 것은 "두 가지 대화 방식 비교" 가 아닙니다.

> **아이디어 하나당 branch 하나, worktree 하나, 세션 하나.**
> 시험해 보고 싶은 게 셋이면 셋을 동시에 돌리고 마지막에 비교하면 됩니다.

`setup.sh` 는 이름을 주면 그대로 만들어 줍니다.

```bash
bash parallel_lab/setup.sh harmony-integration scvi-integration no-integration
```

```
✓ worktrees/harmony-integration    (branch exp/harmony-integration ← main)
✓ worktrees/scvi-integration       (branch exp/scvi-integration ← main)
✓ worktrees/no-integration         (branch exp/no-integration ← main)
```

이름을 준 실험은 진행 방식이 비어 있습니다. 각 `EXPERIMENT.md` 의 **아이디어** 칸을
채우고 시작하면 됩니다. 비교하는 방법은 오늘과 똑같습니다.

### 오늘 남길 네 가지

1. **worktree 하나 = 실험 하나.** 공용 입력은 나눠 쓰고, 실험이 만드는 것만 갈라집니다
2. **비교하려면 미리 약속해 둬야 합니다.** `results/summary/metrics.json` 이 그 약속입니다
3. **결정을 기록해야 비교가 됩니다.** 결과만 놓고는 왜 갈렸는지 알 수 없습니다
4. **자율 실행은 빠르고, 개입은 방향을 잡습니다.** 어느 한쪽이 정답이 아닙니다

---

## 정리하기

worktree 를 지우면 그 안의 `results/` 도 같이 사라집니다. `comparison/` 은 남습니다.

```bash
bash parallel_lab/cleanup.sh          # 무엇이 지워지는지 보여주기만
bash parallel_lab/cleanup.sh --yes    # 실제로 지움
```

**남기고 싶은 그림이 있으면 먼저 `comparison/` 으로 복사하세요.**

---

## 안 될 때

| 증상 | 해볼 것 |
|---|---|
| `setup.sh` 가 "커밋되지 않은 변경" 이라며 멈춘다 | 화면의 두 선택지 중 하나. 보통 `git add -A && git commit` |
| `fatal: '...' is already checked out` | 그 branch 를 이미 쓰는 worktree 가 있습니다. `git worktree list` |
| worktree 안에서 Claude 가 다른 실험을 들여다본다 | `CLAUDE.md` 맨 아래 블록이 붙어 있는지 확인 |
| worktree 안에 `data/` 가 없다 | 커밋 전에 만들어졌습니다. 지우고 `setup.sh` 다시 |
| `data/raw/` 파일이 깨졌다 | 링크에 덮어썼습니다. `git checkout data/raw` 로 main 에서 복구 |
| worktree 에서 `/mcp` 가 failed | 1교시에 만든 `mcp_lab/meeting.py` 를 커밋하지 않았습니다. main 에서 커밋하고 `setup.sh` 다시 |
| 디스크가 모자란다 | worktree 하나당 17MB 입니다. 실험 개수를 줄이세요 |
| 두 세션이 같은 파일을 고친다 | 있을 수 없습니다. 경로를 확인하세요 — 둘 다 `worktrees/` 밖에 있으면 잘못된 것입니다 |
| 전부 되돌리고 싶다 | `bash parallel_lab/cleanup.sh --yes` |
