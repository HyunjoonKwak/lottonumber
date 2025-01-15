import pandas as pd

# 파일 경로 정의
lotto_file_path = './lotto_win_info.csv'
wish_file_path_xlsx = './wish_number.xlsx'

# 로또 데이터 로드
lotto_data = pd.read_csv(lotto_file_path)
wish_data = pd.read_excel(wish_file_path_xlsx)

def update_rank_counts(rank_counts, rank_details, rank, draw_round):
    """
    등수별 횟수 및 회차 정보를 업데이트.
    """
    rank_counts[rank] += 1
    rank_details[rank].append(draw_round)

def generate_result_message(rank_counts, rank_details):
    """
    등수별 요약 및 상세 메시지 생성.
    """
    result_summary = [f"{rank} {count}회" for rank, count in rank_counts.items() if count > 0]
    detail_message = "; ".join(
        [f"{rank}: {', '.join(map(str, rank_details[rank]))}" for rank in rank_details if rank_details[rank]]
    )
    return ", ".join(result_summary), detail_message

def update_wish_results_with_details(lotto_df, wish_df):
    """
    로또 데이터와 희망 번호 데이터를 비교하여 등수를 계산하고,
    당첨 횟수 및 당첨 회차를 Result 컬럼에 추가.
    """
    results = []
    details = []

    for _, wish_row in wish_df.iterrows():
        # 희망 번호 집합 생성
        wish_set = {wish_row['Num1'], wish_row['Num2'], wish_row['Num3'],
                    wish_row['Num4'], wish_row['Num5'], wish_row['Num6']}
        
        # 각 등수별 횟수 및 회차 저장
        rank_counts = {'1등': 0, '2등': 0, '3등': 0, '4등': 0}
        rank_details = {'1등': [], '2등': [], '3등': [], '4등': []}

        for _, lotto_row in lotto_df.iterrows():
            # 당첨 번호 집합 및 보너스 번호
            draw_set = {lotto_row['Num1'], lotto_row['Num2'], lotto_row['Num3'],
                        lotto_row['Num4'], lotto_row['Num5'], lotto_row['Num6']}
            bonus_number = lotto_row['보너스']

            # 교집합 크기 계산
            match_count = len(wish_set.intersection(draw_set))

            if match_count == 6:
                update_rank_counts(rank_counts, rank_details, '1등', lotto_row['회차'])
            elif match_count == 5 and bonus_number in wish_set:
                update_rank_counts(rank_counts, rank_details, '2등', lotto_row['회차'])
            elif match_count == 5:
                update_rank_counts(rank_counts, rank_details, '3등', lotto_row['회차'])
            elif match_count == 4:
                update_rank_counts(rank_counts, rank_details, '4등', lotto_row['회차'])

        # 결과 메시지 생성
        if any(rank_counts.values()):
            result_summary, detail_message = generate_result_message(rank_counts, rank_details)
            results.append(result_summary)
            details.append(detail_message)
        else:
            results.append("낙첨")
            details.append("")

    # 결과를 DataFrame에 추가
    wish_df['Result'] = results
    wish_df['Details'] = details
    return wish_df

# 희망 번호와 로또 데이터를 비교하여 결과 업데이트
updated_wish_data = update_wish_results_with_details(lotto_data, wish_data)

# 변환된 .xlsx 파일에 업데이트된 데이터 저장
try:
    updated_wish_data.to_excel(wish_file_path_xlsx, index=False)
    print(f"결과가 성공적으로 업데이트되었습니다: {wish_file_path_xlsx}")
except Exception as e:
    print(f"파일 업데이트 실패: {wish_file_path_xlsx}\n오류: {e}")