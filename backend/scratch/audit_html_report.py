import re
from pathlib import Path

def audit_html():
    html_path = Path("scratch/sample_report.html")
    content = html_path.read_text(encoding="utf-8")
    
    checks = {
        "A4 page size": "@page { size: A4;" in content,
        "Cover page section": 'id="cover"' in content,
        "Headers/Footers": 'class="footer"' in content,
        "CALIBRATION PENDING": "CALIBRATION PENDING" in content,
        "No fabricated score": "Overall Score: None" not in content and 'Score Status: CALIBRATION_PENDING' not in content,
        "Executive Summary": 'id="executive-summary"' in content,
        "Seven Pillars Overview": 'id="pillars-overview"' in content,
        "Established Models": 'id="established-models"' in content,
        "Forensic Findings": 'id="forensic-findings"' in content,
        "Key Red Flags": 'id="red-flags"' in content,
        "Management Questions": 'id="management-questions"' in content,
        "Investigation Priorities": 'id="investigation-priorities"' in content,
        "Confidence & Data Quality": 'id="confidence-data"' in content,
        "Methodology": 'id="methodology"' in content,
        "Important Limitations": 'id="limitations"' in content,
        "Audit Trail": 'id="audit-trail"' in content,
    }
    
    print("=== HTML REPORT AUDIT RESULTS ===")
    all_passed = True
    for key, val in checks.items():
        status = "PASS" if val else "FAIL"
        print(f"[{status}] {key}")
        if not val:
            all_passed = False
            
    # Check for established models
    models = ["Beneish", "Sloan", "Altman", "Piotroski", "Ohlson"]
    for m in models:
        present = m.lower() in content.lower()
        print(f"[{'PASS' if present else 'FAIL'}] Established Model: {m}")
        if not present:
            all_passed = False

    print("=================================")
    print(f"OVERALL HTML AUDIT: {'PASSED' if all_passed else 'FAILED'}")

if __name__ == "__main__":
    audit_html()
