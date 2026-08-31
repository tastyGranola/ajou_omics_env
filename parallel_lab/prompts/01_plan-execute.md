# 세션 A — plan-and-execute

실행 위치: `worktrees/plan-execute/`

```bash
cd worktrees/plan-execute && claude
```

---

## 왜 구조화된 프롬프트인가

이 실험은 **한 번 승인하면 끝까지 혼자 갑니다.** 승인 전 프롬프트가 사실상 유일한
개입 지점입니다. 그래서 "알아서 해줘" 대신 각 단계에서 **무엇을 고정하고 무엇을 맡길지**를
미리 갈라서 적습니다.

아래 프롬프트의 형식은 Biomni 논문 보충자료(Science 393, eadz4351) Section L 의
분석 지시 프롬프트를 따랐습니다. `TASK`/`GOAL` 머리말, `DATA` 블록, `1 / 1.1 / 1.2`
소수점 번호, 단계마다 명시적인 임계값과 출력 경로가 그것입니다.

| 표기 | 뜻 |
|---|---|
| `[고정]` | 내가 정했다. 그대로 따른다 — 결정 로그에 남길 것이 없다 |
| `[위임]` | 네가 판단해서 정해라 — **결정 로그에 남는다** (`decided_by: claude`) |
| `[산출]` | 이 단계가 남겨야 하는 파일 |
| `[검증]` | 이 단계가 끝나면 `step-validator` 에이전트가 채점한다 |

**모든 항목에 번호가 붙어 있습니다.** 결정 로그도, 검증 결과도 `3.6` 처럼 번호로
서로를 가리킵니다. 세션 C 에서 "어디서 갈렸나" 를 찾을 때 이 번호가 좌표가 됩니다.

`[위임]` 을 몇 개 남기느냐가 이 실험의 성격을 정합니다. 전부 `[고정]` 으로 바꾸면
"명세 실행" 실험이 되고, 전부 `[위임]` 으로 바꾸면 원래의 "완전 자율" 실험이 됩니다.

---

## 여는 프롬프트 — 그대로 붙여 넣으세요

