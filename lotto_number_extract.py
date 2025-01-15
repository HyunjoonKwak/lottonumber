import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
from collections import Counter
import csv
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 프록시 설정
proxies = {
    "http": "http://your_proxy_address:port",
    "https": "https://your_proxy_address:port",
}

def fetch_lotto_data(drw_no):
    base_url = "https://dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
    req_url = base_url + str(drw_no)
    
    session = requests.Session()
    retry = Retry(
        total=5,  # 총 재시도 횟수
        backoff_factor=1,  # 재시도 간 대기 시간 (1초, 2초, 4초, 8초, 16초)
        status_forcelist=[429, 500, 502, 503, 504],  # 재시도할 HTTP 상태 코드
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    try:
        req_lotto = session.post(req_url, timeout=10)  # 타임아웃 설정
        # req_lotto = session.post(req_url, timeout=10, proxies=proxies)  # 타임아웃 및 프록시 설정

        req_lotto.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        lotto_no = req_lotto.json()
        return lotto_no
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: 회차 {drw_no}, 오류: {e}")
        return None

def get_lotto_win_info(min_drw_no, max_drw_no):
    # 기존 데이터 로드
    if os.path.exists("lotto_win_info.csv"):
        existing_data = pd.read_csv("lotto_win_info.csv")
        existing_draws = set(existing_data["회차"])
    else:
        existing_data = pd.DataFrame()
        existing_draws = set()

    data = {
        "회차": [],
        "추첨일": [], 
        "Num1": [], 
        "Num2": [], 
        "Num3": [], 
        "Num4": [], 
        "Num5": [], 
        "Num6": [],
        "보너스": [], 
        "총판매액": [], 
        "1등당첨금": [], 
        "1등당첨인원": [], 
        "1등수령액": []
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

    new_data = pd.DataFrame(data)
    if not new_data.empty:
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        combined_data = existing_data

    return combined_data

def main():
    lotto_df = get_lotto_win_info(1, 1154)
    print(lotto_df.head())
    lotto_df.to_csv("./lotto_win_info.csv", index=False)

if __name__ == "__main__":
    main()
