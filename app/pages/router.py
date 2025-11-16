from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router_pages = APIRouter(prefix = '', tags = ['Frontend'])

@router_pages.get('/', response_class = HTMLResponse)
async def root(request: Request):
    return FileResponse('app/static/index.html')