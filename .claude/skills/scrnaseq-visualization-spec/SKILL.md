---
name: scrnaseq-visualization-spec
description: 단일세포 RNA-seq 분석의 annotation·DEG·기능 분석(GSEA·pathway) 단계에서 반드시 만들어야 하는 그림의 종류·구성·기준 임베딩을 명시한다. annotation 은 celltypist 로 수행하고 cluster marker dotplot(필요하면 curated marker로 축소)으로 검증한다. DEG 시각화는 celltype DEG(annotation UMAP + marker scatter)와 조건 간 DEG(비보정 UMAP + volcano) 두 세트로 나누어 서로 다른 임베딩을 쓴다. 기능 분석은 pathway 활성 점수를 UMAP scatter와 ctrl/stim 구분 stacked violin으로 보여주고, 모든 그림은 한글 폰트 깨짐(tofu) 없이 렌더링한다. scrnaseq-plan-execute·scrnaseq-stepwise-hitl 실행 중 annotation·DEG·기능분석 단계 코드를 짜기 전에 읽는다. 트리거: "annotation 그림", "DEG 그림", "dotplot", "volcano plot", "scatter plot", "GSEA 그림", "pathway 그림", "stacked violin", "한글 깨짐", "폰트 깨짐" 단계 진입 시.
---

이 스킬은 8단계 scRNA-seq 파이프라인(`scrnaseq-plan-execute`/`scrnaseq-stepwise-hitl` 공용)에서
**"그림을 그렸다"만으로는 부족한 지점**을 규격화한 것이다. 어떤 임베딩 위에 그릴지, 어떤
그림 형태(scatter vs volcano)를 쓸지가 결과 해석을 바꾸므로, annotation·DEG·기능분석 코드를
짜기 **전에** 이 문서를 읽고 아래 규격을 따른다. `step-validator` 는 이 규격을 기준으로 채점한다.

## 0. 모든 그림 공통 — 한글 폰트 깨짐(tofu) 방지

matplotlib 기본 폰트(DejaVu Sans)에는 한글 글리프가 없다. 그림 제목·축 라벨에 한글이
섞이면 네모(tofu)로 깨진다 — GSEA/pathway 그림처럼 제목에 "~ 경로 활성" 같은 한글 설명을
붙이는 자리에서 특히 자주 터진다. 아래 둘 중 하나를 **반드시** 지킨다.

1. **(권장) 그림 안 텍스트는 영어만 쓴다.** title·axis label·legend·주석 텍스트 전부.
   pathway/gene set 이름(`INTERFERON_ALPHA_RESPONSE` 등)과 유전자 심볼은 원래 영어이므로
   번역하지 않는다. 해석·설명은 그림이 아니라 리포트 본문(한글)에 쓴다 — 그림 캡션에서
   한글로 설명해도 되는 건 리포트 파일 쪽 텍스트이지 matplotlib 렌더링 텍스트가 아니다.
2. **부득이 그림 안에 한글을 넣어야 하면**, 렌더링 전에 이 환경에 실제로 설치된 한글
   폰트를 확인하고(`fc-list :lang=ko` 또는 `matplotlib.font_manager` 로 탐색) 그 폰트
   이름으로 `plt.rcParams['font.family']` 를 지정한다. `plt.rcParams['axes.unicode_minus']
   = False` 도 같이 설정한다(안 하면 마이너스 부호가 깨진다). 어떤 폰트를 썼는지 결정
   로그에 남긴다.

어느 쪽을 택했든 **저장하기 전에 실제로 그림을 확인해서** 네모 깨짐이 없는지 본다.
확인 없이 "폰트 설정했으니 괜찮겠지"로 넘기지 않는다.

## 1. Annotation — celltypist 로 수행한다

marker positive/negative 점수 최댓값 할당 방식 대신 **celltypist** 로 세포 타입을 예측한다.

- 조직에 맞는 pretrained 모델을 고른다 (PBMC 면 `Immune_All_Low.pkl` 또는
  `Immune_All_High.pkl` 계열). 모델이 로컬에 없으면 `celltypist.models.download_models()`
  로 받고, **모델 이름과 버전을 결정 로그와 `annotation_summary.json` 에 기록한다** —
  기록이 없으면 재현 불가능하다.
- `celltypist.annotate(adata, model=..., majority_voting=True)` 로 세포 단위 예측 후
  cluster 단위로 다수결(majority voting) 라벨을 cluster 에 배정한다. 세포 단위 예측을
  그대로 쓰지 않는다 — 같은 클러스터 안에서 라벨이 흔들리면 그 자체가 클러스터링/해상도
  문제일 수 있으므로 별도로 기록한다.
- `core_markers.xlsx` 같은 참조 마커 파일이 있으면 celltypist 라벨과 **대조 검증**에
  쓴다(2번 dotplot 이 이 역할을 한다). celltypist 예측을 이 파일로 덮어쓰지 않는다 —
  불일치가 있으면 근거와 함께 기록하고 어느 쪽을 채택했는지 남긴다.
