# PRD: Django 개인 블로그 시스템

**Product Requirements Document**
**프로젝트명:** Django 개인 블로그 시스템
**작성일:** 2026-04-06
**버전:** v1.0
**작성자:** hellodm7-svg
**배포 URL:** https://django-blog-16zr.onrender.com
**GitHub:** https://github.com/hellodm7-svg/django-blog

---

## 1. 제품 개요 (Product Overview)

### 1.1 목적
개인이 글을 작성·관리·공유할 수 있는 블로그 웹 서비스를 제공한다. Django 프레임워크 기반으로 개발하며, 클라우드 환경(Render)에 배포하여 누구나 접근 가능한 실서비스로 운영한다.

### 1.2 대상 사용자
| 사용자 유형 | 설명 |
|-------------|------|
| **블로그 운영자 (Admin)** | 게시글 작성/수정/삭제, 카테고리·태그 관리, 사이트 설정 변경 |
| **일반 방문자 (Guest)** | 게시글 열람, 검색, 카테고리/태그 필터링 |
| **로그인 사용자 (User)** | 댓글 작성/삭제, 게시글 작성 (권한 보유 시) |

### 1.3 핵심 가치
- **간결한 글쓰기 경험**: Summernote 리치 에디터 (데스크톱) + 심플 에디터 (모바일) 자동 전환
- **멀티 테마 지원**: 다크/라이트/매거진/미니멀 4종 테마를 관리자 페이지에서 즉시 전환
- **반응형 UI**: 데스크톱·모바일 최적화 (하단 탭바, 카테고리 스크롤 등)

---

## 2. 기술 스택 (Tech Stack)

| 구분 | 기술 | 버전 |
|------|------|------|
| 언어 | Python | 3.12.7 |
| 프레임워크 | Django | 6.0.3 |
| DB (로컬) | SQLite | - |
| DB (배포) | PostgreSQL | Render Free |
| 서버 | Render | Starter ($7/월) |
| WSGI | Gunicorn | 21.2.0 |
| 정적 파일 | WhiteNoise | 6.6.0 |
| UI | Bootstrap 5 | 5.3.0 |
| 리치 에디터 | django-summernote | 0.8.20.0 |
| 관리자 UI | django-unfold | 0.52.0 |
| 이미지 처리 | Pillow | 12.1.1 |
| 버전 관리 | Git / GitHub | - |
| 개발 도구 | Cursor IDE | - |

---

## 3. 데이터 모델 (Data Models)

### 3.1 ERD 요약

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Category   │     │     Post     │     │     Tag      │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ name (unique)│◄────│ category(FK) │     │ name (unique)│
│ slug (unique)│     │ title        │────►│ slug (unique)│
└──────────────┘     │ content      │ M:N └──────────────┘
                     │ thumbnail    │
                     │ author(FK)───│──► User (Django Auth)
                     │ tags(M2M)    │
                     │ is_published │
                     │ view_count   │
                     │ created_at   │
                     │ updated_at   │
                     └──────┬───────┘
                            │ 1:N
                     ┌──────┴───────┐
                     │   Comment    │
                     ├──────────────┤
                     │ post(FK)     │
                     │ author(FK)   │
                     │ content      │
                     │ created_at   │
                     │ updated_at   │
                     └──────────────┘

