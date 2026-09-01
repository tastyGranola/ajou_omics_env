#!/usr/bin/env python3
"""기능 분석에 쓸 prior knowledge 를 data/genesets/ 에 내려받아 캐시한다.

    python3 fetch_genesets.py             # 전부
    python3 fetch_genesets.py hallmark    # 하나만
    python3 fetch_genesets.py --force     # 이미 있어도 다시 받음
    python3 fetch_genesets.py --list      # 무엇을 받는지만 보여줌

왜 캐시하나
  dc.op.* 는 부를 때마다 omnipathdb.org 에 요청을 보낸다. 수강생 스무 명이 동시에
  치면 느리고, 오프라인이면 실습이 멈춘다. 그리고 원격 자원은 조용히 바뀐다 —
  같은 코드가 다른 결과를 내면 비교가 깨진다. 한 번 받아서 커밋해 두면
  모두가 같은 prior knowledge 로 같은 결과를 낸다.

산출물
  data/genesets/<이름>.csv.gz  long format — source, target (, weight)
  data/genesets/manifest.json  무엇을 언제 어디서 받았는지
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

TIMEOUT = 60
ENRICHR_GMT = "https://maayanlab.cloud/Enrichr/geneSetLibrary?mode=text&libraryName={name}"


# --- 저장 위치 -------------------------------------------------------------


def repo_root() -> pathlib.Path:
    """main 작업 트리의 루트. worktree 안에서 실행해도 main 을 가리킨다.

    data/genesets/ 는 실험이 만드는 것이 아니라 공용 입력이므로 main 한 곳에만 둔다.
    """
    try:
        out = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout
        for line in out.splitlines():
            if line.startswith("worktree "):
                return pathlib.Path(line[len("worktree "):])
    except (OSError, subprocess.CalledProcessError):
        pass
    return pathlib.Path(__file__).resolve().parent.parent


# --- 내려받기 --------------------------------------------------------------


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "ajou-omics-lab/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw


def from_enrichr(library: str) -> tuple[list[dict], str]:
    """Enrichr 의 GMT 엔드포인트에서 gene set 을 받는다.

    GMT 한 줄: <집합 이름>\\t<설명>\\t<유전자>\\t<유전자>...
    """
    url = ENRICHR_GMT.format(name=library)
    text = http_get(url).decode("utf-8")
    rows = []
    for line in io.StringIO(text):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3:
            continue
        source = parts[0].strip()
        for gene in parts[2:]:
            gene = gene.split(",")[0].strip()   # Enrichr 는 가끔 "GENE,1.0" 으로 준다
            if gene:
                rows.append({"source": source, "target": gene})
    if not rows:
        raise RuntimeError(f"Enrichr 라이브러리 '{library}' 가 비어 있습니다")
    return rows, url


def from_decoupler(fn_name: str, **kwargs) -> tuple[list[dict], str]:
    """decoupler.op 의 함수를 불러 omnipath 자원을 받는다."""
    try:
        import decoupler as dc
    except ImportError:
        raise RuntimeError(
            "decoupler 가 설치되어 있지 않습니다 — pip install 'decoupler>=2.2,<3'"
        ) from None

    if not hasattr(dc, "op"):
        raise RuntimeError(
            f"decoupler {getattr(dc, '__version__', '?')} 은 1.x 입니다. "
            "이 실습은 2.x 가 필요합니다 — pip install -U 'decoupler>=2.2,<3'"
        )

    df = getattr(dc.op, fn_name)(**kwargs)
    cols = [c for c in ("source", "target", "weight") if c in df.columns]
    if "source" not in cols or "target" not in cols:
        raise RuntimeError(
            f"dc.op.{fn_name} 이 예상과 다른 컬럼을 돌려줬습니다: {list(df.columns)}"
        )
    rows = df[cols].to_dict("records")
    return rows, f"decoupler.op.{fn_name}({', '.join(f'{k}={v!r}' for k, v in kwargs.items())})"


# --- 받을 목록 -------------------------------------------------------------

SOURCES = {
    "hallmark": {
        "종류": "gene set",
        "설명": "MSigDB Hallmark 50개 — 잘 정의된 생물학적 상태. 중복이 적어 해석하기 쉽다",
        "fetch": lambda: from_decoupler("hallmark", organism="human"),
        "메모": "source 이름에 HALLMARK_ 접두어가 없다 (INTERFERON_ALPHA_RESPONSE)",
    },
    "reactome": {
        "종류": "gene set",
        "설명": "Reactome 경로 — 큐레이션된 구성원. 집합이 많고 서로 중복이 심하다",
        "fetch": lambda: from_enrichr("Reactome_Pathways_2024"),
        "메모": "Enrichr 배포본. 작은 집합이 많으니 tmin 과 크기 상한을 꼭 걸 것",
    },
    "progeny": {
        "종류": "footprint",
        "설명": "PROGENy 신호경로 14개 — 하류 반응 유전자 + 부호 가중치",
        "fetch": lambda: from_decoupler("progeny", organism="human", top=500),
        "메모": "top=500. weight 의 부호가 활성/억제 방향이다",
    },
    "collectri": {
        "종류": "footprint",
        "설명": "CollecTRI 전사인자 → 표적 유전자 망 + 활성/억제 부호",
        "fetch": lambda: from_decoupler("collectri", organism="human"),
        "메모": "IFN 반응의 STAT1 · STAT2 · IRF9 를 여기서 본다",
    },
}


# --- 쓰기 ------------------------------------------------------------------


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    """gzip 압축한 CSV 로 쓴다. pandas.read_csv 가 확장자를 보고 알아서 풉니다."""
    fields = ["source", "target"] + (["weight"] if "weight" in rows[0] else [])
    tmp = path.with_name(path.name + ".tmp")
    with gzip.open(tmp, "wt", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(path)


def summarize(rows: list[dict]) -> dict:
    sizes: dict[str, int] = {}
    for r in rows:
        sizes[r["source"]] = sizes.get(r["source"], 0) + 1
    counts = sorted(sizes.values())
    return {
        "n_sources": len(sizes),
        "n_edges": len(rows),
        "size_min": counts[0],
        "size_median": counts[len(counts) // 2],
        "size_max": counts[-1],
        "n_sources_under_15": sum(1 for c in counts if c < 15),
    }


# --- 진행 ------------------------------------------------------------------


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help=f"받을 자원 ({' · '.join(SOURCES)}). 비우면 전부")
    ap.add_argument("--force", action="store_true", help="이미 있어도 다시 받는다")
    ap.add_argument("--list", action="store_true", help="목록만 보여주고 끝낸다")
    args = ap.parse_args(argv)

    if args.list:
        print(f"{'이름':<12}{'종류':<12}설명")
        print("-" * 78)
        for name, spec in SOURCES.items():
            print(f"{name:<12}{spec['종류']:<12}{spec['설명']}")
        return 0

    unknown = [n for n in args.names if n not in SOURCES]
    if unknown:
        print(f"✗ 모르는 자원: {', '.join(unknown)}", file=sys.stderr)
        print(f"  쓸 수 있는 것: {' · '.join(SOURCES)}", file=sys.stderr)
        return 2

    wanted = args.names or list(SOURCES)
    outdir = repo_root() / "data" / "genesets"
    outdir.mkdir(parents=True, exist_ok=True)

    manifest_path = outdir / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError:
            manifest = {}

    print(f"저장 위치: {outdir}")
    print()

    results, failed = [], []
    for name in wanted:
        spec = SOURCES[name]
        dest = outdir / f"{name}.csv.gz"

        if dest.exists() and not args.force:
            info = manifest.get(name, {})
            print(f"· {name:<12} 이미 있음 — 건너뜁니다 "
                  f"({info.get('n_sources', '?')}개 집합). 다시 받으려면 --force")
            results.append((name, "캐시", info))
            continue

        print(f"↓ {name:<12} {spec['설명']}")
        try:
            rows, origin = spec["fetch"]()
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"  ✗ 네트워크 실패: {e}")
            failed.append((name, f"네트워크: {e}"))
            continue
        except Exception as e:                       # noqa: BLE001 — 어떤 실패든 표로 모은다
            print(f"  ✗ {type(e).__name__}: {e}")
            failed.append((name, f"{type(e).__name__}: {e}"))
            continue

        write_csv(dest, rows)
        info = summarize(rows)
        info.update({
            "origin": origin,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": spec["종류"],
            "file": f"data/genesets/{name}.csv.gz",
            "note": spec["메모"],
        })
        manifest[name] = info
        print(f"  ✓ 집합 {info['n_sources']}개 · 엣지 {info['n_edges']:,}개 "
              f"· 크기 {info['size_min']}~{info['size_max']} (중앙값 {info['size_median']})")
        if info["n_sources_under_15"]:
            if spec["종류"] == "gene set":
                print(f"    ※ 15개 미만인 집합이 {info['n_sources_under_15']}개 있습니다 "
                      f"— tmin=15 로 걸러집니다")
            else:
                print(f"    ※ target 이 15개 미만인 source 가 {info['n_sources_under_15']}개입니다. "
                      f"footprint 에는 tmin=15 를 걸지 마세요 — 대부분이 사라집니다")
        results.append((name, "받음", info))

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print()
    print(f"manifest: {manifest_path}")
    if failed:
        print()
        print("실패한 것:")
        for name, why in failed:
            print(f"  ✗ {name:<12} {why}")
        print()
        if any("CERTIFICATE_VERIFY_FAILED" in why for _, why in failed):
            print("  CERTIFICATE_VERIFY_FAILED 는 재시도해도 안 풀립니다.")
            print("  이 파이썬에 CA 번들이 없는 것이라 아래 중 하나로 해결합니다.")
            print("    - macOS 공식 설치본:  /Applications/Python\\ 3.x/Install\\ Certificates.command")
            print("    - 그 밖:              pip install -U certifi")
            print("                          export SSL_CERT_FILE=$(python3 -m certifi)")
            print()
        print("  일시적인 네트워크 문제면 잠시 뒤 다시 시도하세요.")
        print("  계속 안 되면 MSigDB 에서 GMT 를 직접 받아 data/genesets/ 에 두고")
        print("  dc.pp.read_gmt(경로) 로 읽어도 됩니다 — https://www.gsea-msigdb.org/gsea/msigdb")
        return 1

    print()
    print("다음:  python3 verify.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
