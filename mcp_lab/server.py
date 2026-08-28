"""
오믹스 분석 MCP 서버 — 2일차 1교시 실습용

도구 세 개가 들어 있습니다.
계산은 하지 않고, 미리 넣어둔 값을 돌려줍니다.

  오늘 볼 것    : 붙이고 · 부르고 · 막는다
  2교시에 볼 것 : 이 숫자들이 무슨 뜻인가

실행은 Claude Code 가 알아서 합니다. 직접 켜지 않아도 됩니다.
"""

# mcp 패키지 버전에 따라 이름이 다릅니다. 둘 다 받습니다.
try:
    from mcp.server.mcpserver import MCPServer as _Server      # mcp 2.x
except ImportError:                                            # pragma: no cover
    from mcp.server.fastmcp import FastMCP as _Server          # mcp 1.x

mcp = _Server("sc-omics")


# ────────────────────────────────────────────────────────────
#  미리 계산해둔 결과. 실제로 돌리면 수십 분 걸리는 것들입니다.
# ────────────────────────────────────────────────────────────

DATASET = {
    "설명": "치료 전 종양 조직 단일세포 RNA-seq",
    "세포_수": 12000,
    "유전자_수": 18000,
    "샘플": {"반응군": ["R1", "R2", "R3"], "비반응군": ["N1", "N2", "N3"]},
    "배치": {"batch1": ["R1", "R2", "R3", "N1"], "batch2": ["N2", "N3"]},
    "주의": "배치와 군이 부분적으로 얽혀 있습니다.",
    "안내": "발현 행렬은 이 서버 밖으로 나가지 않습니다. 요약만 돌려줍니다.",
}

# 배치 보정을 안 했을 때 — 리보솜·미토콘드리아가 상위를 덮습니다
DE_UNCORRECTED = {
    "유의_유전자_수": 4231,
    "상위10": ["MT-CYB", "RPS27", "MT-ATP6", "MT-CO1", "ACTB",
               "RPL13A", "EEF1A1", "MALAT1", "TMSB4X", "RPL10"],
    "메모": "배치를 보정하지 않았습니다.",
}

# 배치 보정을 했을 때 — 항원제시 · IFN-γ 반응이 올라옵니다
DE_CORRECTED = {
    "유의_유전자_수": 187,
    "상위10": ["IRF1", "B2M", "TAP1", "CXCL10", "GBP1",
               "HLA-A", "STAT1", "CXCL9", "PSMB9", "HLA-B"],
    "메모": "배치를 covariate 로 넣고 검정했습니다.",
}

CELL_TYPES = ["종양세포", "CD4 T세포", "소진 CD8 T세포", "활성 CD8 T세포",
              "전구 CD8 T세포", "골수계", "MDSC 유사", "B세포",
              "섬유아세포", "내피세포"]

_RUNS: dict[str, dict] = {}          # 서버가 들고 있는 상태


# ────────────────────────────────────────────────────────────
#  도구 ①
# ────────────────────────────────────────────────────────────

@mcp.tool()
def dataset_overview() -> dict:
    """데이터셋의 규모 · 샘플 · 군 · 배치 구성을 돌려줍니다.

    발현 행렬 자체는 돌려주지 않습니다. 분석을 시작하기 전에 먼저 부르세요.
    """
    return DATASET


# ────────────────────────────────────────────────────────────
#  도구 ②
# ────────────────────────────────────────────────────────────

@mcp.tool()
def run_pipeline(normalize: bool = True, integrate: bool = False) -> dict:
    """전처리 파이프라인을 실행하고 run_id 를 돌려줍니다.

    결과 데이터가 아니라 손잡이(run_id)만 옵니다.
    이후 분석 도구는 이 run_id 로 부릅니다.

    Args:
        normalize: 정규화 수행 여부
        integrate: 배치 통합 수행 여부
    """
    run_id = "r_int" if integrate else "r_raw"
    _RUNS[run_id] = {"normalize": normalize, "batch_corrected": integrate}
    return {
        "run_id": run_id,
        "batch_corrected": integrate,
        "클러스터_수": 11 if integrate else 14,
        "상태": "완료",
    }


# ────────────────────────────────────────────────────────────
#  도구 ③  ←  실습 ② 에서 여기에 직접 넣습니다.
#
#  위의 DE_UNCORRECTED / DE_CORRECTED 는 이미 준비되어 있습니다.
#  README 의 "실습 ②" 코드를 이 아래에 붙여 넣으세요.
# ────────────────────────────────────────────────────────────


if __name__ == "__main__":
    mcp.run()