┌──────────────────┐
│  SiteSettings    │
├──────────────────┤
│ theme (싱글톤)    │
│ blog_title       │
│ blog_description │
└──────────────────┘
```

### 3.2 모델 상세

#### Post (게시글)
| 필드 | 타입 | 설명 |
|------|------|------|
| title | CharField(200) | 게시글 제목 |
| content | TextField | 게시글 본문 (HTML, Summernote) |
| thumbnail | ImageField | 썸네일 이미지 (선택) |
| author | FK → User | 작성자 |
| category | FK → Category | 카테고리 (선택, SET_NULL) |
| tags | M2M → Tag | 태그 (다중 선택) |
| is_published | Boolean | 공개 여부 (기본: True) |
| view_count | PositiveInteger | 조회수 (기본: 0) |
| created_at | DateTime | 작성일 (자동) |
| updated_at | DateTime | 수정일 (자동) |

#### Category (카테고리)
| 필드 | 타입 | 설명 |
|------|------|------|
| name | CharField(100) | 카테고리명 (고유) |
| slug | SlugField(100) | URL 슬러그 (한글 허용) |

#### Tag (태그)
| 필드 | 타입 | 설명 |
|------|------|------|
| name | CharField(50) | 태그명 (고유) |
| slug | SlugField(50) | URL 슬러그 (한글 허용) |

#### Comment (댓글)
| 필드 | 타입 | 설명 |
|------|------|------|
| post | FK → Post | 소속 게시글 |
| author | FK → User | 작성자 |
| content | TextField | 댓글 내용 |
| created_at | DateTime | 작성일 (자동) |
| updated_at | DateTime | 수정일 (자동) |

#### SiteSettings (사이트 설정 - 싱글톤)
| 필드 | 타입 | 설명 |
|------|------|------|
| theme | CharField(20) | 테마 (dark/light/magazine/minimal) |
| blog_title | CharField(100) | 블로그 제목 (기본: "My Blog") |
| blog_description | CharField(200) | 블로그 설명 |

---

## 4. 기능 요구사항 (Functional Requirements)

### 4.1 게시글 관리 (CRUD)

| ID | 기능 | 설명 | 권한 | 상태 |
|----|------|------|------|------|
| FR-01 | 게시글 목록 | 최신순 정렬, 공개된 글만 표시 | 전체 | ✅ 완료 |
| FR-02 | 게시글 상세 | 본문, 댓글, 조회수 표시 | 전체 | ✅ 완료 |
| FR-03 | 게시글 작성 | Summernote 에디터, 썸네일/카테고리/태그 설정 | 로그인 | ✅ 완료 |
| FR-04 | 게시글 수정 | 본인 작성 글만 수정 가능 | 작성자 | ✅ 완료 |
| FR-05 | 게시글 삭제 | 확인 화면 후 삭제 | 작성자 | ✅ 완료 |
| FR-06 | 조회수 카운트 | 상세 페이지 진입 시 자동 증가 | 자동 | ✅ 완료 |
| FR-07 | 공개/비공개 | is_published 플래그로 제어 | 작성자 | ✅ 완료 |

### 4.2 분류 및 검색

| ID | 기능 | 설명 | 상태 |
|----|------|------|------|
| FR-08 | 카테고리 필터 | 슬러그 기반 URL, 사이드바 목록 | ✅ 완료 |
| FR-09 | 태그 필터 | 슬러그 기반 URL, 태그 pill UI | ✅ 완료 |
| FR-10 | 검색 | 제목 + 내용 대상 키워드 검색 (Q 객체) | ✅ 완료 |
| FR-11 | 모바일 카테고리 | 가로 스크롤 pill 형태 카테고리 바 | ✅ 완료 |

### 4.3 댓글

| ID | 기능 | 설명 | 권한 | 상태 |
|----|------|------|------|------|
| FR-12 | 댓글 작성 | 게시글 하단 폼에서 작성 | 로그인 | ✅ 완료 |
| FR-13 | 댓글 삭제 | 본인 댓글만 삭제 가능 | 작성자 | ✅ 완료 |

### 4.4 인증

| ID | 기능 | 설명 | 상태 |
|----|------|------|------|
| FR-14 | 로그인 | Django auth 기반, 리다이렉트 지원 | ✅ 완료 |
| FR-15 | 로그아웃 | POST 방식 (CSRF 보호) | ✅ 완료 |

### 4.5 관리자 기능

| ID | 기능 | 설명 | 상태 |
|----|------|------|------|
| FR-16 | 관리자 대시보드 | django-unfold 기반 모던 관리자 UI | ✅ 완료 |
| FR-17 | 테마 변경 | 관리자 페이지에서 4종 테마 즉시 전환 | ✅ 완료 |
| FR-18 | 블로그 정보 수정 | 제목, 설명 변경 | ✅ 완료 |
| FR-19 | 자동 관리자 생성 | build.sh에서 배포 시 superuser 자동 생성 | ✅ 완료 |

### 4.6 에디터

| ID | 기능 | 설명 | 상태 |
|----|------|------|------|
| FR-20 | 리치 에디터 (PC) | Summernote WYSIWYG: 서식, 이미지, 표, 링크, 코드뷰 | ✅ 완료 |
| FR-21 | 심플 에디터 (모바일) | User-Agent 감지 → 간단한 Textarea 에디터로 전환 | ✅ 완료 |

---

## 5. 비기능 요구사항 (Non-Functional Requirements)

### 5.1 성능
| ID | 요구사항 | 현황 |
|----|----------|------|
| NFR-01 | 사이트 설정 캐싱 (10분) | ✅ 구현 (SiteSettings.get_settings() 캐시) |
| NFR-02 | 정적 파일 압축 서빙 | ✅ WhiteNoise CompressedManifestStaticFilesStorage |
| NFR-03 | DB 커넥션 풀링 | ✅ conn_max_age=600 |

### 5.2 보안
| ID | 요구사항 | 현황 |
|----|----------|------|
| NFR-04 | CSRF 보호 | ✅ Django 기본 미들웨어 |
| NFR-05 | 로그인 필수 (글쓰기/댓글) | ✅ @login_required 데코레이터 |
| NFR-06 | 작성자 본인만 수정/삭제 | ✅ author=request.user 필터 |
| NFR-07 | SECRET_KEY 환경변수 분리 | ✅ os.environ.get() |
| NFR-08 | XSS 방지 | ⚠️ Summernote HTML 저장 시 추가 sanitize 검토 필요 |

### 5.3 반응형 & 접근성
| ID | 요구사항 | 현황 |
|----|----------|------|
| NFR-09 | 모바일 반응형 레이아웃 | ✅ 768px 브레이크포인트 |
| NFR-10 | 모바일 하단 탭바 | ✅ 고정 하단 내비게이션 (홈/검색/글쓰기/로그인) |
| NFR-11 | 최소 터치 영역 44px | ✅ 버튼 min-height 적용 |
| NFR-12 | 모바일 본문 가독성 | ✅ font-size 1.05rem, line-height 1.95 |

---

## 6. URL 구조 (API Endpoints)

| HTTP | URL | View | 설명 |
|------|-----|------|------|
| GET | `/` | post_list | 게시글 목록 (검색: `?q=keyword`) |
| GET | `/post/<pk>/` | post_detail | 게시글 상세 |
| GET/POST | `/post/create/` | post_create | 게시글 작성 |
| GET/POST | `/post/<pk>/edit/` | post_edit | 게시글 수정 |
| GET/POST | `/post/<pk>/delete/` | post_delete | 게시글 삭제 |
| POST | `/post/<pk>/comment/` | comment_create | 댓글 작성 |
| POST | `/post/<pk>/comment/<comment_pk>/delete/` | comment_delete | 댓글 삭제 |
| GET | `/category/<slug>/` | category_posts | 카테고리별 글 목록 |
| GET | `/tag/<slug>/` | tag_posts | 태그별 글 목록 |
| GET/POST | `/accounts/login/` | Django auth | 로그인 |
| POST | `/accounts/logout/` | Django auth | 로그아웃 |
| - | `/admin/` | Django admin | 관리자 페이지 |

---

## 7. 테마 시스템

4종의 CSS 변수 기반 테마를 SiteSettings 모델로 관리한다. 관리자 페이지에서 변경 시 캐시 초기화 후 즉시 반영된다.

| 테마 | 키 | 배경 | 강조색 | 특징 |
|------|----|------|--------|------|
| 다크 (기본) | `dark` | #0d1117 | #58a6ff | GitHub Dark 스타일 |
| 라이트 모던 | `light` | #f5f7fa | #2563eb | 밝고 깔끔한 UI |
| 매거진 | `magazine` | #fafafa | #c0392b | Georgia 세리프, 신문 스타일 |
| 미니멀 화이트 | `minimal` | #ffffff | #222222 | 흑백 미니멀리즘 |

---

## 8. 배포 아키텍처

```
┌──────────────┐    push     ┌──────────────┐   auto-deploy   ┌──────────────┐
│  개발자 PC   │ ──────────► │    GitHub     │ ──────────────► │    Render    │
│  (Cursor IDE)│             │  (main 브랜치) │                │ Web Service  │
└──────────────┘             └──────────────┘                 └──────┬───────┘
                                                                     │
                                                              ┌──────┴───────┐
                                                              │  build.sh    │
                                                              │  1. pip install│
                                                              │  2. collectstatic│
                                                              │  3. DB backup │
                                                              │  4. migrate   │
                                                              │  5. superuser │
                                                              └──────┬───────┘
                                                                     │
                                                              ┌──────┴───────┐
                                                              │  gunicorn    │
                                                              │  + WhiteNoise│
                                                              │  + PostgreSQL│
                                                              └──────────────┘
