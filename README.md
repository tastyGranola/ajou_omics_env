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
  requirements.txt      설치되는 분석 패키지 목록
  post-create.sh        최초 생성 시 실행되는 설치 스크립트
data/raw/               GEO 원본 파일 (mtx, barcodes, genes, 세포 주석)
data/processed/         전처리된 실습용 h5ad
notebooks/              실습 노트북
scripts/prepare_data.py 원본 데이터 → 실습용 데이터 변환 스크립트
```

## 설치되는 주요 패키지

`scanpy` `anndata` `leidenalg` `igraph` `umap-learn` `harmonypy` `pydeseq2` `decoupler`
`gseapy` `celltypist` `matplotlib` `seaborn` `jupyterlab`

전체 목록과 버전은 [.devcontainer/requirements.txt](.devcontainer/requirements.txt) 참고.

## 참고 문헌

Kang HM, Subramaniam M, Targ S, et al. **Multiplexed droplet single-cell RNA-sequencing using
natural genetic variation.** *Nature Biotechnology* 36, 89–94 (2018).
