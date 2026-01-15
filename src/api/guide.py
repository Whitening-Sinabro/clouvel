from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from src.models.guide import PRDGuide, VerifyGuide
from src.services.guide_service import get_prd_guide, get_verify_guide

router = APIRouter(prefix="/guide", tags=["guide"])


@router.get("/prd", response_model=PRDGuide)
def prd_guide() -> PRDGuide:
    """PRD 작성 가이드 JSON"""
    return get_prd_guide()


@router.get("/prd/view", response_class=HTMLResponse)
def prd_guide_view() -> HTMLResponse:
    """PRD 작성 가이드 HTML"""
    guide = get_prd_guide()

    steps_html = ""
    for s in guide.steps:
        example_html = f'<code>{s.example}</code>' if s.example else ''
        steps_html += f'''
        <div class="step">
            <div class="step-num">{s.step}</div>
            <div class="step-content">
                <h3>{s.title}</h3>
                <p>{s.description}</p>
                {example_html}
            </div>
        </div>
        '''

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{guide.title}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: "Pretendard", -apple-system, sans-serif;
                background: #0a0a0a;
                color: #e5e5e5;
                line-height: 1.6;
            }}
            .container {{ max-width: 720px; margin: 0 auto; padding: 60px 24px; }}
            h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 8px;
                color: #fff;
            }}
            .tagline {{
                color: #888;
                font-size: 1.1rem;
                margin-bottom: 48px;
                padding-bottom: 24px;
                border-bottom: 1px solid #222;
            }}
            .step {{
                display: flex;
                gap: 20px;
                margin-bottom: 32px;
            }}
            .step-num {{
                width: 36px;
                height: 36px;
                background: #E8FF6B;
                color: #000;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                flex-shrink: 0;
            }}
            .step-content h3 {{
                font-size: 1.2rem;
                margin-bottom: 6px;
                color: #fff;
            }}
            .step-content p {{ color: #999; margin-bottom: 12px; }}
            code {{
                display: block;
                background: #1a1a1a;
                padding: 12px 16px;
                border-radius: 8px;
                font-family: "JetBrains Mono", monospace;
                font-size: 0.9rem;
                color: #E8FF6B;
                border-left: 3px solid #E8FF6B;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{guide.title}</h1>
            <p class="tagline">{guide.tagline}</p>
            {steps_html}
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)


@router.get("/verify", response_model=VerifyGuide)
def verify_guide() -> VerifyGuide:
    """검증 체크리스트 JSON"""
    return get_verify_guide()


@router.get("/verify/view", response_class=HTMLResponse)
def verify_guide_view() -> HTMLResponse:
    """검증 체크리스트 HTML"""
    guide = get_verify_guide()

    categories_html = ""
    for cat in guide.categories:
        items_html = ""
        for item in cat.items:
            priority_color = {"critical": "#ff4444", "important": "#ffaa00", "recommended": "#44aa44"}.get(item.priority, "#888")
            items_html += f'''
            <div class="check-item">
                <div class="check-box"></div>
                <div class="check-content">
                    <span class="check-text">{item.check}</span>
                    <span class="check-detail">{item.detail}</span>
                </div>
                <span class="priority" style="color: {priority_color}">{item.priority}</span>
            </div>
            '''
        categories_html += f'''
        <div class="category">
            <h2>{cat.name}</h2>
            {items_html}
        </div>
        '''

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{guide.title}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: "Pretendard", -apple-system, sans-serif;
                background: #0a0a0a;
                color: #e5e5e5;
                line-height: 1.6;
            }}
            .container {{ max-width: 720px; margin: 0 auto; padding: 60px 24px; }}
            h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 8px;
                color: #fff;
            }}
            .tagline {{
                color: #888;
                font-size: 1.1rem;
                margin-bottom: 48px;
                padding-bottom: 24px;
                border-bottom: 1px solid #222;
            }}
            .category {{ margin-bottom: 40px; }}
            .category h2 {{
                font-size: 1rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #666;
                margin-bottom: 16px;
            }}
            .check-item {{
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 16px;
                background: #111;
                border-radius: 8px;
                margin-bottom: 8px;
            }}
            .check-box {{
                width: 20px;
                height: 20px;
                border: 2px solid #333;
                border-radius: 4px;
                flex-shrink: 0;
                margin-top: 2px;
            }}
            .check-content {{ flex: 1; }}
            .check-text {{
                display: block;
                color: #fff;
                font-weight: 500;
            }}
            .check-detail {{
                display: block;
                color: #666;
                font-size: 0.9rem;
                margin-top: 4px;
            }}
            .priority {{
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{guide.title}</h1>
            <p class="tagline">{guide.tagline}</p>
            {categories_html}
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)