- celltypist 모델이 이 조직/종에 없거나 부적절하면(예: 비인간 종, 흔치 않은 조직)
  그 사실을 기록하고 marker 기반 방식으로 돌아갈 수 있다 — 단, **왜 celltypist 를 못
  쓰는지**를 결정 로그에 남긴 경우에만 허용한다.

## 2. Annotation 이후 — cluster marker dotplot (필수)

annotation 이 끝나면 cluster 별로 marker 발현이 실제로 분리되는지 **dotplot 으로 확인한다.**

1. **1차 dotplot**: 이 조직에서 흔히 쓰는 전체 marker 세트(`core_markers.xlsx` 가 있으면
   그 유전자들, 없으면 celltypist 모델의 대표 마커)로 `sc.pl.dotplot(groupby="leiden", ...)`
   를 그린다.
2. **한눈에 클러스터 구분이 안 되면** (예: 대부분의 클러스터에서 여러 마커가 비슷한
   크기·색으로 찍혀 있어 어느 마커가 어느 클러스터를 가르는지 바로 안 보이는 경우)
   — **2차 축소 dotplot**을 추가로 그린다. celltypist 로 배정된 celltype 과 도메인
   지식을 바탕으로, **타입마다 가장 특이적인 marker 1~3개만** 추려서 다시 그린다.
   두 그림 모두 저장하고, 축소가 필요했는지/왜 필요했는지 결정 로그에 남긴다.
3. 축소 여부와 무관하게 최종적으로 **클러스터마다 최소 1개 이상의 뚜렷한 marker**가
   dotplot 상에서 식별돼야 한다. 안 되면 근거 약한 클러스터로 표시하고 annotation 요약에
   남긴다(기존 `unassigned-weak` 관행 유지).

파일명 예: `figures/annotation/dotplot_core_markers.png`(1차),
`figures/annotation/dotplot_curated_markers.png`(2차, 필요시).

## 3. DEG 시각화 — 두 개의 병렬 패널 세트

DEG 는 목적이 다른 두 가지가 있고, **각각 다른 임베딩 위에서 그려야 한다.** 하나로
뭉뚱그리면 조건 신호가 배치 보정으로 지워지거나, 반대로 세포 타입 구조가 조건 차이에
휩쓸려 보이지 않는다.

### 3-1. Celltype DEG 패널 — "세포 타입이 잘 갈라졌는가"

**목적**: annotation 이 만든 세포 타입 구조 자체를 보여주고, 그 구조를 만든 marker 유전자를
같이 보여준다.

- **왼쪽 패널**: UMAP. `stim`(관심 조건)을 포함해 batch 보정(Harmony 등)된 임베딩
  위에서 계산한 clustering 결과를 그린다 — 즉 3단계 배치 통합 이후의 `post-integration`
  UMAP (`umap_post_integration.png` 계열). 색은 celltype.
- **오른쪽 패널**: celltype 별 marker 유전자(cluster marker, one-vs-rest DEG)를
  **scatter plot** 으로 그린다. **volcano 가 아니다** — 유의성 강조가 아니라 발현
  수준 자체를 보여주는 게 목적이다. 기본 형태: x축 = 클러스터 내 발현 세포 비율
  (`pct_expressed_in_group`), y축 = 클러스터 내 평균발현(`mean_expr_in_group`), 점 색 =
  클러스터/celltype, 상위 marker 유전자 이름을 라벨로 표시. (대안으로 x=log2FC,
  y=클러스터 내 평균발현 을 써도 되지만 -log10(padj) 를 축으로 쓰는 볼케이노 형태는
  안 된다.)
- 왼쪽·오른쪽을 **한 figure 안에 나란히**(`plt.subplots(1, 2, ...)`) 배치한다.
- 파일명 예: `figures/annotation/celltype_deg_panel.png`.

### 3-2. 조건(ctrl vs stim) DEG 패널 — "조건 반응이 뚜렷한가"

**목적**: 배치 보정을 걸지 않은 원본 표현형 위에서 조건이 만드는 이동을 보여주고,
그 이동의 유의성을 조건 간 DEG 로 보여준다.

- **왼쪽 패널**: UMAP. **조건 간 배치 보정을 걸지 않은** 임베딩 — 3단계에서 만든
  `pre-integration` UMAP(원본 `X_pca` 기반, `umap_pre_integration.png` 계열)을 그대로
  쓴다. 색은 조건 변수(`stim`/`ctrl`). Harmony 등으로 보정된 임베딩을 쓰면 조건이
  만든 이동 자체가 지워져 이 패널의 목적과 모순된다.
- **오른쪽 패널**: 조건 간 DEG **volcano plot** (x=log2FC, y=-log10(padj), 유의 유전자
  강조, 상위 유전자 라벨). 세포 타입별로 여러 개 필요하면 세포 타입마다 하나씩
  그리드로 배치한다(기존 `volcano_per_celltype.png` 방식 유지).
