single_cell_project/
├── data/
│   ├── raw/
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
│   └── condition_analysis/
│
├── figures/
│   ├── qc/
│   ├── clustering/
│   ├── annotation/
│   └── deg/
│
├── config/
│
└── README.md

이 디렉토리 구조는 프로젝트의 기본적인 조직 원칙을 나타낸다. 파일명, 파일 개수, 분석 스크립트나 노트북의 분할 방식은 고정하지 않는다.

분석 목적과 복잡도에 따라 필요한 파일을 자유롭게 생성·통합·분리할 수 있으며, 사용하지 않는 디렉토리를 형식적으로 채울 필요는 없다.

data/raw/: 원본 데이터. 가능하면 수정하지 않는다.
data/processed/: QC, preprocessing, annotation 등 분석 과정에서 생성되는 재사용 가능한 중간 데이터.
scripts/: 재현 가능하고 반복 실행할 분석 코드. 필요에 따라 하나 또는 여러 파일로 구성한다.
notebooks/: 데이터 탐색, 분석 과정 확인, 시각적 검토, 가설 검증, 결과 해석 등을 위한 interactive analysis 공간. 모든 분석을 반드시 notebook으로 작성할 필요는 없으며, 안정화된 로직은 필요에 따라 scripts/로 옮길 수 있다.
results/qc/: QC 통계, 필터링 결과 등.
results/doublet/: doublet detection 관련 결과.
results/clustering/: 차원 축소, neighborhood graph, clustering 등 세포 구조 분석 결과.
results/annotation/: marker 분석, cell-type annotation 및 annotation 검증 결과.
results/deg/: differential expression 분석 결과.
results/condition_analysis/: treatment, disease, stimulation 등 condition 간 비교 분석 결과.
figures/: 분석 과정에서 생성한 주요 시각화. 필요한 경우 목적에 맞는 하위 디렉토리를 자유롭게 추가한다.
config/: 분석 파라미터나 설정 파일이 필요한 경우 사용한다.
README.md: 데이터, 분석 목적, 주요 분석 과정과 결과를 설명한다.

새로운 분석 단계가 필요하면 기존 구조에 억지로 맞추지 말고 적절한 디렉토리나 하위 디렉토리를 추가할 수 있다.

디렉토리 구조는 고정된 분석 workflow가 아니라 각 산출물의 역할과 저장 위치를 정의하기 위한 기준으로 사용한다.

필요한 최소한의 파일만 생성하며, 단순히 디렉토리 구조를 채우기 위한 파일은 만들지 않는다.

분석의 주요 단계가 완료되면 현재까지의 분석 과정, 핵심 결과, 주요 시각화, 해석 및 다음 분석 후보를 정리한 HTML report를 생성한다.

HTML report 생성 작업은 가능하면 메인 대화/작업 세션을 점유하지 않도록 별도의 background process로 실행한다. 사용자는 report가 생성되는 동안에도 같은 세션에서 추가 질문, 분석 수정, 후속 요청을 계속할 수 있어야 한다.

Report 생성 때문에 분석 세션을 종료하거나 사용자의 추가 입력을 기다리게 하지 않는다. Report 생성에 시간이 걸리는 경우에도 기존 interactive session을 계속 사용할 수 있도록 작업을 분리한다.

새로운 분석 요청이 들어오면 기존 report 생성을 기다리지 말고 가능한 범위에서 분석을 계속 진행한다. 이후 분석 결과가 변경되거나 추가되면 필요에 따라 report를 갱신하거나 새 버전을 생성한다.

core_marker.xlsx는 celltype별 핵심 marker 목록을 담고 있는 참조 파일이다. 사용자의 명시적인 지시가 있거나 annotation 결과를 검증하는 단계가 아닌 이상 이 파일을 사용하지 않는다.

skill을 작성하거나 분석 결과에 대한 근거를 설명할 때는 항상 한글로 작성한다.

코드를 작성해야 할 때는 기본적으로 notebooks/에 새 노트북을 추가하지 말고 scripts/ 안에 script 파일로 작성한다. notebooks/는 탐색적 분석, 시각적 검토, 결과 해석 등 interactive한 용도로만 사용자가 명시적으로 요청했을 때 사용한다.