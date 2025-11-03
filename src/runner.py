"""잡코리아 검색 실행 관리자"""
import json
from pathlib import Path
from src.config import JobKoreaConfig
from src.payload_manager import PayloadManager
from src.scraper import JobKoreaScraper
from src.excel_config_parser import ExcelConfigParser
from src.account_manager import AccountManager


class JobKoreaRunner:
    """잡코리아 검색 실행을 관리하는 클래스"""

    def __init__(self, excel_path: str, output_dir: str = "output"):
        """
        Args:
            excel_path: 엑셀 파일 경로
            output_dir: 출력 디렉토리
        """
        self.excel_path = excel_path
        self.output_dir = output_dir
        self.account_manager = AccountManager(excel_path)

    def run_single_account(
        self,
        sheet_name: str,
        start_page: int = 1,
        end_page: int = 1,
        page_size: int = 100,
        delay: float = 1.0,
        filter_active_within_minutes: int = None
    ) -> bool:
        """
        단일 계정으로 검색 실행

        Args:
            sheet_name: 시트명 (계정 아이디)
            start_page: 시작 페이지
            end_page: 끝 페이지
            page_size: 페이지당 크기
            delay: 지연 시간(초)
            filter_active_within_minutes: 최근활동 필터링 (분 단위, None이면 필터링 안 함)

        Returns:
            성공 여부
        """
        # 1️⃣ 계정 정보 로드
        credentials = self.account_manager.get_credentials(sheet_name)

        if not credentials:
            print(f"⚠️  계정 '{sheet_name}'를 찾을 수 없습니다.")
            return False

        username = credentials['username']
        password = credentials['password']

        # 2️⃣ 검색 조건 로드
        parser = ExcelConfigParser(self.excel_path, sheet_name)
        search_config = parser.parse()

        if not search_config:
            print("⚠️  검색 설정이 없습니다.")
            return False

        # 검색 조건 출력
        self._print_search_config(sheet_name, username, search_config, start_page, end_page, page_size)

        # 3️⃣ 스크래퍼 초기화
        config = JobKoreaConfig(username=username, password=password)
        payload_manager = PayloadManager("data/payload_template.json")
        scraper = JobKoreaScraper(
            config=config,
            payload_manager=payload_manager,
            output_dir=self.output_dir,
            filter_active_within_minutes=filter_active_within_minutes
        )

        # 4️⃣ 데이터 수집
        people = scraper.scrape(
            start_page=start_page,
            end_page=end_page,
            page_size=page_size,
            delay=delay,
            job_name=search_config['job_names'],
            areas=search_config['areas'],
            education=search_config['education'],
            ages=search_config['ages'],
            genders=search_config['genders'],
            job_status=search_config['job_status']
        )

        # 5️⃣ 결과 저장
        self._save_results(people, sheet_name, scraper)

        return True

    def run_all_accounts(
        self,
        start_page: int = 1,
        end_page: int = 2,
        page_size: int = 200,
        delay: float = 1.0,
        filter_active_within_minutes: int = None
    ):
        """
        엑셀 파일의 모든 계정을 순차 실행

        Args:
            start_page: 시작 페이지
            end_page: 끝 페이지
            page_size: 페이지당 크기
            delay: 지연 시간(초)
            filter_active_within_minutes: 최근활동 필터링 (분 단위, None이면 필터링 안 함)
        """
        # 엑셀 파일 확인
        if not Path(self.excel_path).exists():
            print(f"❌ 엑셀 파일을 찾을 수 없습니다: {self.excel_path}")
            return

        # 실행 가능한 계정 시트 목록 가져오기
        valid_sheets = self.account_manager.get_valid_account_sheets()

        if not valid_sheets:
            print("❌ 실행 가능한 계정이 없습니다.")
            print(f"   - 계정 시트에 등록된 아이디: {self.account_manager.list_accounts()}")
            print(f"   - 엑셀의 모든 시트: {self.account_manager.get_all_sheet_names()}")
            return

        # 실행 정보 출력
        print(f"\n{'='*60}")
        print(f"🚀 다중 계정 실행 시작")
        print(f"📋 엑셀 파일: {self.excel_path}")
        print(f"🔢 실행 계정 수: {len(valid_sheets)}개")
        print(f"📄 실행 계정: {', '.join(valid_sheets)}")
        print(f"{'='*60}\n")

        # 순차 실행
        success_count = 0
        fail_count = 0

        for idx, sheet_name in enumerate(valid_sheets, 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(valid_sheets)}] 📌 계정: {sheet_name}")
            print(f"{'='*60}\n")

            success = self.run_single_account(
                sheet_name=sheet_name,
                start_page=start_page,
                end_page=end_page,
                page_size=page_size,
                delay=delay,
                filter_active_within_minutes=filter_active_within_minutes
            )

            if success:
                success_count += 1
            else:
                fail_count += 1

            print(f"\n{'='*60}")
            print(f"✅ [{idx}/{len(valid_sheets)}] {sheet_name} 완료")
            print(f"{'='*60}\n")

        # 최종 결과 출력
        print(f"\n{'='*60}")
        print(f"🎉 전체 실행 완료!")
        print(f"   ✅ 성공: {success_count}개")
        if fail_count > 0:
            print(f"   ❌ 실패: {fail_count}개")
        print(f"{'='*60}\n")

    def _print_search_config(self, sheet_name: str, username: str, config: dict, start_page: int, end_page: int, page_size: int):
        """검색 조건 출력"""
        print(f"🔑 계정: {username}")
        print(f"📄 검색조건 시트: {sheet_name}\n")

        print(f"🔍 검색 조건:")
        print(f"   대분류: {', '.join(config['categories'])}")
        print(f"   직무: {', '.join(config['job_names'][:5])}{'...' if len(config['job_names']) > 5 else ''} (총 {len(config['job_names'])}개)")
        print(f"   지역: {config['areas']}")
        print(f"   학력: {config['education']}")
        print(f"   나이: {config['ages']}")
        print(f"   구직상태: {config['job_status']}")
        print(f"   페이지: {start_page} ~ {end_page} (크기: {page_size})\n")

    def _save_results(self, people: list, sheet_name: str, scraper):
        """결과 저장"""
        if people:
            # 파일명: 시트명 기반
            safe_sheet_name = sheet_name.replace('@', '_').replace('.', '_')
            json_path = Path(self.output_dir) / f"{safe_sheet_name}_summary.json"
            excel_path = Path(self.output_dir) / f"{safe_sheet_name}_결과.xlsx"

            # JSON 저장
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(people, f, ensure_ascii=False, indent=2)

            # 엑셀 저장
            scraper.exporter.save(people, str(excel_path))

            print(f"✅ 완료: {len(people)}명 수집")
            print(f"   📄 JSON: {json_path}")
            print(f"   📊 Excel: {excel_path}")
        else:
            print(f"⚠️  수집된 데이터 없음")
