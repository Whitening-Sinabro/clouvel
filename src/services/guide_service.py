from src.models.guide import PRDGuide, GuideStep, VerifyGuide, CheckCategory, CheckItem


def get_prd_guide() -> PRDGuide:
    return PRDGuide(
        title="PRD 작성법",
        tagline="이 문서가 법. 여기 없으면 안 만듦.",
        steps=[
            GuideStep(
                step=1,
                title="한 줄 요약",
                description="프로젝트가 뭔지 한 문장으로. 못 쓰면 정리 안 된 거임.",
                example='"한 번 라이브로 일주일치 콘텐츠" - Vivorbis',
            ),
            GuideStep(
                step=2,
                title="핵심 원칙 3개",
                description="절대 안 변하는 것들. 이거 기준으로 기능 판단.",
                example="원가 보호 / 무료 체험 / 현금 유입",
            ),
            GuideStep(
                step=3,
                title="입력 스펙 테이블",
                description="필드 | 타입 | 필수 | 제한 | 검증 | 예시",
                example="productName | string | O | 1~100자 | 빈문자열X | '코코넛오일'",
            ),
            GuideStep(
                step=4,
                title="출력 JSON",
                description="말로 설명 X. 실제 응답 그대로.",
                example='{"id": "abc123", "status": "completed", "result": {...}}',
            ),
            GuideStep(
                step=5,
                title="에러 테이블",
                description="상황 | 코드 | 메시지. SNAKE_CASE 통일.",
                example="잔액부족 | INSUFFICIENT_CREDITS | '크레딧 부족. 필요: {n}'",
            ),
            GuideStep(
                step=6,
                title="상태 머신",
                description="복잡한 플로우는 ASCII로.",
                example="[available] --reserve--> [reserved] --capture--> [done]",
            ),
        ],
    )


def get_verify_guide() -> VerifyGuide:
    return VerifyGuide(
        title="PRD 검증",
        tagline="빠뜨리면 나중에 다시 짬",
        categories=[
            CheckCategory(
                name="스펙",
                items=[
                    CheckItem(id="s1", check="입력 제한값 다 있음?", detail="1~100자, 최대 10개 같은 거", priority="critical"),
                    CheckItem(id="s2", check="enum 옵션표 있음?", detail="tone: friendly|expert|urgent", priority="critical"),
                    CheckItem(id="s3", check="출력 JSON 필드 다 나옴?", detail="metadata, createdAt 빠뜨리기 쉬움", priority="critical"),
                ],
            ),
            CheckCategory(
                name="에러",
                items=[
                    CheckItem(id="e1", check="에러코드 SNAKE_CASE?", detail="INSUFFICIENT_CREDITS (O)", priority="important"),
                    CheckItem(id="e2", check="동적 값 들어감?", detail="'필요: {required}, 보유: {available}'", priority="important"),
                ],
            ),
            CheckCategory(
                name="돈",
                items=[
                    CheckItem(id="m1", check="무료/유료 구분표?", detail="Free: 미리보기 / Paid: 다운로드", priority="critical"),
                    CheckItem(id="m2", check="크레딧 차감 시점?", detail="reserve -> capture -> release", priority="critical"),
                    CheckItem(id="m3", check="실패 시 환불?", detail="작업 실패하면 release", priority="critical"),
                ],
            ),
            CheckCategory(
                name="API",
                items=[
                    CheckItem(id="a1", check="/v1/ 붙어있음?", detail="POST /v1/scripts (O)", priority="important"),
                    CheckItem(id="a2", check="202 맞게 씀?", detail="비동기는 202 + jobId", priority="important"),
                ],
            ),
            CheckCategory(
                name="데이터",
                items=[
                    CheckItem(id="d1", check="보관 기간?", detail="무료 24시간, 유료 7일", priority="important"),
                    CheckItem(id="d2", check="만료 알림?", detail="24시간 전 푸시", priority="recommended"),
                ],
            ),
        ],
    )
