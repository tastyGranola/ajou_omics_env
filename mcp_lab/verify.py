#!/usr/bin/env python3
"""
환경 점검 — 실습 전에 한 번 돌리세요.

    python3 mcp_lab/verify.py

'환경' 만 봅니다. .mcp.json 은 실습에서 직접 채우므로 검사하지 않습니다.
"""
import os
import shutil
import subprocess
import sys
import urllib.request

OK   = "  \033[32m✓\033[0m"
NO   = "  \033[31m✗\033[0m"
WARN = "  \033[33m·\033[0m"
fails: list[str] = []
warns: list[str] = []


def check(name, ok, detail="", fix="", warn_only=False):
    print(f"{OK if ok else (WARN if warn_only else NO)} {name}"
          f"{('  — ' + detail) if detail else ''}")
    if not ok:
        (warns if warn_only else fails).append(f"{name}\n      → {fix}")
    return ok


def reachable(url, timeout=8):
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except urllib.error.HTTPError:
        return True          # 응답이 왔으면 망은 열린 것
    except Exception:
        return False


def main() -> int:
    print("\n환경 점검\n")

    v = sys.version_info
    check("Python 3.10 이상", v >= (3, 10), f"{v.major}.{v.minor}.{v.micro}",
          "Python 3.10 이상이 필요합니다 (mcp 패키지 요구사항)")

    try:
        import importlib.metadata as md
        check("mcp 패키지", True, f"v{md.version('mcp')}")
    except Exception:
        check("mcp 패키지", False, "없음",
              "python3 -m pip install -r .devcontainer/requirements.txt")

    uvx = shutil.which("uvx")
    check("uvx  (실습 ③ 용)", uvx is not None, uvx or "없음",
          "python3 -m pip install uv")

    claude = shutil.which("claude")
    check("claude 명령", claude is not None, claude or "PATH 에 없음",
          "npm install -g @anthropic-ai/claude-code  후 새 터미널")

    check("바깥 인터넷 (실습 ③ 용)",
          reachable("https://biocontext-kb.fastmcp.app/mcp/"), "",
          "네트워크 정책일 수 있습니다. 실습 ③의 원격 부분은 건너뛰어도 됩니다",
          warn_only=True)

    env_key = os.environ.get("ANTHROPIC_API_KEY")
    logged_in = os.path.exists(os.path.expanduser("~/.claude.json"))
    check("Claude Code 인증", bool(env_key or logged_in),
          "ANTHROPIC_API_KEY 있음" if env_key
          else "설정 파일 있음 — 첫 실행 때 확인됩니다" if logged_in
          else "아직 없음 — claude 를 실행하면 안내가 나옵니다",
          "claude 를 실행하고 안내를 따르세요", warn_only=True)

    print()
    for w in warns:
        print("  ·", w)
    if warns:
        print()
    if fails:
        print(f"\033[31m{len(fails)}개가 준비되지 않았습니다.\033[0m\n")
        for f in fails:
            print("  •", f)
        print()
        return 1
    print("\033[32m준비 완료.  mcp_lab/LAB.md 의 실습 ① 로 가세요.\033[0m\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
