single_cell_project/
├── data/
│   ├── raw/
│   ├── genesets/
│   └── processed/
│
├── scripts/
│
├── notebooks/
│
├── results/
│   ├── qc/
│   ├── doublet/
│   ├── clustering/
│   ├── annotation/
│   ├── deg/
│   ├── functional/
│   ├── condition_analysis/
│   └── summary/
│
├── figures/
│   ├── qc/
│   ├── clustering/
│   ├── annotation/
│   ├── deg/
│   └── functional/
│
├── config/
│
├── EXPERIMENT.md
│
├── worktrees/
│
├── comparison/
│
└── README.md

이 디렉토리 구조는 프로젝트의 기본적인 조직 원칙을 나타낸다. 파일명, 파일 개수, 분석 스크립트나 노트북의 분할 방식은 고정하지 않는다.

분석 목적과 복잡도에 따라 필요한 파일을 자유롭게 생성·통합·분리할 수 있으며, 사용하지 않는 디렉토리를 형식적으로 채울 필요는 없다.

data/raw/: 원본 데이터. 가능하면 수정하지 않는다.
data/genesets/: 기능 분석용 prior knowledge(gene set·footprint) 캐시. 공용 입력이므로 읽기만 한다.
data/processed/: QC, preprocessing, annotation 등 분석 과정에서 생성되는 재사용 가능한 중간 데이터.
scripts/: 재현 가능하고 반복 실행할 분석 코드. 필요에 따라 하나 또는 여러 파일로 구성한다.
notebooks/: 데이터 탐색, 분석 과정 확인, 시각적 검토, 가설 검증, 결과 해석 등을 위한 interactive analysis 공간. 모든 분석을 반드시 notebook으로 작성할 필요는 없으며, 안정화된 로직은 필요에 따라 scripts/로 옮길 수 있다.
results/qc/: QC 통계, 필터링 결과 등.
results/doublet/: doublet detection 관련 결과.
results/clustering/: 차원 축소, neighborhood graph, clustering 등 세포 구조 분석 결과.
results/annotation/: marker 분석, cell-type annotation 및 annotation 검증 결과.
results/deg/: differential expression 분석 결과.
results/functional/: gene set enrichment, pathway·transcription factor 활성 추정 등 기능 분석 결과. 어떤 prior knowledge(gene set·footprint)와 어떤 통계 방법을 썼는지를 결과 파일이나 metrics.json에 함께 남긴다. 이 기록이 없으면 결과를 재현할 수 없다.
results/condition_analysis/: treatment, disease, stimulation 등 condition 간 비교 분석 결과.
results/summary/: 이 작업 트리 전체의 요약 산출물. metrics.json과 report.html이 여기에 놓인다. 다른 실험과 비교할 때 읽는 위치이므로 파일명을 임의로 바꾸지 않는다.
figures/: 분석 과정에서 생성한 주요 시각화. 필요한 경우 목적에 맞는 하위 디렉토리를 자유롭게 추가한다.
config/: 분석 파라미터나 설정 파일이 필요한 경우 사용한다.
EXPERIMENT.md: 이 작업 트리가 하나의 실험일 때만 존재한다. 실험의 아이디어, 진행 방식, 결정 로그를 담는다.
worktrees/: 병렬 실험용 git worktree가 놓이는 자리. main 작업 트리에만 존재하며 git으로 추적하지 않는다.
comparison/: 여러 실험을 비교한 결과. main 작업 트리에서만 생성한다.
README.md: 데이터, 분석 목적, 주요 분석 과정과 결과를 설명한다.

새로운 분석 단계가 필요하면 기존 구조에 억지로 맞추지 말고 적절한 디렉토리나 하위 디렉토리를 추가할 수 있다.

디렉토리 구조는 고정된 분석 workflow가 아니라 각 산출물의 역할과 저장 위치를 정의하기 위한 기준으로 사용한다.

필요한 최소한의 파일만 생성하며, 단순히 디렉토리 구조를 채우기 위한 파일은 만들지 않는다.

분석의 주요 단계가 완료되면 현재까지의 분석 과정, 핵심 결과, 주요 시각화, 해석 및 다음 분석 후보를 정리한 HTML report를 results/summary/report.html로 생성한다.

HTML report 생성 작업은 가능하면 메인 대화/작업 세션을 점유하지 않도록 별도의 background process로 실행한다. 사용자는 report가 생성되는 동안에도 같은 세션에서 추가 질문, 분석 수정, 후속 요청을 계속할 수 있어야 한다.

Report 생성 때문에 분석 세션을 종료하거나 사용자의 추가 입력을 기다리게 하지 않는다. Report 생성에 시간이 걸리는 경우에도 기존 interactive session을 계속 사용할 수 있도록 작업을 분리한다.

새로운 분석 요청이 들어오면 기존 report 생성을 기다리지 말고 가능한 범위에서 분석을 계속 진행한다. 이후 분석 결과가 변경되거나 추가되면 필요에 따라 report를 갱신하거나 새 버전을 생성한다.

data/genesets/는 기능 분석에 쓰는 prior knowledge(gene set·footprint) 캐시다. 읽기만 하고 쓰지 않는다. 새 자원이 필요하면 fetch_genesets.py로 받아 캐시에 더한다. 분석 코드 안에서 매번 원격으로 내려받지 않는다 — 원격 자원은 조용히 바뀌고, 그러면 같은 코드가 다른 결과를 낸다.

