"""
실제 실행 중인 Chrome에 연결하여 자기소개서 추출
"""
from bs4.element import Tag


from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import subprocess
import os
import signal
import platform
from pathlib import Path
from src.account_manager import AccountManager
from src.auth import JobKoreaAuth



def extract_introduction_from_page(page):
    """현재 페이지에서 자기소개서 추출"""
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    intro_section = soup.select_one("div.base.introduction")
    if not intro_section:
        return None

    items = intro_section.select("ul.list-introduction > li.item")
    if not items:
        return None

    data = []
    for idx, li in enumerate[Tag](items, 1):
        title_elem = li.select_one("div.header")
        title = title_elem.get_text(strip=True) if title_elem else None

        body_elem = li.select_one("div.content#pfl_original") or li.select_one("div.content")
        if body_elem:
            body_text = body_elem.get_text(separator="\n", strip=True)
            if body_text.startswith("- 자기소개서-"):
                body_text = body_text.replace("- 자기소개서-", "", 1).strip()
        else:
            body_text = None

        data.append({
            "index": idx,
            "title": title,
            "body_text": body_text,
        })

    return data


def extract_certificates_from_page(page):
    """현재 페이지에서 자격증 정보 추출"""
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    cert_section = soup.select_one("div.base.certificate")
    if not cert_section:
        return None

    # > 제거: 직접 자식이 아니라 하위 요소 전체 검색
    items = cert_section.select("div.list-certificate div.item")
    if not items:
        return None

    data = []
    for item in items:
        # 취득일
        date_elem = item.select_one("div.date")
        date = date_elem.get_text(strip=True) if date_elem else None

        # 자격증명
        name_elem = item.select_one("div.content-header div.name")
        name = name_elem.get_text(strip=True) if name_elem else None

        # 발행기관
        agency_elem = item.select_one("div.content-header div.agency")
        agency = agency_elem.get_text(strip=True) if agency_elem else None

        if name:  # 자격증명이 있을 때만 추가
            data.append({
                "취득일": date,
                "자격증명": name,
                "발행기관": agency,
            })

    return data if data else None


def login_and_get_cookies(username: str, password: str):
    """
    잡코리아 로그인하여 쿠키 반환
    """
    print(f"🔐 잡코리아 로그인 시도: {username}")
    auth = JobKoreaAuth(username, password)
    session = auth.login()

    if not session:
        print("❌ 로그인 실패!")
        return None

    # requests 쿠키를 Playwright 형식으로 변환
    cookies = []
    for cookie_name, cookie_value in session.cookies.items():
        cookies.append({
            "name": cookie_name,
            "value": cookie_value,
            "domain": ".jobkorea.co.kr",
            "path": "/"
        })

    print(f"✅ 로그인 성공! {len(cookies)}개 쿠키 획득\n")
    return cookies


