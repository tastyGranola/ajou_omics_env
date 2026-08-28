#!/usr/bin/env bash
# 병렬 실험 worktree 와 branch 를 정리한다.
#
#   bash parallel_lab/cleanup.sh          # 무엇이 지워지는지 보여주기만 한다
#   bash parallel_lab/cleanup.sh --yes    # 실제로 지운다
#
# 주의 — worktree 를 지우면 그 안의 results/ figures/ 도 함께 사라집니다.
#        남기고 싶은 것은 먼저 comparison/ 으로 복사하세요.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

YES=0
[ "${1:-}" = "--yes" ] && YES=1

if [ ! -d worktrees ]; then
  echo "worktrees/ 가 없습니다. 정리할 것이 없습니다."
  exit 0
fi

TARGETS=()
for wt in worktrees/*/; do
  if [ -d "$wt" ]; then TARGETS+=("${wt%/}"); fi
done

if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "worktrees/ 가 비어 있습니다."
  exit 0
fi

count_files() {
  find "$1/results" "$1/figures" -type f 2>/dev/null | wc -l | tr -d ' '
}

echo "지워질 것:"
for t in "${TARGETS[@]}"; do
  n=$(basename "$t")
  files=$(count_files "$t" || true)
  echo "    $t  (산출물 ${files:-0} 개)  + branch exp/$n"
done
echo
echo "comparison/ 은 지우지 않습니다."

if [ "$YES" -eq 0 ]; then
  echo
  echo "실제로 지우려면:  bash parallel_lab/cleanup.sh --yes"
  exit 0
fi

echo
for t in "${TARGETS[@]}"; do
  n=$(basename "$t")
  git worktree remove --force "$t" && echo "✓ worktree 제거 $t"
  git branch -D "exp/$n" >/dev/null 2>&1 && echo "✓ branch 삭제 exp/$n" || true
done
git worktree prune
rmdir worktrees 2>/dev/null || true
echo
git worktree list