```
TASK   IFN-beta 자극에 대한 PBMC 세포 타입별 반응 차이 규명
GOAL   IFN-beta 자극을 받은 PBMC 는 세포 타입별로 어떻게 다르게 반응하는가?

DATA
  입력      data/processed/gse96583_ifnb.h5ad
  참조      core_markers.xlsx   (5.3 annotation 검증에서만 사용)
  WORKDIR   이 작업 트리
  모든 중간 데이터·그림·로그는 이 작업 트리 안에만 쓴다.


표기
  [고정]  그대로 따른다
  [위임]  네가 판단해서 정하고, 무엇을 왜 골랐는지와 고르지 않은 대안을
          EXPERIMENT.md 결정 로그와 metrics.json 의 decisions 에 남긴다
          (decided_by: claude, 항목 번호를 함께 적는다)
  [산출]  이 단계가 남겨야 하는 파일
  [검증]  이 단계가 끝나면 step-validator 서브에이전트를 부른다


진행 규칙
  R1  먼저 전체 계획을 체크박스 목록으로 만들어 보여준다.
        1. [ ] ...
      한 단계를 끝낼 때마다 목록을 갱신해서 다시 보여준다.
        1. [✓] ... (완료)
        2. [✗] ... (실패 — 이유)
        3. [ ] 수정된 2단계
      계획을 벗어나야 하면 멈추지 말고, [✗] 와 이유를 적은 뒤 수정된 단계를 넣고 간다.
  R2  코드 출력은 research log 처럼 쓴다. 단계 이름과 수치를 명확히 print 한다.
      함수를 부르고 결과를 print 하지 않으면 무엇을 했는지 확인할 수 없다.
  R3  그림을 저장하면 절대 경로를 print 한다.
  R4  데이터나 결과를 지어내거나 시뮬레이션하지 않는다. 사용자는 연구자다.
      수치가 없으면 없다고 적는다. 추정치를 실측치처럼 적지 않는다.
  R5  각 단계가 끝나면 step-validator 를 부른다.
        - 검증 결과 전문을 results/validation/<번호>_<단계>.md 에 저장한다
        - metrics.json 의 validation 블록에 점수를 누적한다
        - FAIL 이면 다음 단계로 가지 말고 고친 뒤 다시 검증한다
        - WARN 은 고치지 않아도 되지만 무엇을 남겨 뒀는지 결정 로그에 적는다
      검증자를 설득하려 하지 않는다. 근거가 없다는 지적은 근거를 만들어서 해소한다.


1   QC
1.1 [고정] MT- 유전자 비율을 계산하고, 필터를 걸기 전에 n_genes · total_counts ·
    pct_counts_mt 의 분포를 그린다
1.2 [고정] 하한 필터 — min_genes_per_cell 200, min_counts_per_cell 500,
    min_cells_per_gene 3
1.3 [위임] n_genes 상한과 pct_counts_mt 컷오프. 1.1 의 분포를 보고 정한다.
    상한을 두지 않기로 해도 된다. 잘려나가는 세포가 어떤 세포인지 먼저 확인한다
1.4 [고정] 필터 단계마다 잔존율을 표로 남긴다 — 시작 세포 수 대비 각 필터 후 세포 수와 %
1.5 [고정] stim 과 ctrl 각각의 필터 전후 세포 수를 함께 남긴다.
    한쪽이 크게 기울면 그 사실을 명시한다
[산출] figures/qc/ · results/qc/qc_retention.csv · metrics.json 의 qc
[검증] step-validator 를 "QC" 로 호출


2   정규화 · HVG
2.1 [고정] normalize_total(target_sum=1e4) 뒤 log1p
2.2 [고정] log-normalized 행렬을 adata.raw 또는 layers["lognorm"] 에 보존한다.
    6.1 에서 이 값을 쓴다
2.3 [고정] HVG 2000개, flavor="seurat", 배치를 나누지 않고 전체에서 선택
2.4 [고정] scale(max_value=10) 뒤 PCA 를 50 성분까지 계산
2.5 [위임] 이후 단계에서 실제로 쓸 PC 개수. variance ratio 를 보고 정한다
[산출] figures/preprocessing/pca_variance_ratio.png · metrics.json 의 preprocessing
[검증] step-validator 를 "정규화·HVG" 로 호출


3   배치 통합
3.1 [고정] adata.obs 의 컬럼을 먼저 출력해서, stim 말고 다른 배치 변수
    (donor, lane, batch 등)가 있는지 확인하고 결과를 적는다
3.2 [고정] batch_key = "stim" 으로 Harmony 통합을 수행한다
3.3 [고정] 보정 전 PCA 기반 UMAP 과 보정 후 UMAP 을 둘 다 그린다
3.4 [고정] 조건 효과가 살아 있는지 수치로 확인한다. ISG15, IFI6, ISG20, MX1, IFIT1 의
    stim/ctrl 평균 발현 차이를 보정 전과 후로 나란히 표에 남긴다. 그림만 보고 넘어가지 않는다
3.5 [고정] 이후 neighbors 는 3.2 의 결과(X_pca_harmony) 위에서 만든다
3.6 [위임] 3.4 의 표에서 조건 효과가 뭉개졌다고 판단되면 보정 없이 진행하는 쪽으로
    바꿔도 된다. 유지하든 바꾸든 3.4 의 어느 수치를 보고 그렇게 판단했는지 적는다
[산출] figures/clustering/umap_before_harmony.png · umap_after_harmony.png
       results/clustering/ifn_signature_preservation.csv
       metrics.json 의 preprocessing.batch_correction · batch_key
[검증] step-validator 를 "배치 통합" 으로 호출. 이 단계의 FAIL 은 반드시 해소하고 넘어간다


4   Clustering
4.1 [고정] neighbors(n_neighbors=15). 난수 seed 를 고정한다
4.2 [고정] leiden 을 resolution 0.2 / 0.4 / 0.6 / 0.8 / 1.0 으로 모두 돌린다
4.3 [고정] resolution 별 클러스터 개수와 최소 클러스터 크기를 표로, UMAP 을 패널로 남긴다
4.4 [위임] 그중 하나를 고른다. 근거는 4.3 의 수치로 댄다
4.5 [고정] 세포 수 10개 미만 클러스터가 있으면 목록으로 표시하고 어떻게 다룰지 적는다
[산출] results/clustering/resolution_sweep.csv
       figures/clustering/umap_resolution_panel.png
       metrics.json 의 clustering (최종 선택 하나) + resolution_sweep 키 (비교한 값 전체)
[검증] step-validator 를 "Clustering" 으로 호출


5   Annotation
5.1 [고정] rank_genes_groups(method="wilcoxon") 로 클러스터별 상위 marker 를 뽑는다
5.2 [고정] 세포 타입 이름마다 근거로 삼은 marker 를 함께 적는다
5.3 [고정] core_markers.xlsx 로 대조하고, 일치·불일치를 모두 표에 남긴다.
    불일치 항목을 빼지 않는다
5.4 [위임] 클러스터 병합 여부와 최종 이름. 근거가 약한 클러스터는 unassigned 로 남겨도 된다
5.5 [고정] PBMC 에서 기대되는 주요 타입(CD4 T, CD8 T, B, NK, CD14+ Mono,
    FCGR3A+ Mono, DC) 중 나오지 않은 것이 있으면 목록으로 적고 이유를 쓴다
[산출] results/annotation/marker_evidence.csv · results/annotation/core_marker_check.csv
       figures/annotation/ · metrics.json 의 annotation
[검증] step-validator 를 "Annotation" 으로 호출


6   조건 간 차등발현
6.1 [고정] 검정 입력은 2.2 의 log-normalized 발현이다. 배치 보정된 임베딩을 쓰지 않는다
6.2 [고정] 세포 타입별로 stim vs ctrl 을 비교한다. 전체 세포를 한 번에 비교하지 않는다
6.3 [고정] 세포 수 50개 미만인 타입도 계산하되 결과에 "저신뢰" 로 표시한다
6.4 [고정] method="wilcoxon", padj < 0.05, |log2FC| > 0.5.
    up/down 의 방향 정의를 명시한다 (stim 기준)
6.5 [고정] 세포 단위 검정이 같은 도너의 세포를 독립 표본으로 취급한다는 한계
    (pseudoreplication)를 리포트에 명시한다
6.6 [위임] pseudobulk 로 한 번 더 확인할지 여부. 했다면 두 결과의 차이도 적는다
[산출] results/deg/deg_per_celltype.csv · figures/deg/ · metrics.json 의 deg
[검증] step-validator 를 "차등발현" 으로 호출


7   리포트 · 마무리
7.1 [고정] results/summary/report.html 을 아래 네 절로 만든다
      a) 핵심 요약 — 200단어 이내. 목적 · 데이터 · 방법 · 주요 발견
      b) 주요 결과 — 세포 타입별 DEG 개수 표, 상위 유전자, 조건 간 차이
      c) 그림 요약 — QC · 보정 전후 UMAP · resolution 패널 · DEG
      d) 방법·QC 부록 — 모든 임계값을 담은 파라미터 표, 패키지 버전,
         단계별 세포 잔존율, 총 실행 시간과 최대 메모리
7.2 [고정] 리포트의 주장마다 근거 각주를 단다. [위임] 결정에서 비롯된 주장에는
    해당 항목 번호(예: 3.6)를 함께 적는다
7.3 [고정] results/summary/metrics.json 을 parallel_lab/metrics_template.json
    형식으로 완성한다. 정해진 키 이름을 바꾸지 않는다
7.4 [고정] EXPERIMENT.md 의 진행 체크리스트를 모두 채운다
[산출] results/validation/ 아래 단계별 검증 리포트 일곱 개
[검증] step-validator 를 "마무리" 로 한 번 더 호출한다.
       metrics.json 의 validation.n_fail 이 0 인지 확인하고, 아니면 해소한 뒤 끝낸다


먼저 위 요구사항을 반영한 전체 실행 계획을 R1 의 체크박스 목록으로 세워서 보여줘.
각 단계에 남은 [위임] 판단이 무엇이고 어떤 선택지가 있는지도 계획에 같이 적어줘.

내가 계획을 승인하면 그 다음부터는 나에게 묻지 말고 끝까지 실행해.
```