def extract_all_resumes(summary_json_path: str, max_count: int = None, output_file: str = "output/Details.json"):
    """
    실행 중인 Chrome에 연결하여 자기소개서 일괄 추출
    1명씩 처리할 때마다 JSON 파일에 저장 (중간 손실 방지)
    """
    # 이력서 목록 로드
    with open(summary_json_path, 'r', encoding='utf-8') as f:
        resumes = json.load(f)

    print(f"📋 총 {len(resumes)}개 이력서 발견")

    if max_count:
        resumes = resumes[:max_count]
        print(f"   → {max_count}개만 처리합니다.\n")

    # 기존 진행 상황 확인 (이어서 하기)
    if Path(output_file).exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            try:
                existing_results = json.load(f)
                processed_rnos = {r.get('이력서번호') for r in existing_results if r.get('추출상태') == '성공'}
                print(f"💾 기존 저장 파일 발견: {len(existing_results)}개 처리됨")
                print(f"   이어서 진행합니다...\n")
                results = existing_results
            except:
                results = []
    else:
        processed_rnos = set()
        results = []

    # 계정 정보 로드
    excel_path = "configs/jobkorea_Excel.xlsx"
    account_manager = AccountManager(excel_path)
    accounts = account_manager.list_accounts()

    if not accounts:
        print("❌ 계정이 없습니다.")
        return []

    credentials = account_manager.get_credentials(accounts[0])
    if not credentials:
        print("❌ 계정 정보를 불러올 수 없습니다.")
        return []

    username = credentials['username']
    password = credentials['password']

    # 로그인하여 쿠키 획득
    cookies = login_and_get_cookies(username, password)
    if not cookies:
        return []

    # Chrome 자동 실행
    chrome_process = None
    print("=" * 80)
    print("🚀 Chrome 디버깅 모드 자동 실행")
    print("=" * 80)

    # OS별 Chrome 경로 및 user-data-dir 설정
    system = platform.system()
    if system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        user_data_dir = "/tmp/chrome-debug"
        manual_cmd = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222'
    elif system == "Windows":
        # Windows Chrome 경로 (일반적인 위치들 체크)
        possible_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe")
        ]
        chrome_path = None
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        if not chrome_path:
            chrome_path = "chrome.exe"  # PATH에 있을 경우
        user_data_dir = os.path.expandvars("%TEMP%\\chrome-debug")
        manual_cmd = 'chrome.exe --remote-debugging-port=9222'
    else:  # Linux
        chrome_path = "google-chrome"
        user_data_dir = "/tmp/chrome-debug"
        manual_cmd = 'google-chrome --remote-debugging-port=9222'

    try:
        chrome_cmd = [
            chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={user_data_dir}"
        ]

        print(f"📌 OS: {system}")
        print(f"📌 실행 명령어:")
        if system == "Windows":
            print(f'   "{chrome_path}" --remote-debugging-port=9222 --user-data-dir={user_data_dir}\n')
        else:
            print(f"   {' '.join([f'\"{p}\"' if ' ' in p else p for p in chrome_cmd])}\n")

        # Chrome 프로세스 실행
        chrome_process = subprocess.Popen(
            chrome_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("✅ Chrome 실행 중...")
        print("⏳ Chrome이 완전히 시작될 때까지 5초 대기...\n")
        time.sleep(5)

    except Exception as e:
        print(f"⚠️  Chrome 자동 실행 실패: {e}")
        print("수동으로 실행해주세요:")
        print(f"   {manual_cmd}\n")

    with sync_playwright() as p:
        try:
            # 실행 중인 Chrome에 연결
            print("🔗 실행 중인 Chrome에 연결 시도...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Chrome 연결 성공!\n")

            # 기본 컨텍스트 가져오기
            contexts = browser.contexts
            if not contexts:
                print("❌ Chrome 컨텍스트를 찾을 수 없습니다.")
                return []

            context = contexts[0]
            pages = context.pages

            if not pages:
                print("❌ 열린 탭이 없습니다. Chrome에서 새 탭을 열어주세요.")
                return []

            # 첫 번째 페이지 사용 (또는 새 탭 생성)
            page = pages[0]
            print(f"✅ 현재 탭 사용: {page.url}\n")

            # 🔥 쿠키 주입!
            print("🍪 로그인 쿠키 주입 중...")
            context.add_cookies(cookies)
            print("✅ 쿠키 주입 완료!\n")

            # 각 이력서 순회
            for idx, resume in enumerate(resumes, 1):
                resume_no = resume.get('이력서번호')
                resume_link = resume.get('이력서링크')
                name = resume.get('이름', 'Unknown')

                # 이미 처리된 경우 건너뛰기
                if resume_no in processed_rnos:
                    print(f"[{idx}/{len(resumes)}] {name} (rNo={resume_no}) - ⏭️  건너뜀 (이미 처리됨)")
                    continue

                print(f"[{idx}/{len(resumes)}] {name} (rNo={resume_no})")

                try:
                    # 이력서 페이지 이동
                    page.goto(resume_link, wait_until='domcontentloaded', timeout=30000)

                    # JavaScript 실행 대기
                    time.sleep(3)

                    # 자기소개서 추출
                    intro_data = extract_introduction_from_page(page)

                    # 자격증 추출
                    cert_data = extract_certificates_from_page(page)

                    # 결과 구성
                    result = {
                        **resume,
                        "자기소개서": intro_data,
                        "자격증": cert_data,
                        "추출상태": "성공"
                    }
                    results.append(result)

                    # 출력
                    if intro_data:
                        print(f"   ✅ 자기소개서 {len(intro_data)}개 추출")
                        # 미리보기
                        if intro_data[0]['body_text']:
                            preview = intro_data[0]['body_text'][:100]
                            print(f"   📝 {preview}...")
                    else:
                        print(f"   ⚠️  자기소개서 없음")

                    if cert_data:
                        print(f"   ✅ 자격증 {len(cert_data)}개 추출")
                        # 자격증 목록 출력
                        cert_names = [c['자격증명'] for c in cert_data[:3]]
                        print(f"   🏆 {', '.join(cert_names)}{'...' if len(cert_data) > 3 else ''}")
                    else:
                        print(f"   ⚠️  자격증 없음")

                    # 🔥 즉시 JSON 파일에 저장
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    print(f"   💾 저장 완료 ({len(results)}/{len(resumes)})\n")

                    # 요청 간 간격
                    time.sleep(1)

                except Exception as e:
                    print(f"   ❌ 오류: {e}\n")

                    result = {
                        **resume,
                        "자기소개서": None,
                        "자격증": None,
                        "추출상태": f"오류: {str(e)}"
                    }
                    results.append(result)

                    # 🔥 오류 발생해도 즉시 저장
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    print(f"   💾 저장 완료 (오류 포함)\n")

                    time.sleep(1)

        except Exception as e:
            print(f"\n❌ Chrome 연결 실패: {e}")
            print("\n해결 방법:")
            print("1. Chrome을 디버깅 모드로 실행하세요:")
            print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            print("\n2. 또는 다른 터미널에서 위 명령어를 실행한 후 다시 시도하세요")
            import traceback
            traceback.print_exc()
            return []
        finally:
            # Chrome 프로세스 종료
            if chrome_process:
                print("\n🛑 Chrome 프로세스 종료 중...")
                try:
                    chrome_process.terminate()
                    chrome_process.wait(timeout=5)
                    print("✅ Chrome 종료 완료")
                except:
                    chrome_process.kill()
                    print("✅ Chrome 강제 종료 완료")

    return results


def main():
    # ⏱️ 시작 시간 기록
    start_time = time.time()

    # 이력서 목록 파일
    summary_json = "output/kspac2022_summary.json"
    output_file = "output/kspac2022_with_introduction.json"

    if not Path(summary_json).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {summary_json}")
        return

    print(f"📂 파일: {summary_json}\n")

    # 테스트: 처음 3개만 처리
    # 전체 처리하려면 max_count=None으로 변경
    results = extract_all_resumes(
        summary_json_path=summary_json,
        max_count=None,  # None으로 변경하면 전체 처리
        output_file=output_file
    )

    if not results:
        return

    # 최종 결과는 이미 저장되어 있음 (각 단계마다 저장했으므로)

    # ⏱️ 종료 시간 및 경과 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    # 통계
    success_count = sum(1 for r in results if r.get('추출상태') == '성공')
    fail_count = len(results) - success_count

    print("\n" + "="*80)
    print("✅ 완료!")
    print(f"   성공: {success_count}개")
    print(f"   실패: {fail_count}개")
    print(f"   총: {len(results)}개")
    print(f"\n💾 저장: {output_file}")
    print(f"\n⏱️  총 수행시간: {minutes}분 {seconds}초 ({elapsed_time:.2f}초)")
    if len(results) > 0:
        avg_time = elapsed_time / len(results)
        print(f"   평균 처리시간: {avg_time:.2f}초/건")
    print("="*80)


if __name__ == "__main__":
    main()
