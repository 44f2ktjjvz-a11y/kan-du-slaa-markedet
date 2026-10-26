"""Byg index.html (den offentlige app) og local/slides.html (præsentationen, publiceres aldrig)."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
APP_URL = (root / "src" / "app_url.txt").read_text(encoding="utf-8").strip() if (root / "src" / "app_url.txt").exists() else ""
data = json.dumps(json.loads((root / "data" / "returns.json").read_text(encoding="utf-8")),
                  ensure_ascii=False, separators=(",", ":"))

def build(tpl_path, out_path, extra=None, payload=None):
    tpl = tpl_path.read_text(encoding="utf-8")
    assert "/*DATA*/null" in tpl
    out = tpl.replace("/*DATA*/null", payload or data)
    for k, v in (extra or {}).items():
        assert k in out
        out = out.replace(k, v)
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(out, encoding="utf-8", newline="\n")
    print(out_path.relative_to(root), len(out), "bytes")

build(root / "src" / "index.template.html", root / "index.html")
build(root / "src" / "hvadnu.template.html", root / "hvadnu.html", {"/*NEWS*/": (root / "src" / "news.js").read_text(encoding="utf-8")})
build(root / "src" / "portefolje.template.html", root / "portefolje.html",
      payload=(root / "data" / "builder.json").read_text(encoding="utf-8"))
# præsentationen og dens kilde ligger i local/, som git ignorerer: den må aldrig blive offentlig
build(root / "local" / "slides.template.html", root / "local" / "slides.html", {'/*APP_URL*/""': json.dumps(APP_URL)})

# Din første million som egen side uden menu og uden links til de andre opgaver
_t = (root / "src" / "index.template.html").read_text(encoding="utf-8").replace("<body>", '<body data-solo="g3">', 1)
_p = root / "src" / "_million.template.html"
_p.write_text(_t, encoding="utf-8")
build(_p, root / "million.html")
_p.unlink()
