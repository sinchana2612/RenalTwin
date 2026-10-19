import json
from pathlib import Path
p=Path("artifacts/models/v1/metrics.json"); out=Path("artifacts/reports/evaluation_report.md");out.parent.mkdir(parents=True,exist_ok=True)
if not p.exists(): raise SystemExit("Run training first; metrics.json not found")
m=json.loads(p.read_text()); out.write_text("# RenalTwin Synthetic Evaluation Report\n\n> Research prototype. Synthetic simulator results are not clinical evidence.\n\n```json\n"+json.dumps(m,indent=2)+"\n```\n");print(out)
