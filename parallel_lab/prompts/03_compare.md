# 세션 C — 비교

실행 위치: **저장소 루트** (main 작업 트리)

```bash
cd /workspaces/ajou-omics-env && claude
```

앞의 두 창은 닫지 않아도 됩니다. 세 번째 터미널을 새로 엽니다.

---

## 여는 프롬프트 — 그대로 붙여 넣으세요

```
worktrees/ 아래 두 실험을 비교해줘.

각 실험의 EXPERIMENT.md 와 results/summary/metrics.json, results/, figures/ 를 읽고
comparison/comparison_report.html 과 comparison/comparison.md 를 만들어줘.

이걸 꼭 담아줘.
  1. 같은 데이터·같은 질문인데 결과 수치가 어디서 얼마나 갈렸는지
  2. 그 차이를 만든 결정이 무엇이었는지 — 갈라진 지점을 짚어줘
  3. 각 결정을 누가 했는지 (claude / human) 를 세어서 두 실험을 대비시켜줘
  4. 어느 쪽이 옳은지 이 데이터로 판단할 수 없는 항목은 그렇다고 명시해줘

실험 worktree 안의 파일은 고치지 마.
```

## 이어서 물어볼 것들

```
두 실험이 처음으로 갈라진 지점이 어디야? 그 앞까지는 얼마나 같았어?
```

```
사람이 개입한 결정 중에 결과를 가장 크게 바꾼 건 뭐야?
```

```
세션 A 가 혼자 내린 결정 중에, 내가 봤다면 다르게 골랐을 만한 게 있어?
```

## 남길 것

```
comparison/comparison.md 마지막에 "다음에 시험해 볼 아이디어" 를 세 개만 적어줘.
각각 어떤 branch 이름으로 실험하면 좋을지도 같이.
```

그 세 개를 그대로 다음 실습으로 넘길 수 있습니다.

```bash
bash parallel_lab/setup.sh <아이디어-1> <아이디어-2> <아이디어-3>
```
