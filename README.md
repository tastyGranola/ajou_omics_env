# IFN-beta 자극에 대한 면역세포 반응 분석 실습 환경

> **연구 질문** — IFN-beta 자극을 받은 말초혈액 면역세포(PBMC)는 세포 타입별로 어떻게 다르게 반응하는가?

GitHub Codespaces 에서 클릭 몇 번으로 single-cell RNA-seq 분석 환경이 그대로 열리도록 구성한
실습용 저장소입니다. 설치 과정 없이 바로 데이터 분석부터 시작할 수 있습니다.

## 시작하기

1. 이 저장소 상단의 **Code ▸ Codespaces ▸ Create codespace on main** 클릭
2. 컨테이너가 만들어지고 패키지가 설치될 때까지 기다립니다 (최초 1회, 3~5분)
3. 터미널에 `✅ 환경 준비 완료` 가 뜨면 `notebooks/00_smoke_test.ipynb` 를 열어 데이터가
   잘 로드되는지 확인합니다

VS Code 화면은 어두운 테마(Default Dark Modern)로 설정되어 있고,
**Claude Code 확장**이 미리 설치되어 있어 사이드바에서 바로 사용할 수 있습니다.
터미널에서 `claude` 명령으로도 실행됩니다. (최초 실행 시 Anthropic 계정 로그인이 필요합니다)

## 데이터

| 항목 | 내용 |
|---|---|
| 출처 | [GSE96583](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE96583) — Kang et al., *Nat Biotechnol* 2018 (demuxlet 논문) |
| 사용 범위 | batch2 — 대조군(GSM2560248) / IFN-beta 자극군(GSM2560249) |
| 설계 | 루푸스 환자 8명의 PBMC, 조건당 8명 pooling 후 demuxlet 으로 공여자 판별 |
| 파일 | `data/processed/gse96583_ifnb.h5ad` (11,998 세포 × 14,391 유전자, 18 MB) |

`.X` 에는 **정규화하지 않은 raw count** 가 들어 있습니다. QC · 정규화 · HVG 선별 · 통합 ·
클러스터링 · 차등발현은 실습에서 직접 수행할 부분이라 일부러 처리하지 않았습니다.

**미리 처리해 둔 것**

- demuxlet 이 doublet(3,169) / ambiguous(1,217) 로 판정한 세포 **제거 완료**
- 세포 타입이 할당되지 않은 세포 제거
- (조건 × 세포타입) 층화 다운샘플로 약 12,000 세포까지 축소 — 무료 Codespace 사양에서도 원활히 동작
- 3개 미만의 세포에서만 검출되는 유전자 제거

**일부러 넣지 않은 것**

- **세포 타입 주석** — 원 논문 저자들이 붙여 둔 세포 타입 라벨은 결과 파일에서 제외했습니다.
  클러스터링과 마커 유전자로 직접 주석을 붙이는 것이 실습의 핵심 과정이기 때문입니다.
  (층화 다운샘플 단계에서 세포 타입 구성 비율을 맞추는 데에만 내부적으로 사용했습니다)
- 정규화, HVG 선별, 배치 통합, 차원축소, 클러스터링 결과

**`obs` 컬럼**

| 컬럼 | 설명 |
|---|---|
| `stim` | `ctrl` (대조군) / `stim` (IFN-beta 자극) |
| `donor` | 공여자 ID (demuxlet 판별 결과) |
| `total_counts`, `n_genes` | 기본 QC 지표 |

> 참고 — 이 데이터는 유전자 목록에 미토콘드리아 유전자(`MT-`) 13개가 있지만 count 가 전부 0 입니다
> (원 저자가 미토콘드리아 리드를 제외함). 따라서 미토콘드리아 비율 기반 QC 는 적용할 수 없고,
> `total_counts` 와 `n_genes` 로 QC 를 진행합니다.

### 데이터 재생성

```bash
python scripts/prepare_data.py                   # 기본값: 12,000 세포, 세포 타입 주석 제외
python scripts/prepare_data.py --n-cells 24000   # 다운샘플 없이 singlet 전체 (약 36 MB)
python scripts/prepare_data.py --with-cell-type  # 강사용: 원 저자 세포 타입 주석 포함본
```

`--with-cell-type` 은 `gse96583_ifnb_with_celltype.h5ad` 로 따로 저장되며 git 에 포함되지
않습니다. 수강생 주석 결과를 원 논문과 비교할 때 사용하세요.

GEO 원본 파일도 `data/raw/` 에 함께 포함되어 있어, 네트워크 다운로드 없이 전처리 과정을
그대로 재현할 수 있습니다. (스크립트는 파일이 이미 있으면 다운로드를 건너뜁니다)

