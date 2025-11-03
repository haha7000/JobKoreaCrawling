# 잡코리아 채용 자동화 시스템

잡코리아 API를 활용하여 이력서 검색, 평가, 포지션 제안까지 자동화하는 시스템입니다.

## 📋 목차
- [시스템 개요](#시스템-개요)
- [실행 순서](#실행-순서)
- [환경 설정](#환경-설정)
- [파일 구조](#파일-구조)
- [상세 가이드](#상세-가이드)
- [문제 해결](#문제-해결)

## 🎯 시스템 개요

이 시스템은 4단계로 구성됩니다:

1. **main.py**: 잡코리아에서 이력서 검색 및 수집
2. **Detail.py**: 자기소개서 및 자격증 상세정보 추출
3. **grade.py**: 후보자 자동 평가 및 점수 산출
4. **position_offer.py**: AI 기반 맞춤형 포지션 제안 문구 생성

## 🚀 실행 순서

```bash
# 1단계: 이력서 검색 및 수집
python main.py

# 2단계: 자기소개서/자격증 추출
python Detail.py

# 3단계: 후보자 평가
python grade.py

# 4단계: 포지션 제안 문구 생성
python position_offer.py
```

## ⚙️ 환경 설정

### 1. Python 버전
```bash
Python 3.8 이상
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

필요한 주요 패키지:
- `requests`: API 호출
- `playwright`: 웹 자동화
- `beautifulsoup4`: HTML 파싱
- `openpyxl`: 엑셀 파일 처리
- `openai`: OpenAI API 연동

Playwright 설치 (최초 1회):
```bash
playwright install chromium
```

### 3. 계정 설정

`configs/jobkorea_Excel.xlsx` 파일에 잡코리아 계정 정보 입력:

**[계정정보] 시트:**
| 아이디 | 비밀번호 |
|--------|----------|
| your_id@example.com | your_password |

**검색 조건 시트 (계정 아이디와 동일한 이름):**
- 대분류, 직무, 지역, 학력, 나이 등 검색 조건 설정

### 4. OpenAI API 키 설정 (4단계용)

```bash
# 환경변수 설정 (macOS/Linux)
export OPENAI_API_KEY_COMPANY="sk-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY_COMPANY="sk-..."

# Windows (CMD)
set OPENAI_API_KEY_COMPANY=sk-...
```

## 📁 파일 구조

```
apiTEst/
├── main.py                          # 1단계: 이력서 검색
├── Detail.py                        # 2단계: 상세정보 추출
├── grade.py                         # 3단계: 평가
├── position_offer.py                # 4단계: 제안문구 생성
├── only_offers.py                   # 제안문구만 추출
├── configs/
│   └── jobkorea_Excel.xlsx         # 계정 및 검색조건 설정
├── data/
│   └── payload_template.json       # API 요청 템플릿
├── src/
│   ├── config.py                   # 설정 관리
│   ├── auth.py                     # 인증 처리
│   ├── scraper.py                  # 스크래핑 로직
│   ├── payload_manager.py          # API 페이로드 관리
│   ├── account_manager.py          # 계정 관리
│   ├── excel_config_parser.py      # 엑셀 설정 파싱
│   └── exporter.py                 # 엑셀 출력
└── output/                          # 결과 파일
    ├── {계정명}_summary.json       # 1단계 출력
    ├── {계정명}_결과.xlsx           # 1단계 출력 (엑셀)
    ├── {계정명}_with_introduction.json  # 2단계 출력
    ├── {계정명}_scored.json        # 3단계 출력 (합격자만)
    └── {계정명}_with_offers.json   # 4단계 출력 (제안문구 포함)
```

## 📖 상세 가이드

### 1단계: main.py - 이력서 검색

**기능:**
- 잡코리아 API를 통해 설정된 조건으로 이력서 검색
- 최근활동 필터링 (예: 240분 이내 활동한 사용자만)
- JSON 및 엑셀 형식으로 저장

**설정 수정 (main.py 파일 내):**
```python
START_PAGE = 1
END_PAGE = 2
PAGE_SIZE = 100
FILTER_ACTIVE_WITHIN_MINUTES = 30  # 240분(4시간) 이내 활동
```

**출력:**
- `output/{계정명}_summary.json`: 이력서 목록 (JSON)
- `output/{계정명}_결과.xlsx`: 이력서 목록 (엑셀)

**주요 추출 정보:**
- 번호, 이름, 성별, 나이, 제목, 경력, 학력, 지역, 직무
- 기술스택, 이력서번호, 이력서링크, 최근활동

---

### 2단계: Detail.py - 자기소개서/자격증 추출

**기능:**
- Chrome 디버깅 모드 자동 실행
- Playwright를 통해 각 이력서 페이지 방문
- 자기소개서 및 자격증 정보 추출
- 중간 저장 기능 (처리 중 중단되어도 이어서 실행 가능)

**중요:**
- Chrome이 **자동으로 실행**됩니다 (macOS/Windows/Linux 지원)
- 처리 완료 후 Chrome 자동 종료

**설정 수정 (Detail.py 파일 내):**
```python
summary_json = "output/kspac2022_summary.json"  # 입력 파일
output_file = "output/kspac2022_with_introduction.json"  # 출력 파일
max_count = None  # 전체 처리 (숫자 입력 시 제한)
```

**출력:**
- `output/{계정명}_with_introduction.json`: 자기소개서 및 자격증 포함

**OS별 Chrome 경로:**
- **macOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **Linux**: `google-chrome`

---

### 3단계: grade.py - 후보자 평가

**기능:**
- 경력, 자격증, 전문성 기반 자동 점수 산출
- 합격/불합격 판정 (기본: 30점 이상 합격)
- 엑셀 파일에 점수 컬럼 자동 추가

**평가 기준:**
| 항목 | 최대 점수 | 내용 |
|------|-----------|------|
| 영업 경력 | 30점 | 보험/금융/일반 영업 경력, 활동 여부 |
| 커뮤니케이션 | 5점 | 고객 소통, 문제 해결 역량 (현재 0점) |
| 전문성 | 30점 | 자격증, 학력, 교육 이력 |
| 동기/어학 | 5점 | TOEIC, OPIC 등 어학 점수 (현재 어학만) |
| **총점** | **70점** | - |

**설정 수정 (grade.py 파일 내):**
```python
MIN_SCORE = 30  # 최소 합격 점수
```

**출력:**
- `output/{계정명}_scored.json`: 합격자만 포함 (30점 이상)
- `output/{계정명}_with_introduction.json`: 원본에 점수 추가
- `output/{계정명}_결과.xlsx`: 엑셀에 "점수" 컬럼 추가

---

### 4단계: position_offer.py - 포지션 제안 문구 생성

**기능:**
- OpenAI GPT-4를 활용한 맞춤형 제안 문구 생성
- 30점 이상 합격자에게만 제안 문구 생성
- 자기소개서, 자격증, 경력 기반으로 개인화된 문구 작성
- 엑셀 파일에 "제안문구" 컬럼 자동 추가

**기본 템플릿:**
```
안녕하세요. 한국중소기업진흥원 입니다.
저희가 찾고있는 포지션에 적합한 인재라고 생각되어 이렇게 제안 드립니다.
긍정적인 검토 부탁 드리며, 관련 자세한 내용이 궁금하시다면 응답기간 내 회신 부탁 드립니다.
```

**설정 수정 (position_offer.py 파일 내):**
```python
INPUT_FILE = "output/kspac2022_with_introduction.json"
OUTPUT_FILE = "output/kspac2022_with_offers.json"
EXCEL_FILE = "output/kspac2022_결과.xlsx"
MIN_SCORE = 30  # 제안 대상 최소 점수
```

**출력:**
- `output/{계정명}_with_offers.json`: 제안문구 포함 (합격자만)
- `output/{계정명}_결과.xlsx`: 엑셀에 "제안문구" 컬럼 추가 (30점 이상만)

---

## 🔧 문제 해결

### 1. Chrome 연결 실패 (Detail.py)

**증상:**
```
❌ Chrome 연결 실패: ...
```

**해결:**
- Chrome이 자동으로 실행되지 않은 경우
- 수동으로 Chrome 디버깅 모드 실행:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Windows (PowerShell)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=%TEMP%\chrome-debug

# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

### 2. OpenAI API 키 오류 (position_offer.py)

**증상:**
```
❌ 오류: OpenAI API 키가 필요합니다.
```

**해결:**
```bash
# 환경변수 설정
export OPENAI_API_KEY_COMPANY="sk-proj-..."

# 또는 코드에서 직접 지정 (position_offer.py)
generator = PositionOfferGenerator(api_key="sk-proj-...")
```

### 3. 로그인 실패

**증상:**
```
❌ 로그인 실패!
```

**해결:**
1. `configs/jobkorea_Excel.xlsx` 파일의 계정 정보 확인
2. 잡코리아 웹사이트에서 직접 로그인 테스트
3. 2FA(이중인증) 설정 확인

### 4. 파일을 찾을 수 없음

**증상:**
```
❌ 파일을 찾을 수 없습니다: output/kspac2022_summary.json
```

**해결:**
- 이전 단계가 정상 완료되었는지 확인
- `output/` 디렉토리 존재 확인
- 파일명이 올바른지 확인 (계정명 기반)

### 5. 중간에 중단된 경우

**Detail.py 이어서 실행:**
- 자동으로 기존 진행 상황을 확인하고 이어서 처리됩니다
- `output/{계정명}_with_introduction.json` 파일이 있으면 자동으로 이어서 시작

---

## 📊 출력 파일 예시

### 1단계 출력 (summary.json)
```json
[
  {
    "번호": 1,
    "이름": "홍길동",
    "성별": "남",
    "나이": "만 30세",
    "경력": "5년2개월",
    "직무": "금융영업, 고객관리",
    "이력서번호": "12345678",
    "이력서링크": "https://www.jobkorea.co.kr/...",
    "최근활동": "10분전 입사지원"
  }
]
```

### 3단계 출력 (scored.json)
```json
[
  {
    "이름": "홍길동",
    "점수상세": {
      "영업경력점수": 25,
      "커뮤니케이션점수": 0,
      "전문성점수": 10,
      "동기어학점수": 3,
      "총점": 38
    }
  }
]
```

### 4단계 출력 (with_offers.json)
```json
[
  {
    "이름": "홍길동",
    "포지션제안문구": "안녕하세요. 한국중소기업진흥원 입니다. 귀하의 5년 이상의 금융영업 경력과 고객관리 역량이 저희가 찾고 있는 포지션에 적합하다고 생각되어 제안 드립니다..."
  }
]
```

---

## 🎯 API 정보

### 포지션 제안 API
**URL**: `https://www.jobkorea.co.kr/Corp/Person/PositionOfferSave`

상세 스펙: [position_offer_api.md](position_offer_api.md) 참고

---

## 📝 개발 노트

- **개발일**: 2025년 11월
- **개발자**: 김동훈
- **목적**: 잡코리아 채용 프로세스 자동화
- **기술 스택**: Python, Playwright, OpenAI API, BeautifulSoup

---

## 📞 문의

문제 발생 시:
1. 각 단계별 출력 파일 확인
2. 에러 메시지 전체 복사
3. 실행 환경 정보 (OS, Python 버전) 확인
