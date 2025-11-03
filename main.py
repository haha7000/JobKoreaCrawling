"""잡코리아 이력서 검색 메인 실행 파일"""
from src.runner import JobKoreaRunner


def main():
    """메인 실행 함수"""
    # ==================== 🔧 실행 설정 ====================

    EXCEL_PATH = "configs/jobkorea_Excel.xlsx"  # 엑셀 파일 경로

    # 페이지 설정
    START_PAGE = 1
    END_PAGE = 2
    PAGE_SIZE = 100
    DELAY = 1.0

    OUTPUT_DIR = "output"

    # 🔥 최근활동 필터링 설정 (분 단위)
    FILTER_ACTIVE_WITHIN_MINUTES = 240  # 240분(4시간) 이내 활동한 사용자만 추출

    # =====================================================

    # Runner 초기화 및 실행
    runner = JobKoreaRunner(
        excel_path=EXCEL_PATH,
        output_dir=OUTPUT_DIR
    )

    # 모든 계정 자동 실행
    runner.run_all_accounts(
        start_page=START_PAGE,
        end_page=END_PAGE,
        page_size=PAGE_SIZE,
        delay=DELAY,
        filter_active_within_minutes=FILTER_ACTIVE_WITHIN_MINUTES
    )


if __name__ == "__main__":
    main()
