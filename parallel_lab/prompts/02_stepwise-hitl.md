# 세션 B — 단계별 쿼리 · human-in-the-loop

실행 위치: `worktrees/stepwise-hitl/`

```bash
cd worktrees/stepwise-hitl && claude
```

---

세션 A 와 **Task · Objective · Dataset · Path 가 똑같습니다.** 달라지는 것은 진행 방식뿐입니다.
A 는 계획을 한 번 승인받고 혼자 가고, B 는 갈림길마다 멈춰 여러분에게 묻습니다.

## 여는 프롬프트 — 그대로 붙여 넣으세요

```
Task       IFN-beta 자극에 대한 PBMC 세포 타입별 반응 분석
Objective  IFN-beta 자극을 받은 PBMC 는 세포 타입별로 어떻게 다르게 반응하는가.
           유전자 수준과 경로·전사인자 수준에서 각각 답한다.

Dataset    GSE96583 batch2 — PBMC, 도너 8명, ctrl / stim 두 조건.
           약 12,000 세포 × 14,391 유전자. .X 는 raw count.
           obs: stim · donor · total_counts · n_genes. 세포 타입 주석은 없다.

Path       입력    data/processed/gse96583_ifnb.h5ad
           참조    data/genesets/                 gene set · footprint 캐시
                   core_markers.xlsx              annotation 검증용
                   parallel_lab/CHEATSHEET.md     decoupler 2.x API
           작업    이 작업 트리. 모든 중간 데이터·그림·로그를 여기에만 쓴다.

Rules
  R1  계획을 한 번에 세우지 말고 한 단계씩 간다. QC 부터 시작한다.
  R2  각 단계를 끝낼 때마다 (1) 무엇을 했고 어떤 수치가 나왔는지,
      (2) 이 단계에서 판단이 갈리는 지점과 선택지 2~3개를 근거와 함께 제시하고 멈춘다.
      내가 고르기 전에 스스로 정하고 넘어가지 않는다.
  R3  내가 고른 결정은 EXPERIMENT.md 결정 로그에 decided_by: human 으로 남긴다.
      내가 "알아서 해" 라고 맡긴 것만 claude 로 남긴다.
  R4  수치를 지어내지 않는다. 없으면 없다고 적는다.
  R5  decoupler 는 2.x 다. 기능 분석 코드를 짜기 전에 CHEATSHEET.md 를 읽는다.

단계는 대략 이 순서로 간다.
  1  QC
  2  정규화 · HVG · 차원축소
  3  배치 통합
  4  Clustering
  5  Annotation
  6  조건 간 차등발현
  7  조건 간 기능 분석 (경로 · 전사인자)
  8  REPORT

Output Format
  results/summary/metrics.json   parallel_lab/metrics_template.json 의 키 이름을 지킨다.
  results/summary/report.html

QC 부터 시작해줘.
```

---

## 각 단계에서 하는 일

Claude 가 선택지를 내놓으면 **고르기 전에 근거를 한 번 되물어 보세요.**

```
2번을 고르면 뒤 단계에서 뭐가 달라져?
```

```
그 컷오프로 잘려나가는 세포가 어떤 세포들인지 먼저 보여줘.
```

고른 뒤에는 진행시킵니다.

```
2번으로 가자. 그리고 이 결정 EXPERIMENT.md 에 남겨줘 — 내가 골랐다고.
```

## 흔히 갈리는 지점

| 단계 | 갈림길 |
|---|---|
| 1 QC | `n_genes` 상한을 둘 것인가 · 컷오프를 어디로 |
| 2 정규화·HVG | HVG 개수 · flavor · PC 개수 |
| **3 배치 통합** | **`stim` 을 배치로 보고 보정할 것인가** |
| 4 Clustering | resolution — 클러스터를 몇 개로 볼 것인가 |
| 5 Annotation | 애매한 클러스터를 합칠 것인가 나눌 것인가 |
| 6 차등발현 | 세포 타입 안에서 볼 것인가 · 검정 방법 |
| **7 기능 분석** | **어느 gene set 을 쓸 것인가** · 세포 수준인가 조건 대비인가 |

### ★ 3단계에서 한 번 멈추세요

`stim` 을 배치로 보고 보정하면 **보려던 조건 효과가 같이 지워질 수 있습니다.**
A 는 이 갈림길에서 혼자 결정했습니다. B 에서는 여러분이 결정합니다.
**두 실험이 여기서 갈릴 가능성이 가장 높습니다.**

```
보정하면 IFN 반응 유전자의 조건 간 차이가 얼마나 줄어? 보정 전후를 수치로 보여줘.
```

### ★ 7단계에서 6단계와 비교시키세요

7단계는 (도너 × 조건) pseudobulk 로 갑니다. 도너가 8명, 조건마다 다 있으니 **8 대 8** 입니다.
6단계에서 세포 단위로 뽑은 DEG 개수와 나란히 놓아 보세요.

```
6단계에서 세포 단위로 뽑은 DEG 개수랑 지금 pseudobulk DEG 개수를
세포 타입별로 나란히 표로 보여줘. 차이가 나는 이유도.
```

대개 자릿수가 다릅니다. **그게 6단계에서 한계로만 적었던 pseudoreplication 의 크기입니다.**

그리고 이 데이터는 **답의 일부가 알려져 있습니다** — IFN-beta 를 넣었으니 인터페론 반응이
최상위여야 합니다. 그래서 근거를 끝까지 따라갈 수 있습니다.

```
상위 경로가 그 자리에 온 이유를 leading edge 유전자로 보여줘.
그 유전자들의 실제 log2FC 와 검정 통계량도 같은 표에.
```

## 고르기 전에 검증자를 부를 수 있습니다

세션 A 와 **같은 검증자**(`step-validator`)가 이 작업 트리에도 걸려 있습니다.

```
고르기 전에, 방금 끝낸 단계를 step-validator 로 채점해줘.
결과는 results/validation/<번호>_<단계>.md 에 저장하고,
정확성·완결성 점수와 고쳐야 할 것만 보여줘.
```

정확성 2점 이하면 `FAIL`(진행 금지), 둘 다 4점 이상이면 `PASS`, 나머지는 `WARN` 입니다.

점수를 보고 고르면 선택의 근거가 달라집니다. **그 차이가 A 와 비교할 재료입니다.**
A 는 같은 점수를 혼자 읽고 혼자 반영했고, 여기서는 여러분이 읽습니다.

> 채점자도 Claude 입니다. 5점이 옳다는 뜻은 아닙니다.

## 끝났을 때 확인

```
results/summary/metrics.json 과 EXPERIMENT.md 결정 로그를 채워줘.
내가 고른 것과 네가 고른 것을 decided_by 로 구분해줘.
채점을 돌린 단계는 validation 블록에 점수를 남겨줘.
```
