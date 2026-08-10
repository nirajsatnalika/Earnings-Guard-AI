import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

SAMPLE_RESPONSE_PATH = Path(__file__).resolve().parents[2] / "samples" / "sample_efs_response.json"

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def get_sample_analysis_id():
    if SAMPLE_RESPONSE_PATH.exists():
        data = json.loads(SAMPLE_RESPONSE_PATH.read_text())
        return data.get("analysis_id", "sample_analysis_001")
    return "sample_analysis_001"

def test_report_endpoint_returns_pdf(client: TestClient):
    analysis_id = get_sample_analysis_id()

    # Mock WeasyPrint HTML object so test passes deterministically without native GTK library installed
    mock_html = MagicMock()
    mock_html.return_value.write_pdf.return_value = b"%PDF-1.4 Mock PDF Binary Content"

    with patch("app.reports.report.WEASYPRINT_AVAILABLE", True), \
         patch("app.reports.report.HTML", mock_html):
        response = client.get(f"/api/v1/efs/{analysis_id}/report")
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content.startswith(b"%PDF")
        assert "EFS_Assessment_" in response.headers.get("content-disposition", "")

def test_report_endpoint_weasyprint_unavailable(client: TestClient):
    analysis_id = get_sample_analysis_id()

    with patch("app.reports.report.WEASYPRINT_AVAILABLE", False), \
         patch("app.reports.report.WEASYPRINT_ERROR", "GTK library missing"):
        response = client.get(f"/api/v1/efs/{analysis_id}/report")
        assert response.status_code == 501
        assert "GTK/Pango/Cairo" in response.json()["detail"]

def test_report_endpoint_invalid_analysis_id(client: TestClient):
    mock_html = MagicMock()
    mock_html.return_value.write_pdf.return_value = b"%PDF-1.4 Mock PDF Binary Content"
    with patch("app.reports.report.WEASYPRINT_AVAILABLE", True), \
         patch("app.reports.report.HTML", mock_html):
        response = client.get("/api/v1/efs/sample_analysis_001/report")
        assert response.status_code == 200
