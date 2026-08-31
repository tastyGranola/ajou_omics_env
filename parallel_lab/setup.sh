#!/usr/bin/env bash
# 병렬 실험용 git worktree 를 만든다.
#
#   bash parallel_lab/setup.sh                 # 2일차 2교시 기본 실험 두 개
#   bash parallel_lab/setup.sh harmony scvi    # 임의의 아이디어 이름으로 N 개
#
# 옵션
#   --ignore-dirty   커밋되지 않은 변경이 있어도 진행한다
set -euo pipefail

# 항상 main 작업 트리를 기준으로 동작한다.
# parallel_lab/ 은 각 worktree 에도 링크되어 있어서, 스크립트 위치로 루트를 잡으면
# worktree 안에서 실행했을 때 자기 자신을 루트로 착각한다.
ROOT="$(git worktree list --porcelain 2>/dev/null | sed -n '1s/^worktree //p')"
if [ -z "$ROOT" ] || [ ! -d "$ROOT/.git" ]; then
  echo "✗ git 저장소 안에서 실행하세요." >&2
  exit 1
fi
HERE="$(pwd)"
cd "$ROOT"
if [ "$HERE" != "$ROOT" ] && [ "${HERE#$ROOT/worktrees/}" != "$HERE" ]; then
  echo "· 실험 worktree 안에서 실행했습니다 — main($ROOT) 기준으로 동작합니다"
fi

# main 과 공유할 것 — 실험이 만들지 않고 읽기만 하는 공용 입력·도구.
# 이 경로들은 복사하지 않고 main 을 가리키는 심볼릭 링크로 건다.
# data/processed/ 는 분석 중간 데이터가 쌓이는 곳이라 공유하지 않는다 (실험마다 따로).
# .claude/agents/ 는 검증 에이전트다. 실험마다 다르면 검증 기준이 달라져 비교가 깨지므로 공유한다.
# data/genesets/ 는 기능 분석의 prior knowledge 캐시다. 실험마다 다른 gene set 을 받으면
#   "gene set 을 바꿨더니 결과가 달라졌다" 를 말할 수 없으므로 공유한다.
#   ★ git 에 커밋되어 있어야 링크가 걸린다 (link_shared.py 가 git ls-files 를 쓴다).
SHARED=(data/raw data/genesets mcp_lab parallel_lab .devcontainer .claude/agents core_markers.xlsx)

IGNORE_DIRTY=0
NAMES=()
for arg in "$@"; do
  case "$arg" in
    --ignore-dirty) IGNORE_DIRTY=1 ;;
    -*) echo "모르는 옵션입니다: $arg" >&2; exit 1 ;;
    *)  NAMES+=("$arg") ;;
  esac
done
if [ ${#NAMES[@]} -eq 0 ]; then
  NAMES=(plan-execute stepwise-hitl)
fi

# --- 사전 점검 -------------------------------------------------------------

if [ ! -d .git ]; then
  echo "✗ main 작업 트리에서 실행하세요. (지금 위치: $ROOT)" >&2
  exit 1
fi

DIRTY="$(git status --porcelain)"
if [ -n "$DIRTY" ] && [ "$IGNORE_DIRTY" -eq 0 ]; then
  echo "✗ 커밋되지 않은 변경이 있습니다. worktree 는 마지막 커밋을 기준으로 만들어지므로"
  echo "  아래 변경들은 실험 worktree 에 들어가지 않습니다."
  echo
  echo "$DIRTY" | sed 's/^/    /'
  echo
  echo "  둘 중 하나를 고르세요."
  echo "    1) 지금 상태를 실험의 출발점으로 삼는다"
  echo "         git add -A && git commit -m '병렬 실험 출발점'"
  echo "         bash parallel_lab/setup.sh"
  echo "    2) 마지막 커밋을 출발점으로 삼고 위 변경은 main 에만 둔다"
  echo "         bash parallel_lab/setup.sh --ignore-dirty"
  exit 1
fi

BASE="$(git rev-parse --abbrev-ref HEAD)"
mkdir -p worktrees

# --- 실험별 설명 -----------------------------------------------------------

describe() {
  case "$1" in
    plan-execute)
      echo "전체 계획을 먼저 세우고, 한 번 승인받은 뒤 끝까지 자율 실행한다" ;;
    stepwise-hitl)
      echo "한 단계씩 진행하고, 판단이 갈리는 지점마다 멈춰 사람에게 묻는다" ;;
    *)
      echo "(아이디어 설명을 EXPERIMENT.md 에 직접 적으세요)" ;;
  esac
}

rules_block() {
  case "$1" in
    plan-execute)
      cat <<'BLOCK'
사용자가 목표를 주면 먼저 전체 분석 계획을 세워 제시하고 승인을 받는다. 승인 이후에는 사용자에게 되묻지 않고 계획을 끝까지 실행한다.

실행 중 판단이 갈리는 지점을 만나면 멈추지 말고 스스로 결정한다. 대신 무엇을 골랐고 왜 골랐는지, 그리고 고르지 않은 대안이 무엇이었는지를 EXPERIMENT.md 결정 로그에 남긴다. 이때 decided_by 는 claude 다.

계획을 벗어나야 할 이유가 생기면 실행을 멈추지 말고 벗어난 뒤, 무엇이 왜 달라졌는지를 결정 로그에 기록한다.

