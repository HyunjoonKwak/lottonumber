import time
from datetime import datetime, timedelta
import pandas as pd
import os
from collections import Counter
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

def fetch_lotto_data(drw_no):
    """
    로또 데이터를 특정 회차 번호로 가져옵니다.
    """
    base_url = "https://dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
    req_url = base_url + str(drw_no)
    
    session = requests.Session()
    retry = Retry(
        total=5,  # 총 재시도 횟수
        backoff_factor=1,  # 재시도 간 대기 시간
        status_forcelist=[429, 500, 502, 503, 504],  # 재시도할 HTTP 상태 코드
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    try:
        response = session.get(req_url, timeout=10)
        response.raise_for_status()
        lotto_data = response.json()
        
        if lotto_data.get("returnValue") != "success":
            print(f"회차 {drw_no} 데이터가 없습니다.")
            return None
        return lotto_data
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: 회차 {drw_no}, 오류: {e}")
        return None

def calculate_next_draw(latest_draw_number, latest_draw_date):
    """
    최신 회차 번호와 날짜를 기반으로 다음 회차와 추첨일을 계산합니다.
    """
    current_date = datetime.now()
    latest_date = datetime.strptime(latest_draw_date, "%Y-%m-%d")
    
    # 매주 토요일마다 회차가 증가
    next_draw_date = latest_date + timedelta(days=7)
    
    if current_date >= next_draw_date:  # 다음 회차 추첨일이 현재 날짜보다 이전이면
        return latest_draw_number + 1, next_draw_date.strftime("%Y-%m-%d")
    return None, None

def get_lotto_win_info(min_drw_no, max_drw_no):
    """
    지정된 범위의 로또 데이터를 가져옵니다.
    """
    if os.path.exists("lotto_win_info.csv"):
        existing_data = pd.read_csv("lotto_win_info.csv")
        existing_draws = set(existing_data["회차"])
    else:
        existing_data = pd.DataFrame()
        existing_draws = set()

    data = {
        "회차": [], "추첨일": [], "Num1": [], "Num2": [], "Num3": [],
        "Num4": [], "Num5": [], "Num6": [], "보너스": [],
        "총판매액": [], "1등당첨금": [], "1등당첨인원": [], "1등수령액": []
    }

    for i in tqdm(range(min_drw_no, max_drw_no + 1)):
        if i in existing_draws:
            print(f"회차 {i}는 이미 저장되어 있습니다. 스킵합니다.")
            continue
        
        lotto_no = fetch_lotto_data(i)
        if lotto_no:
            data["회차"].append(lotto_no['drwNo'])
            data["추첨일"].append(lotto_no['drwNoDate'])
            data["Num1"].append(lotto_no['drwtNo1'])
            data["Num2"].append(lotto_no['drwtNo2'])
            data["Num3"].append(lotto_no['drwtNo3'])
            data["Num4"].append(lotto_no['drwtNo4'])
            data["Num5"].append(lotto_no['drwtNo5'])
            data["Num6"].append(lotto_no['drwtNo6'])
            data["보너스"].append(lotto_no['bnusNo'])
            data["총판매액"].append(lotto_no['totSellamnt'])
            data["1등당첨금"].append(lotto_no['firstAccumamnt'])
            data["1등당첨인원"].append(lotto_no['firstPrzwnerCo'])
            data["1등수령액"].append(lotto_no['firstWinamnt'])
        else:
            print(f"회차 {i} 데이터가 없습니다. 스킵합니다.")

    new_data = pd.DataFrame(data)
    if not new_data.empty:
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        combined_data = existing_data

    return combined_data

def main_task():
    """
    토요일 밤 10시에 실행할 메인 작업.
    """
    print("로또 데이터 업데이트 시작...")
    
    # 기존 데이터 로드
    if os.path.exists("lotto_win_info.csv"):
        lotto_df = pd.read_csv("lotto_win_info.csv")
        latest_draw = lotto_df["회차"].max()  # 가장 최근 저장된 회차
        latest_draw_date = lotto_df[lotto_df["회차"] == latest_draw]["추첨일"].values[0]
    else:
        lotto_df = pd.DataFrame()
        latest_draw = 1154
        latest_draw_date = "2025-01-11"  # 초기값

    # 최신 회차와 추첨일 출력
    print(f"최신 추첨 회차: {latest_draw}, 추첨일: {latest_draw_date}")
    
    # 현재까지 저장된 데이터 기반으로 1~45번 숫자의 등장 빈도 계산
    num_list = lotto_df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Num6']].values.flatten()
    count = Counter(num_list)
    common_num_45 = count.most_common(45)  # 1~45번 숫자의 빈도
    # 결과 출력 
    print("\n=== 숫자별 등장 빈도 (1~45) ===")
    for num, freq in common_num_45:
        print(f"숫자 {num}: {freq}회")

    # # 상위 10개 빈출 숫자 출력
    # common_num_10 = count.most_common(10)
    # print("\n=== 상위 10개 빈출 숫자 ===")
    # for num, freq in common_num_10:
    #     print(f"숫자 {num}: {freq}회")

    # 다음 회차 계산
    next_draw, next_draw_date = calculate_next_draw(latest_draw, latest_draw_date)
    if next_draw is None:
        print("다음 회차 추첨일이 아직 오지 않았습니다.")
        return
    
    print(f"다음 추첨 회차: {next_draw}, 추첨일: {next_draw_date}")
    
    # 다음 회차 데이터 가져오기
    updated_lotto_df = get_lotto_win_info(next_draw, next_draw)
    if updated_lotto_df.empty:
        print("새로운 데이터를 추가하지 못했습니다. 다시 시도하세요.")
        return
    
    # 데이터 저장
    combined_data = pd.concat([lotto_df, updated_lotto_df], ignore_index=True)
    combined_data.to_csv("./lotto_win_info.csv", index=False)
    print("데이터가 성공적으로 업데이트되었습니다.")

    # 1~45번 숫자의 등장 빈도 계산
    num_list = combined_data[['Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Num6']].values.flatten()
    count = Counter(num_list)
    common_num_45 = count.most_common(45)  # 1~45번 숫자의 빈도
    
    print("\n=== 숫자별 등장 빈도 (1~45) ===")
    for num, freq in common_num_45:
        print(f"숫자 {num}: {freq}회")
    
    # # 상위 10개 빈출 숫자 출력
    # common_num_10 = count.most_common(10)
    # print("\n=== 상위 10개 빈출 숫자 ===")
    # for num, freq in common_num_10:
    #     print(f"숫자 {num}: {freq}회")

def background_scheduler():
    """
    백그라운드 스케줄러. 1초마다 현재 시간이 토요일 밤 10시인지 체크하고 작업 실행.
    """
    while True:
        now = datetime.now()
        if now.weekday() == 5 and now.hour == 22 and now.minute == 0:  # 토요일 밤 10시
            main_task()
            time.sleep(60)  # 실행 후 1분 대기
        time.sleep(1)  # 1초마다 체크

if __name__ == "__main__":
    main_task()
    background_scheduler()
