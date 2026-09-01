---
name: scrnaseq-stepwise-hitl
description: 단일세포 RNA-seq 분석을 한 단계씩 진행하며 판단이 갈리는 지점마다 멈춰 사용자에게 선택지를 제시하는 human-in-the-loop 방식으로 계획하고 실행한다. 연구 질문만 받아서 Task/Objective/Dataset/Path 를 코드베이스 탐색과 질문으로 채운 뒤, QC 부터 한 단계씩 진행하며 매 갈림길에서 승인을 받는다. scrnaseq-plan-execute 와 짝을 이루는 진행 방식이며, 자율 실행 대신 단계별 개입을 원할 때 쓴다. 트리거: "단계별로 물어보면서 분석해줘", "/scrnaseq-stepwise-hitl".
---

이 스킬은 `scrnaseq-plan-execute` 와 **같은 형식**(Task/Objective/Dataset/Path, 8단계 구조,
step-validator 검증)을 쓰지만 **진행 방식이 다르다.** 전체 계획을 한 번에 승인받지 않고,
**한 단계씩 진행하며 매 갈림길에서 멈춰 사용자에게 묻는다.**

두 스킬이 같은 실험을 다른 진행 방식으로 도는 짝이라면(예: 같은 데이터·같은 질문을
worktree 두 개로 나눠 비교), Task/Objective/Dataset/Path 를 두 세션에서 동일하게 맞춘다 —
달라지는 것은 이 스킬의 진행 방식뿐이어야 비교가 성립한다.

## 0. 전제 확인

`.claude/agents/step-validator.md` 가 이 저장소에 있는지 확인한다. 없으면 사용자에게 알린다.

## 1. Task / Objective / Dataset / Path 를 채운다

`scrnaseq-plan-execute` 의 1단계와 같은 절차를 따른다 — 연구 질문(Task)을 받고,
코드베이스를 탐색해 Dataset 을 실측으로 확인하고(짐작 금지), Objective 를 구체화하고,
Path(입력·참조·작업 디렉토리)를 채운 뒤 사용자에게 확인받는다.

## 2. 단계 구조를 이 연구 질문에 맞게 조립한다

`scrnaseq-plan-execute` 의 2단계와 같은 원칙으로 QC → 정규화/HVG → 배치 통합 →
clustering → annotation → 조건 간 차등발현 → 조건 간 기능 분석 → REPORT 구조를 조립하되,
조건 변수·마커·양성 대조는 이 Dataset 에 맞게 다시 채운다. 기능 분석 단계가 필요하면
`decoupler-cheatsheet` 스킬을 먼저 읽는다.

## 3. 진행 방식 — 여기가 plan-execute 와 다른 지점

- **계획을 한 번에 세우지 않는다.** QC 부터 시작해서 한 단계씩 간다.
- 각 단계를 끝낼 때마다 (1) 무엇을 했고 어떤 수치가 나왔는지, (2) 이 단계에서 판단이
  갈리는 지점과 선택지 2~3개를 근거와 함께 제시하고 **멈춘다.** 사용자가 고르기 전에
  스스로 정하고 다음 단계로 넘어가지 않는다.
- 사용자가 고른 선택은 `EXPERIMENT.md` 결정 로그에 `decided_by: human` 으로 남긴다.
  사용자가 "알아서 해" 라고 맡긴 것만 `claude` 로 남긴다.
- 수치를 지어내지 않는다. 없으면 없다고 적는다.
- 사용자가 원하면, 다음 단계로 넘어가기 전에 `step-validator` 서브에이전트로 방금 끝낸
  단계를 채점하고 결과를 보여준 뒤 그 점수를 보고 선택하게 한다. 결과는
  `results/validation/<번호>_<단계>.md` 에 저장한다.

배치 통합 단계에서는 다음을 반드시 사용자에게 되묻는다 — **조건 변수를 통계 검정의
batch_key 로 보정할 것인가, 아니면 clustering/annotation 목적의 시각화용 임베딩에만
보정을 걸고 통계 입력은 원본으로 남길 것인가.** 이 선택이 결과를 가장 크게 가른다.

## 4. 끝났을 때

`results/summary/metrics.json` 과 `EXPERIMENT.md` 결정 로그를 채운다. 사용자가 고른 것과
Claude 가 고른 것을 `decided_by` 로 구분해서 보여준다. 채점을 돌린 단계는 validation 결과를
함께 정리한다.
