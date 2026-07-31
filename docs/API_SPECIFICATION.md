# Upload API

POST /api/v1/upload

Description:
Uploads Balance Sheet, Profit & Loss and Cash Flow statements.

Request:
multipart/form-data

Fields:
- balance_sheet
- profit_loss
- cash_flow

Response

{
    "analysis_id": "uuid",
    "status": "uploaded",
    "uploaded_files": [...]
}

Errors

400 Invalid File

413 File Too Large

415 Unsupported File Type