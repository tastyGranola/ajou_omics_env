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

# Codespaces secret 으로 CLAUDE_CODE_OAUTH_TOKEN 이 등록되어 있으면 컨테이너 환경변수로
# 자동 주입되고, Claude Code CLI 와 VS Code 확장이 이를 그대로 사용한다.
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
  echo "▶ Claude Code: CLAUDE_CODE_OAUTH_TOKEN 감지 — 별도 로그인 없이 사용할 수 있습니다"
else
  echo "▶ Claude Code: 토큰이 없습니다. 터미널에서 'claude' 실행 후 로그인하거나,"
  echo "  GitHub Settings ▸ Codespaces ▸ Secrets 에 CLAUDE_CODE_OAUTH_TOKEN 을 등록하세요"
fi

echo "✅ 환경 준비 완료"
python - <<'PY'
import anndata, scanpy
print(f"   scanpy {scanpy.__version__} / anndata {anndata.__version__}")
PY
