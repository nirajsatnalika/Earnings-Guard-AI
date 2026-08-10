import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from datetime import datetime

from app.calculations.efs.engine import EFSEngine
from app.reports.report import jinja_env, WEASYPRINT_AVAILABLE, WEASYPRINT_ERROR, HTML

def main():
    analysis_id = "sample_analysis_001"
    engine = EFSEngine()
    result = engine.run(analysis_id=analysis_id, input_payload={})
    
    print(f"Engine run complete for analysis_id: {result.analysis_id}")
    print(f"Assessment ID: {result.assessment_id}")
    print(f"Status: {result.status}")
    print(f"Overall Score: {result.overall.score}")
    print(f"Score Status: {result.overall.score_status}")
    
    template = jinja_env.get_template("report.html")
    html_content = template.render(
        assessment=result,
        generated_at=datetime.utcnow().isoformat() + "Z",
    )
    
    html_path = Path("scratch/sample_report.html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"Wrote HTML preview to: {html_path.resolve()}")
    
    if WEASYPRINT_AVAILABLE:
        try:
            pdf_bytes = HTML(string=html_content).write_pdf()
            company_name = getattr(result, "company_name", "Company")
            safe_company = "".join(c for c in company_name if c.isalnum() or c in "_- ")
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            filename = f"EFS_Assessment_{safe_company}_{today_str}.pdf"
            pdf_path = Path("scratch") / filename
            pdf_path.write_bytes(pdf_bytes)
            print(f"Successfully generated PDF: {pdf_path.resolve()}")
            print(f"PDF size: {len(pdf_bytes)} bytes")
        except Exception as e:
            print(f"WeasyPrint rendering error: {e}")
    else:
        print(f"WeasyPrint unavailable: {WEASYPRINT_ERROR}")

if __name__ == "__main__":
    main()