| 파일 | 내용 |
|---|---|
| `GSM2560248_2.1.mtx.gz`, `GSM2560248_barcodes.tsv.gz` | 대조군 count matrix / 바코드 |
| `GSM2560249_2.2.mtx.gz`, `GSM2560249_barcodes.tsv.gz` | IFN-beta 자극군 count matrix / 바코드 |
| `GSE96583_batch2.genes.tsv.gz` | 유전자 목록 (Ensembl ID + symbol) |
| `GSE96583_batch2.total.tsne.df.tsv.gz` | 세포 주석 (공여자, 조건, demuxlet singlet/doublet 판정, 원 저자 세포 타입) |

> 이 주석 파일에는 원 저자의 세포 타입 라벨이 그대로 들어 있습니다 (GEO 원본이라 손대지 않았습니다).
> 실습 중 정답을 미리 보지 않으려면 열어보지 마세요.

## 저장소 구조

```
.devcontainer/
  devcontainer.json     Codespace 정의 (이미지, 확장, 테마, 머신 사양)
  requirements.txt      설치되는 분석 패키지 + MCP 패키지 목록
  tools.txt             uvx 로 미리 받아둘 MCP 서버 목록
  post-create.sh        최초 생성 시 실행되는 설치·점검 스크립트
.mcp.json               MCP 서버 등록 파일 — 2일차 실습에서 직접 채웁니다
data/raw/               GEO 원본 파일 (mtx, barcodes, genes, 세포 주석)
data/genesets/          기능 분석용 gene set · footprint 캐시 (fetch_genesets.py 가 만듭니다)
data/processed/         전처리된 실습용 h5ad
notebooks/              실습 노트북
scripts/prepare_data.py 원본 데이터 → 실습용 데이터 변환 스크립트
agent_lab/              2일차 1교시 MCP · SKILL 실습 (LAB.md 부터 보세요)
.claude/skills/         scRNA-seq 분석·비교 스킬 (scrnaseq-plan-execute 등)
.claude/agents/         step-validator — 단계별 채점 서브에이전트
.claude/scripts/        worktree_init.sh — 실험 worktree 세팅 (스킬이 부릅니다)
setup.sh                실험 worktree 를 이름 목록으로 여러 개 미리 생성
status.sh               병렬 실험 진행 상황 표
cleanup.sh              worktree 정리
verify.py               환경 점검 (패키지 · gene set 캐시 · 입력 데이터)
fetch_genesets.py       gene set · footprint 를 data/genesets/ 에 캐시
metrics_template.json   실험 간 비교용 metrics.json 스키마
worktrees/              병렬 실험용 worktree — 스킬이 알아서 만듭니다 (git 추적 안 함)
comparison/             여러 실험을 비교한 결과
CLAUDE.example.md       Claude Code 용 프로젝트 지침 — cp CLAUDE.example.md CLAUDE.md
```

## 2일차 1교시 — MCP · SKILL 실습

같은 Codespace 에서 이어집니다. **새로 만들 것이 없습니다.**

```bash
python3 agent_lab/verify.py     # 환경 점검 (Codespace 생성 시 이미 한 번 돕니다)
```

안내서는 [agent_lab/LAB.md](agent_lab/LAB.md) 입니다.
안 될 때는 `bash agent_lab/doctor.sh` 로 진단합니다.

## 병렬 실험 — 같은 질문을 서로 다른 진행 방식으로

한 연구 질문을 두고 **서로 다른 진행 방식을 동시에** 돌려 보고 비교할 수 있습니다.
`git worktree` 로 branch 마다 작업 폴더를 따로 만들어, 여러 Claude 세션이 같은
저장소에서 서로 부딪히지 않고 나란히 분석합니다.

분석 자체는 `.claude/skills/` 의 스킬로 시작합니다 — 프롬프트를 복사-붙여넣기 하지 않습니다.

| 스킬 | 진행 방식 |
|---|---|
| `scrnaseq-plan-execute` | 계획을 먼저 세우고 승인 후 끝까지 자율 실행 |
| `scrnaseq-stepwise-hitl` | 한 단계씩 가고 갈림길마다 사람에게 물음 |
| `scrnaseq-compare-experiments` | worktrees/ 아래 여러 실험을 비교 (저장소 루트에서 실행) |

**worktree 를 직접 만들지 않습니다.** 스킬이 자기 실험용 worktree 를 만들고 그 안으로
들어갑니다. 터미널 두 개를 열고 각각 **저장소 루트**에서 `claude` 를 띄운 뒤, 한쪽에서
`/scrnaseq-plan-execute` 를, 다른 쪽에서 `/scrnaseq-stepwise-hitl` 을 부르면 됩니다.