여기서 **plan mode** 를 쓰면 더 분명해집니다. 프롬프트를 넣기 전에 `Shift+Tab` 을 두 번
눌러 `plan mode` 로 바꾸면, Claude 는 파일을 고치지 않고 계획만 세웁니다.
계획을 승인하는 순간부터 실행으로 넘어갑니다.

## 검증자는 무엇을 하나

`step-validator` 는 이 저장소에 정의된 **읽기 전용 서브에이전트**입니다
(`.claude/agents/step-validator.md`). 분석을 하지 않고, 방금 끝난 단계를 **두 축으로
1–5 점 채점**합니다.

| 축 | 묻는 것 |
|---|---|
| **정확성** | 방법이 맞는가. 이 결과를 믿을 수 있는가 |
| **완결성** | 남길 것을 남겼는가. 다른 사람이 이대로 재현할 수 있는가 |

두 점수에서 게이트가 자동으로 나옵니다 — 정확성 2점 이하면 `FAIL`(진행 금지),
정확성과 완결성이 **둘 다 4점 이상**이면 `PASS`, 그 밖은 전부 `WARN` 입니다.
확인할 파일을 못 찾았으면 점수 대신 `UNKNOWN` 입니다.

이 루브릭은 Biomni 보충자료 Table S32–S33 의 완결성·정확성 1–5 채점표를 단일세포
분석용으로 옮긴 것입니다. 같은 자료 Section I 에서 평가자를 **출처에 블라인드**로 둔 것과,
"발견이 데이터에서 나온 것인지 환각인지 코드와 트레이스를 따라가며 확인" 한 절차도
그대로 가져왔습니다. 그래서 검증자는 **점수를 매기기 전에 이 작업 트리가 어떤 진행 방식의
실험인지 보지 않습니다.**

