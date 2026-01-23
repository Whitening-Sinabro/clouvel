# Chrome Extension 템플릿

> Chrome 브라우저 확장프로그램

---

## 자동 감지 조건

다음 조건 충족 시 `chrome-ext`로 감지:

- `manifest.json` 파일 존재
- `manifest.json`에 `manifest_version`, `permissions` 포함

---

## PRD 질문 가이드

| 순서 | 섹션         | 질문                                 | 예시                                         |
| ---- | ------------ | ------------------------------------ | -------------------------------------------- |
| 1    | summary      | 이 확장프로그램이 해결하려는 문제는? | 유튜브 광고 스킵이 번거로움                  |
| 2    | target       | 주요 사용자는?                       | 유튜브 헤비 유저, 직장인                     |
| 3    | features     | 핵심 기능 3가지                      | 광고 스킵, 스폰서 건너뛰기, 통계             |
| 4    | permissions  | 필요한 권한은?                       | activeTab, storage                           |
| 5    | side_effects | 기존 기능/다른 확장에 영향?          | 다른 광고 차단 확장과 충돌, 사이트 로딩 영향 |
| 6    | out_of_scope | 제외할 기능                          | Firefox 지원, 다크모드                       |

---

## PRD 예시

````markdown
# YouTube Ad Skipper PRD

## 1. 프로젝트 개요

### 1.1 목적

유튜브 광고를 자동으로 스킵하는 Chrome 확장프로그램

### 1.2 타겟 사용자

- 유튜브 헤비 유저
- 광고에 민감한 사용자

### 1.3 성공 지표

| 지표    | 목표   |
| ------- | ------ |
| 설치 수 | 1,000+ |
| 평점    | 4.5+   |

---

## 2. 기능 요구사항

### 2.1 핵심 기능

1. **광고 자동 스킵**: Skip 버튼 자동 클릭
2. **스폰서 구간 건너뛰기**: SponsorBlock 연동
3. **통계 표시**: 스킵한 광고 시간 누적

### 2.2 제외 범위

- Firefox 지원
- 다크모드
- 유료 플랜

---

## 3. 기술 스펙

### 3.1 Manifest

```json
{
  "manifest_version": 3,
  "name": "YouTube Ad Skipper",
  "version": "1.0.0",
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["*://*.youtube.com/*"],
  "content_scripts": [
    {
      "matches": ["*://*.youtube.com/*"],
      "js": ["content.js"]
    }
  ]
}
```
````

### 3.2 파일 구조

```
/
├── manifest.json
├── popup/
│   ├── popup.html
│   └── popup.js
├── content.js
├── background.js
└── icons/
```

### 3.3 필요 권한

| 권한        | 용도           |
| ----------- | -------------- |
| `activeTab` | 현재 탭 접근   |
| `storage`   | 설정/통계 저장 |

```

---

## 체크리스트

- [ ] Manifest V3 사용하는가?
- [ ] 필요한 최소 권한만 요청하는가?
- [ ] 프라이버시 정책이 있는가?
- [ ] 스토어 설명이 준비되었는가?
- [ ] 아이콘이 준비되었는가? (16, 48, 128px)
```