```bash
git add -A && git commit -m "병렬 실험 출발점"   # worktree 는 마지막 커밋에서 갈라집니다
claude                                          # 그 다음 /scrnaseq-plan-execute
```

스킬은 연구 질문을 먼저 받고 → `worktrees/<실험이름>/` 을 만들고 → 그 안으로 세션을
옮긴 뒤 분석을 시작합니다. 커밋되지 않은 변경이 있으면 지금 커밋할지 마지막 커밋에서
갈라질지 물어봅니다.

```bash
bash status.sh     # 실험 상태를 한 표로
bash cleanup.sh    # 정리
```

공용 입력(`data/raw/`, `data/genesets/`, `agent_lab/`, `core_markers.xlsx`, `.claude/` 등)은
복사하지 않고 main 을 가리키는 심볼릭 링크로 걸립니다. 실험이 **만드는** 것(`scripts/`,
`data/processed/`, `results/`, `figures/`)만 worktree 마다 따로 생깁니다 — worktree 하나당 약 17MB.
무엇을 공유하고 무엇을 따로 둘지는 `.claude/scripts/worktree_init.sh` 의 `SHARED` 목록에
한 곳으로 모여 있습니다.

시험해 보고 싶은 아이디어가 셋 이상이면 `setup.sh` 로 미리 깔아 둘 수 있습니다.
이때는 만들어진 worktree 에서 각각 `claude` 를 띄웁니다.

```bash
bash setup.sh harmony-integration scvi-integration no-integration
cd worktrees/harmony-integration && claude
```

실험이 끝나면 저장소 루트에서 `/scrnaseq-compare-experiments` 로 비교합니다.

### 분석 범위 — 기능 분석까지 갑니다

이 분석은 QC → 클러스터링 → 주석 → 차등발현에서 끝나지 않고,
**조건 간 기능 분석(경로 · 전사인자 활성)** 까지 갑니다. 내용은
[sc-best-practices 의 Gene set enrichment and pathway analysis](https://www.sc-best-practices.org/conditions/gsea-pathway/)
챕터를 따랐습니다.

```bash
python3 verify.py            # 패키지 · gene set 캐시 · 입력 데이터 점검
python3 fetch_genesets.py    # gene set 을 data/genesets/ 에 캐시 (최초 1회)
```

| | |
|---|---|
| 무엇을 하나 | 세포 수준 점수(AUCell · ULM) · pseudobulk 조건 대비(GSEA · ULM · ORA) |
| 쓰는 자원 | MSigDB Hallmark · Reactome · PROGENy · CollecTRI |
| 왜 pseudobulk 인가 | 도너가 8명, 조건마다 8명 전부 있습니다. (도너 × 조건)으로 합치면 **8 대 8** 의 진짜 반복이 되고, 세포 단위 검정의 pseudoreplication 이 해소됩니다 |
| 양성 대조 | IFN-beta 를 넣었으니 인터페론 반응이 최상위여야 합니다. **안 나오면 앞 단계가 깨진 것입니다** |

> **decoupler 는 2.0 에서 API 가 전면 개편되었습니다** (`dc.run_ulm` → `dc.mt.ulm`).
> LLM 이 학습한 코드 대부분은 1.x 라 Claude 가 옛 함수를 쓸 가능성이 높습니다.
> 대응표는 `.claude/skills/decoupler-cheatsheet/SKILL.md` 맨 앞에 있습니다.
> 이미 만들어 둔 Codespace 는 `pip install -U 'decoupler>=2.2,<3' 'pydeseq2>=0.5,<1'` 를 한 번 실행하세요.

## 설치되는 주요 패키지

`scanpy` `anndata` `leidenalg` `igraph` `umap-learn` `harmonypy` `pydeseq2` `decoupler`
`gseapy` `celltypist` `matplotlib` `seaborn` `jupyterlab`

전체 목록과 버전은 [.devcontainer/requirements.txt](.devcontainer/requirements.txt) 참고.

## 참고 문헌

Kang HM, Subramaniam M, Targ S, et al. **Multiplexed droplet single-cell RNA-sequencing using
natural genetic variation.** *Nature Biotechnology* 36, 89–94 (2018).

Heumos L, Schaar AC, Lance C, et al. **Best practices for single-cell analysis across modalities.**
*Nature Reviews Genetics* 24, 550–572 (2023). — https://www.sc-best-practices.org/

Badia-i-Mompel P, Vélez Santiago J, Braunger J, et al. **decoupleR: ensemble of computational
methods to infer biological activities from omics data.** *Bioinformatics Advances* 2, vbac016 (2022).

Holland CH, Tanevski J, Perales-Patón J, et al. **Robustness and applicability of transcription
factor and pathway analysis tools on single-cell RNA-seq data.** *Genome Biology* 21, 36 (2020).