두 실험이 **같은 검증자**를 씁니다. `setup.sh` 가 `.claude/agents/` 를 심볼릭 링크로
걸기 때문입니다. 기준까지 달라지면 점수를 비교할 수 없습니다.

> **검증자도 Claude 입니다.** 5점이 옳다는 뜻은 아닙니다.
> 세션 C 에서 "검증자가 놓친 것" 을 찾는 것까지가 이 실습입니다.

## 계획을 받으면 이것부터 보세요

`[위임]` 여섯 개(1.3 · 2.5 · 3.6 · 4.4 · 5.4 · 6.6)에 대해 **선택지를 제대로 벌려
놓았는지** 확인합니다. 3.6 과 4.4 가 이 실험의 결과를 가장 크게 좌우합니다.

계획을 그대로 받아들여도 되고, 한 군데만 고쳐도 됩니다. 고쳤다면 무엇을 고쳤는지
기억해 두세요. 비교할 때 그 한 줄이 결과를 어디까지 바꿨는지 보게 됩니다.

```
좋아. 이대로 진행해.
```

## 실행이 도는 동안

**이 창은 그대로 두고 세션 B 로 넘어가세요.** 기다리지 않습니다.
그게 이 실습의 요점입니다.

돌아왔을 때는 마지막에 출력된 **체크박스 목록**만 보면 어디까지 갔는지 알 수 있습니다.
`[✗]` 가 있으면 계획을 벗어난 자리입니다 — 거기가 볼 만한 곳입니다.

## 끝났을 때 확인

```
results/summary/metrics.json 과 EXPERIMENT.md 결정 로그가 채워졌는지 확인하고,
빠진 항목이 있으면 채워줘. [위임] 이었던 1.3 · 2.5 · 3.6 · 4.4 · 5.4 · 6.6 여섯 개가
모두 결정 로그에 항목 번호와 함께 있어야 한다.

그리고 results/validation/ 의 단계별 채점을 한 표로 요약해줘.
정확성·완결성 점수, WARN 으로 남겨 둔 것, 왜 고치지 않았는지까지.
```

## 이 프롬프트 자체를 실험 변수로 쓰기

`[고정]` 과 `[위임]` 의 경계를 옮기면 그대로 다른 실험이 됩니다.

| 바꾸는 곳 | 무엇을 보게 되나 |
|---|---|
| 3.2 Harmony 를 `[위임]` 으로 | 보정 여부를 Claude 가 처음부터 고르게 했을 때와의 차이 |
| 4.2 를 `[고정] resolution 0.5` 로 | 여러 값을 비교하는 것이 실제로 결과를 바꾸는지 |
| `[위임]` 을 전부 `[고정]` 으로 | 명세 실행과 자율 실행의 차이 |
| `[검증]` 호출을 전부 빼면 | 자기 검증이 결과를 실제로 바꾸는지 |

이름만 정해 주면 worktree 가 생기니, 프롬프트를 고쳐서 그대로 다음 실험으로 넘기면 됩니다.

```bash
bash parallel_lab/setup.sh spec-driven fully-autonomous
```