```

### 환경변수
| 변수 | 설명 | 배포 값 |
|------|------|---------|
| SECRET_KEY | Django 시크릿 키 | (Render 환경변수) |
| DEBUG | 디버그 모드 | False |
| ALLOWED_HOSTS | 허용 호스트 | *.onrender.com |
| DATABASE_URL | PostgreSQL 연결 | (Render 자동 설정) |

---

## 9. 프로젝트 디렉토리 구조

```
myproject/
├── config/                  # Django 프로젝트 설정
│   ├── settings.py          # 메인 설정 파일
│   ├── urls.py              # 루트 URL 설정
│   ├── wsgi.py              # WSGI 엔트리포인트
│   └── asgi.py              # ASGI 엔트리포인트
├── blog/                    # 블로그 앱
│   ├── models.py            # 데이터 모델 (5개)
│   ├── views.py             # 뷰 함수 (9개)
│   ├── urls.py              # URL 라우팅 (9개)
│   ├── forms.py             # PostForm, CommentForm
│   ├── admin.py             # 관리자 설정
│   ├── context_processors.py # SiteSettings 전역 주입
│   └── templates/blog/      # HTML 템플릿
│       ├── base.html         # 기본 레이아웃 (테마, 네비게이션)
│       ├── post_list.html    # 게시글 목록
│       ├── post_detail.html  # 게시글 상세
│       ├── post_form.html    # 게시글 작성/수정 폼
│       └── post_confirm_delete.html  # 삭제 확인
├── build.sh                 # Render 빌드 스크립트
├── requirements.txt         # Python 패키지 목록
├── manage.py                # Django 관리 명령어
└── db.sqlite3               # 로컬 개발 DB
```

---

## 10. 알려진 제한사항 및 향후 개선 사항

### 10.1 현재 제한사항
| 항목 | 설명 |
|------|------|
| 회원가입 없음 | 관리자가 직접 사용자 생성 필요 |
| 댓글 수정 불가 | 삭제만 가능, 수정 기능 미구현 |
| 페이지네이션 없음 | 게시글 수 증가 시 성능 저하 가능 |
| 이미지 업로드 제한 | Render Free 디스크 용량 제한 |
| Summernote HTML 저장 | XSS sanitize 추가 검토 필요 |

### 10.2 향후 개선 후보
| 우선순위 | 항목 | 설명 |
|----------|------|------|
| 높음 | 페이지네이션 | 게시글 목록 페이징 처리 |
| 높음 | 회원가입 | 자체 회원가입 또는 소셜 로그인 |
| 중간 | 댓글 수정 | 댓글 CRUD 완성 |
| 중간 | 이미지 외부 저장소 | S3 또는 Cloudinary 연동 |
| 낮음 | SEO 최적화 | meta 태그, sitemap, Open Graph |
| 낮음 | RSS 피드 | 블로그 RSS 구독 지원 |

---

## 11. 트러블슈팅 이력

| # | 문제 | 원인 | 해결 |
|---|------|------|------|
| 1 | Bad Request 400 | ALLOWED_HOSTS에 Render 도메인 누락 | `.onrender.com` 추가 |
| 2 | 로그아웃 405 오류 | Django 최신 버전은 POST 방식 필요 | `<form>` + POST로 변경 |
| 3 | 재배포 시 데이터 초기화 | SQLite 파일 기반 → 재배포 시 삭제 | PostgreSQL 전환 |
| 4 | GitHub push 차단 | 액세스 토큰 파일 포함 | .gitignore에 txt 추가 |

---

*이 문서는 프로젝트의 현재 구현 상태를 기준으로 작성되었습니다.*
