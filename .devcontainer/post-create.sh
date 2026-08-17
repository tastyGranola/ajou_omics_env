#!/usr/bin/env bash
# Codespace 가 처음 만들어질 때 한 번 실행됩니다.
set -euo pipefail

echo "▶ pip 업그레이드"
python -m pip install --upgrade pip

echo "▶ single-cell 분석 패키지 설치 (수 분 소요)"
pip install --no-cache-dir -r .devcontainer/requirements.txt

echo "▶ Jupyter 커널 등록"
python -m ipykernel install --user --name ajou-omics --display-name "Python (ajou-omics)"

echo "▶ Claude Code CLI 설치"
npm install -g @anthropic-ai/claude-code

echo "✅ 환경 준비 완료"
python - <<'PY'
import anndata, scanpy
print(f"   scanpy {scanpy.__version__} / anndata {anndata.__version__}")
PY