모든 단계가 끝나면 results/summary/metrics.json 과 results/summary/report.html 을 완성하고 사용자에게 결과를 보고한다.
BLOCK
      ;;
    stepwise-hitl)
      cat <<'BLOCK'
한 번에 한 단계만 진행한다. 사용자가 다음으로 가자고 하기 전에는 다음 단계로 넘어가지 않는다.

각 단계를 끝낼 때마다 (1) 무엇을 했고 어떤 수치가 나왔는지, (2) 이 단계에서 판단이 갈리는 지점과 선택지 2~3개를 근거와 함께 제시하고 멈춘다. 선택지를 제시한 뒤에는 사용자의 답을 기다린다. 스스로 고르고 진행하지 않는다.

사용자가 고른 선택은 EXPERIMENT.md 결정 로그에 decided_by 를 human 으로 기록한다. 사용자가 "알아서 해"라고 맡긴 경우에만 claude 로 기록한다.

여러 단계를 한 번에 처리해 달라는 요청이 아니라면 단계를 묶어서 진행하지 않는다.
BLOCK
      ;;
    *)
      cat <<'BLOCK'
이 실험의 아이디어와 진행 방식은 EXPERIMENT.md 에 적혀 있다. 세션을 시작할 때 EXPERIMENT.md 를 먼저 읽고 그 방식대로 진행한다.
BLOCK
      ;;
  esac
}

# --- worktree 생성 ---------------------------------------------------------

for NAME in "${NAMES[@]}"; do
  BRANCH="exp/$NAME"
  DIR="worktrees/$NAME"

  if [ -e "$DIR" ]; then
    echo "· $DIR 이미 있습니다 — 건너뜁니다"
    continue
  fi

  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    if ! OUT="$(git worktree add --no-checkout "$DIR" "$BRANCH" 2>&1)"; then
      echo "$OUT" >&2; exit 1
    fi
    NOTE="기존 branch $BRANCH 재사용"
  else
    if ! OUT="$(git worktree add --no-checkout -b "$BRANCH" "$DIR" "$BASE" 2>&1)"; then
      echo "$OUT" >&2; exit 1
    fi
    NOTE="branch $BRANCH ← $BASE"
  fi

  # 공유할 경로는 체크아웃하지 않고 main 을 가리키는 심볼릭 링크로 건다.
  #   read-tree        index 만 채운다 (파일은 아직 안 쓴다)
  #   skip-worktree    공유 경로를 "작업 트리에서 신경 쓰지 마라" 로 표시
  #   checkout-index   나머지만 실제로 꺼낸다
  git -C "$DIR" read-tree HEAD
  python3 "$ROOT/parallel_lab/link_shared.py" "$ROOT" "$ROOT/$DIR" "${SHARED[@]}"
  git -C "$DIR" checkout-index -a
  python3 "$ROOT/parallel_lab/link_shared.py" --link "$ROOT" "$ROOT/$DIR" "${SHARED[@]}"
  echo "✓ $DIR   ($NOTE)"

  # CLAUDE.md — 공통 지침 + 이 실험의 진행 방식
  if [ -f CLAUDE.md ]; then
    cp CLAUDE.md "$DIR/CLAUDE.md"
  else
    cp CLAUDE.example.md "$DIR/CLAUDE.md"
  fi
  {
    echo
    echo
    echo "## 이 작업 트리는 실험 \"$NAME\" 이다"
    echo
    echo "branch: $BRANCH"
    echo
    rules_block "$NAME"
  } >> "$DIR/CLAUDE.md"

  # 1교시에서 채운 .mcp.json 을 그대로 물려준다
  [ -f .mcp.json ] && cp .mcp.json "$DIR/.mcp.json"

  # EXPERIMENT.md — 실험 카드
  cat > "$DIR/EXPERIMENT.md" <<MD
# 실험 — $NAME

| | |
|---|---|
| branch | \`$BRANCH\` |
| 작업 트리 | \`$DIR\` |
| 목표 | IFN-beta 자극에 대한 PBMC 세포 타입별 반응 차이를 규명한다 |
| 진행 방식 | $(describe "$NAME") |

## 아이디어

<!-- 이 실험에서 무엇을 시험해 보려는지 한두 문단으로 적는다. -->

## 결정 로그

판단이 갈린 지점을 만날 때마다 아래 표에 한 줄씩 더한다.
같은 내용을 \`results/summary/metrics.json\` 의 \`decisions\` 에도 남긴다.

| 단계 | 갈린 지점 | 선택 | 근거 | 결정 주체 |
|---|---|---|---|---|
| | | | | |

## 진행 상황

- [ ] QC
- [ ] 정규화 · HVG
- [ ] 배치 통합 · 차원축소
- [ ] Clustering
- [ ] Cell type annotation
- [ ] 조건 간 차등발현
- [ ] 조건 간 기능 분석 (GSEA · pathway)
- [ ] \`results/summary/metrics.json\`
- [ ] \`results/summary/report.html\`
MD

done

# --- 안내 ------------------------------------------------------------------

echo
git worktree list
echo
echo "다음 — 실험마다 VS Code 터미널을 하나씩 열고 그 안에서 claude 를 띄웁니다."
for NAME in "${NAMES[@]}"; do
  echo "    cd $ROOT/worktrees/$NAME && claude"
done
echo
echo "여는 프롬프트는 parallel_lab/prompts/ 에 있습니다."
echo "진행 상황 확인:  bash parallel_lab/status.sh"
