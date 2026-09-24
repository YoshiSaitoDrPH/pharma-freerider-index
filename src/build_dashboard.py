"""Inject data/processed/results.json into dashboard/template.html -> dashboard/index.html (self-contained)."""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[1]
data = (ROOT / "data" / "processed" / "results.json").read_text()
html = (ROOT / "dashboard" / "template.html").read_text().replace("__DATA__", data)
(ROOT / "dashboard" / "index.html").write_text(html)
print("dashboard/index.html written", len(html), "bytes")
