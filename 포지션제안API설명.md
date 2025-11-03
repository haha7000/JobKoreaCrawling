# 잡코리아 포지션 제안 API

## 기본 정보
- **URL**: `https://www.jobkorea.co.kr/Corp/Person/PositionOfferSave`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded; charset=UTF-8`

## Headers
```
Accept: */*
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: www.jobkorea.co.kr
Origin: https://www.jobkorea.co.kr
Referer: https://www.jobkorea.co.kr/corp/person/find/resume/view?rNo=26202001
X-Requested-With: XMLHttpRequest
```

## Request Parameters (필수)

### 이력서 정보
- `R_No`: 이력서 번호 (예: "26202001")
- `HT_ID`: 헤드헌터 ID (빈값 가능)

### 포지션 정보
- `PSTN_INFO_IDF_VALUE`: 포지션 정보 ID (예: "47945132")
- `PSTN_INFO_TYPE_CODE`: 포지션 타입 코드 (예: "2")
- `S_NO`: 순번 (예: "0")

### 담당자 정보
- `GI_Name`: 담당자 이름 (예: "이은경")
- `GI_Class`: 담당자 부서 (예: "인사팀")
- `GI_Email1`: 이메일 앞부분 (예: "x_car")
- `GI_Email2`: 이메일 도메인 (예: "naver.com")
- `GI_Phone1`: 전화번호 첫자리 (예: "010")
- `GI_Phone2`: 전화번호 중간자리 (예: "8204")
- `GI_Phone3`: 전화번호 끝자리 (예: "2282")
- `Mobile_No2`: 휴대폰 중간자리 (빈값 가능)
- `Mobile_No3`: 휴대폰 끝자리 (빈값 가능)

### 제안 내용
- `GI_Title`: 채용공고 제목 (URL 인코딩)
- `Contents`: 제안 메시지 내용 (URL 인코딩)
- `Reply_Expire_Dt`: 응답 만료일 (예: "2025-11-03")

### 옵션 설정 (0 또는 1)
- `Notice_SMS_Rcv_Stat`: SMS 수신 알림 상태 (0=비활성, 1=활성)
- `Contents_Save_Stat`: 내용 저장 상태 (0=비저장, 1=저장)
- `PHONE_NO_DISPLAY_STAT`: 전화번호 표시 여부 (0=숨김, 1=표시)
- `MOBILE_NO_DISPLAY_STAT`: 휴대폰번호 표시 여부 (0=숨김, 1=표시)
- `EMAIL_DISPLAY_STAT`: 이메일 표시 여부 (0=숨김, 1=표시)
- `GUIN_OFC_MAN_SAVE_STAT`: 담당자 정보 저장 상태 (0=비저장, 1=저장)
- `FREE_RESEND_STAT`: 무료 재전송 상태 (0=비활성, 1=활성)
- `WAITREPLY_EXPIRE_STAT`: 응답 대기 만료 상태 (0=비활성, 1=활성)

## Response
- **Status**: 200 OK
- **Content-Type**: application/json; charset=utf-8
- **Body Size**: 187 bytes (압축됨)

## 예시 요청

```python
import requests
from urllib.parse import urlencode

url = "https://www.jobkorea.co.kr/Corp/Person/PositionOfferSave"

headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.jobkorea.co.kr",
    "Referer": "https://www.jobkorea.co.kr/corp/person/find/resume/view?rNo=26202001",
    "X-Requested-With": "XMLHttpRequest"
}

data = {
    "R_No": "26202001",
    "HT_ID": "",
    "PSTN_INFO_IDF_VALUE": "47945132",
    "PSTN_INFO_TYPE_CODE": "2",
    "S_NO": "0",
    "GI_Name": "이은경",
    "GI_Class": "인사팀",
    "GI_Email1": "x_car",
    "GI_Email2": "naver.com",
    "GI_Phone1": "010",
    "GI_Phone2": "8204",
    "GI_Phone3": "2282",
    "Mobile_No2": "",
    "Mobile_No3": "",
    "GI_Title": "[한국중소기업진흥원] 기업 정책자금 컨설턴트 신입/경력 공개 채용",
    "Contents": "안녕하세요. 한국중소기업진흥원 입니다.\n저희가 찾고있는 포지션에 적합한 인재라고 생각되어 이렇게 제안 드립니다.\n긍정적인 검토 부탁 드리며, 관련 자세한 내용이 궁금하시다면 응답기간 내 회신 부탁 드립니다.\n",
    "Notice_SMS_Rcv_Stat": "0",
    "Contents_Save_Stat": "0",
    "PHONE_NO_DISPLAY_STAT": "0",
    "MOBILE_NO_DISPLAY_STAT": "0",
    "EMAIL_DISPLAY_STAT": "0",
    "Reply_Expire_Dt": "2025-11-03",
    "GUIN_OFC_MAN_SAVE_STAT": "0",
    "FREE_RESEND_STAT": "0",
    "WAITREPLY_EXPIRE_STAT": "0"
}

response = requests.post(url, headers=headers, data=data)
print(response.status_code)
print(response.json())
```