- 파일명 예: `figures/deg/condition_deg_panel.png` (왼쪽 UMAP + 대표 celltype 1개 volcano),
  세포 타입별 전체 volcano 는 `figures/deg/volcano_per_celltype.png` 로 별도 유지해도 된다.

### 3-3. 결정 로그에 남길 것

두 패널 세트가 **서로 다른 임베딩을 의도적으로 쓴다는 사실**을 결정 로그에 한 줄로
남긴다 — 이후 검증자나 리뷰어가 "왜 UMAP이 두 종류냐"고 묻지 않도록.

## 4. 기능 분석(GSEA·pathway) 시각화 — pathway 활성을 세포 단위로 보여준다

enrichment 표(상위 pathway 순위·점수)만으로는 그 pathway 가 실제로 어느 세포에서 얼마나
발현되는지, 조건에 따라 어떻게 갈리는지 보이지 않는다.
[sc-best-practices의 조건 비교·기능 분석 챕터](https://www.sc-best-practices.org/conditions/gsea-pathway/)
방식을 따라 아래 두 그림을 **enrichment 표에 추가로** 그린다. 대상 pathway 는 상위
결과(양성 대조인 `INTERFERON_ALPHA_RESPONSE` 계열 포함)에서 3~5개를 고른다.

### 4-1. Pathway 활성 scatter plot (embedding plot)

**목적**: 고른 pathway 의 세포 단위 활성 점수(`dc.mt.*` 결과의 score matrix, 즉
`adata.obsm["score_..."]` 류)를 UMAP 위에 점 색으로 얹어, 그 활성이 특정 세포 타입/영역에
몰려 있는지 눈으로 확인한다.

- **비보정(pre-integration) UMAP**을 쓴다 — 3-2 조건 DEG 패널과 같은 이유로, 배치
  보정된 임베딩을 쓰면 조건이 만드는 활성 차이가 지워질 수 있다.
- `sc.pl.embedding(adata, basis="X_umap_pre_integration", color="score_<pathway>", ...)`
  같은 형태로 pathway 마다 그리거나, `groupby`/좌우 분할로 **ctrl vs stim 을 나란히**
  배치해 조건 간 활성 분포 차이가 보이게 한다.
- 파일명 예: `figures/functional/pathway_scatter_<pathway>.png`.

### 4-2. Ctrl vs Stim 구분 stacked violin plot

**목적**: 고른 pathway 활성 점수의 분포를 celltype 별로, 그리고 그 안에서 ctrl/stim 을
나눠 비교한다 — scatter 는 공간 패턴을, stacked violin 은 celltype × 조건별 분포 차이를
정량적으로 보여준다.

- `sc.pl.stacked_violin` 은 `groupby` 를 하나만 받으므로, celltype 과 조건을 합친 그룹
  컬럼(예: `adata.obs["celltype_stim"] = adata.obs["celltype"].astype(str) + "_" +
  adata.obs["stim"].astype(str)`)을 만들어 그 컬럼으로 그리거나, celltype 별 subplot 을
  만들어 각각 `seaborn.violinplot(..., x="celltype", y="score", hue="stim", split=True)`
  로 그린다. 어느 방식을 쓰든 **같은 celltype 안에서 ctrl/stim 이 나란히 비교 가능**해야
  한다 — celltype 만으로 묶고 조건을 안 나누면 이 그림의 목적을 못 채운다.
- 여러 pathway 를 한 그림에 stack 해도 되고(변수=pathway, groupby=celltype_stim), pathway
  하나당 그림 하나로 나눠도 된다 — 어느 쪽이든 ctrl/stim 구분이 보이면 된다.
- 파일명 예: `figures/functional/pathway_stacked_violin.png`.

### 4-3. 결정 로그에 남길 것

고른 pathway 목록(왜 이 pathway 들을 골랐는지 — 양성 대조 포함 여부), scatter 에 쓴
임베딩이 pre-integration 인 이유, stacked violin 에서 celltype×조건을 어떻게 묶었는지를
한 줄로 남긴다. 0번의 폰트 규칙을 지켰는지(그림 텍스트를 영어로 뒀는지, 아니면 어떤
한글 폰트를 지정했는지)도 함께 남긴다.

## 5. step-validator 채점 포인트 (요약)

- annotation 단계: celltypist 사용 여부·모델명 기록, 1차 dotplot 존재, 필요시 2차 축소
  dotplot과 그 판단 근거.
- 조건 간 차등발현 단계: celltype DEG 패널(post-integration UMAP + scatter)과
  조건 DEG 패널(pre-integration UMAP + volcano)이 각각 올바른 임베딩을 쓰는지, 두 패널을
  뒤바꿔 쓰지 않았는지.
- 기능 분석 단계: pathway 활성 scatter(비보정 UMAP)와 ctrl/stim 구분 stacked violin 이
  둘 다 있는지, 그림 텍스트에 한글 폰트 깨짐(tofu)이 없는지.
