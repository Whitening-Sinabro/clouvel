from fastapi import APIRouter, HTTPException
from src.models.docs import ScanRequest, ScanResponse, AnalyzeResponse
from src.services.docs_service import scan_docs, analyze_docs

router = APIRouter(prefix="/docs", tags=["docs"])


@router.post("/scan", response_model=ScanResponse)
def scan_project_docs(request: ScanRequest) -> ScanResponse:
    """프로젝트의 docs 디렉토리를 스캔하여 파일 목록 반환"""
    try:
        return scan_docs(request.path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_project_docs(request: ScanRequest) -> AnalyzeResponse:
    """프로젝트의 docs 디렉토리를 분석하여 필수 문서 존재 여부 확인"""
    try:
        return analyze_docs(request.path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