이 환경의 decoupler는 2.x다. dc.mt.* / dc.op.* / dc.pp.* / dc.pl.* / dc.tl.* 를 쓴다. dc.run_ulm, dc.get_progeny, dc.get_pseudobulk 같은 1.x 함수는 존재하지 않는다. 기능 분석 코드를 작성하기 전에 decoupler-cheatsheet 스킬을 먼저 읽는다.

core_markers.xlsx는 celltype별 핵심 marker 목록을 담고 있는 참조 파일이다. 사용자의 명시적인 지시가 있거나 annotation 결과를 검증하는 단계가 아닌 이상 이 파일을 사용하지 않는다.

skill을 작성하거나 분석 결과에 대한 근거를 설명할 때는 항상 한글로 작성한다.

코드를 작성해야 할 때는 기본적으로 notebooks/에 새 노트북을 추가하지 말고 scripts/ 안에 script 파일로 작성한다. notebooks/는 탐색적 분석, 시각적 검토, 결과 해석 등 interactive한 용도로만 사용자가 명시적으로 요청했을 때 사용한다.


## 병렬 실험 (git worktree)

하나의 연구 목표에 대해 서로 다른 아이디어나 진행 방식을 동시에 시험하기 위해, 각 실험을 별도의 branch와 git worktree에서 독립적으로 수행하고 마지막에 비교한다.

### 지금 어느 작업 트리에 있는지 먼저 판단한다

저장소 루트에 EXPERIMENT.md가 있으면 이 작업 트리는 **실험 작업 트리**다. 없으면 **main 작업 트리**다. 세션을 시작할 때 이것을 먼저 확인하고, 아래의 해당 규칙을 따른다.

### 실험 작업 트리에서 지키는 것

작업 범위는 이 작업 트리 안으로 제한한다. 다른 실험의 디렉토리를 읽거나 쓰지 않고, worktrees/나 comparison/을 만들지 않는다. 다른 실험이 무엇을 하고 있는지 궁금하더라도 들여다보지 않는다. 실험 사이의 독립성이 비교의 전제다.

이 작업 트리 안에서 심볼릭 링크로 걸린 경로는 main과 공유되는 공용 파일이다. data/raw/, data/genesets/, agent_lab/, .devcontainer/, .claude/, core_markers.xlsx, setup.sh·status.sh·cleanup.sh·verify.py·fetch_genesets.py·link_shared.py·metrics_template.json, .venv/가 여기에 해당한다. 읽기만 하고 쓰거나 지우거나 이름을 바꾸지 않는다. 링크를 통해 쓰면 main과 다른 실험의 파일까지 함께 바뀐다. 어떤 경로가 링크인지 확실하지 않으면 ls -l로 확인한다. .venv/는 다른 경로들과 달리 git 이 추적하지 않는 gitignore 대상이라 link_shared.py 목록이 아니라 worktree_init.sh 가 별도 블록에서 심볼릭 링크로 건다 — 실험마다 패키지를 새로 설치하지 않고 main의 Python 환경을 그대로 쓴다.

data/processed/는 공유하지 않는다. 이 작업 트리만의 실물 디렉토리이므로 분석 중간 데이터는 평소대로 여기에 쓴다.

branch를 옮기거나(checkout, switch) merge, rebase, 다른 worktree 제거를 하지 않는다. 사용자가 명시적으로 지시할 때만 한다.

EXPERIMENT.md의 결정 로그를 계속 갱신한다. 분석 과정에서 판단이 갈리는 지점(필터링 기준, 정규화 방식, batch 보정 여부, clustering resolution, marker 선택, 통계 방법 등)을 만날 때마다 무엇을 골랐는지, 왜 골랐는지, 그리고 그 선택을 누가 했는지(claude / human)를 기록한다.

주요 단계가 끝날 때마다 results/summary/metrics.json을 갱신한다. 이 파일은 실험 사이를 비교하기 위한 공통 산출물이므로 정해진 키 이름을 바꾸지 않는다. 필요한 항목은 추가할 수 있지만 기존 키를 삭제하거나 이름을 바꾸지 않는다. 형식은 저장소 루트의 metrics_template.json을 따른다.

같은 목표를 다루더라도 다른 실험의 결과에 맞추려 하지 않는다. 결과가 갈리는 것 자체가 관찰 대상이다.

### main 작업 트리에서 지키는 것

main에서는 분석을 직접 실행하지 않는다. worktrees/ 아래 각 실험의 EXPERIMENT.md, results/summary/metrics.json, results/, figures/를 읽어 비교하는 일만 한다.

비교 결과는 comparison/에 쓴다. 각 실험 작업 트리의 파일은 수정하지 않는다.

비교할 때는 결과만 보지 않는다. 어떤 결정이 결과의 차이를 만들었는지, 그 결정을 누가 했는지(claude / human), 두 실험이 갈라진 지점이 어디인지를 함께 정리한다. 결론을 내리기 어려운 항목은 "어느 쪽이 옳은지 이 데이터로는 판단할 수 없다"고 명시한다.

비교 리포트는 comparison/comparison_report.html로 생성하고, 같은 내용의 요약을 comparison/comparison.md에도 남긴다.
