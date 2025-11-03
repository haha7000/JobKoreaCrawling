"""잡코리아 이력서 검색 메인 실행 파일"""
from src.runner import JobKoreaRunner


def main():
    """메인 실행 함수"""

    # config 파일 경로(엑셀)
    EXCEL_PATH = "configs/jobkorea_Excel.xlsx"

    # - 잡코리아 API는 페이지 단위로 이력서를 조회합니다
    START_PAGE = 1          # 검색 시작 페이지 (1부터 시작)
    END_PAGE = 2            # 검색 종료 페이지 (예: 2페이지까지 검색)
    PAGE_SIZE = 100         # 페이지당 조회할 이력서 수 (최대 100개)
                           # 예) START_PAGE=1, END_PAGE=2, PAGE_SIZE=100 → 총 200명 조회

    DELAY = 1.0            # 페이지 요청 간 지연 시간(초)
                           # - API 과부하 방지 및 차단 회피용
                           # - 1.0초 권장 (너무 짧으면 차단 위험)

    # 결과 저장 디렉토리
    OUTPUT_DIR = "output"


    # - 최근 N분 이내에 활동한 사용자만 필터링
    # - None으로 설정하면 필터링 안 함 (모든 이력서 수집)
    # - 예) 240 = 4시간 이내 활동한 사용자만 추출
    #      30 = 30분 이내 활동한 사용자만 추출
    FILTER_ACTIVE_WITHIN_MINUTES = 240

    # =====================================================

    # Runner 초기화 및 실행
    # - JobKoreaRunner: 잡코리아 검색을 실행하는 클래스
    # - 엑셀 파일에서 계정 정보와 검색 조건을 읽어서 자동으로 검색 실행
    runner = JobKoreaRunner(
        excel_path=EXCEL_PATH,      # 설정 파일 경로
        output_dir=OUTPUT_DIR        # 결과 저장 폴더
    )

    # 📋 모든 계정 자동 실행
    # - 엑셀의 [계정정보] 시트에 등록된 모든 계정을 순차적으로 실행
    # - 각 계정마다 별도의 JSON/엑셀 파일로 결과 저장
    runner.run_all_accounts(
        start_page=START_PAGE,                              # 시작 페이지
        end_page=END_PAGE,                                  # 종료 페이지
        page_size=PAGE_SIZE,                                # 페이지당 이력서 수
        delay=DELAY,                                        # 요청 간 지연 시간
        filter_active_within_minutes=FILTER_ACTIVE_WITHIN_MINUTES  # 최근활동 필터링
    )


if __name__ == "__main__":
    main()
