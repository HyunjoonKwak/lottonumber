import pandas as pd
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox

# 파일 로드
file_path = './lotto_win_info.csv'
lotto_data = pd.read_csv(file_path)

def check_user_numbers():
    """
    사용자 입력 숫자 확인 및 로또 데이터 비교.
    """
    try:
        # 사용자 입력 가져오기
        user_input = input_var.get()
        # 쉼표(,)와 공백으로 분리
        input_numbers = list(map(int, user_input.replace(',', ' ').split()))

        if len(input_numbers) != 6:
            raise ValueError("숫자 6개를 정확히 입력해주세요.")

        # 입력 숫자 세트를 생성
        input_set = set(input_numbers)

        # 과거 당첨 번호와 비교
        results = {'1등': [], '2등': [], '3등': [], '4등': []}
        for index, row in lotto_data.iterrows():
            draw_set = {row['Num1'], row['Num2'], row['Num3'], row['Num4'], row['Num5'], row['Num6']}
            bonus_number = row['보너스']
            match_count = len(input_set.intersection(draw_set))
            
            if match_count == 6:
                # 6개 일치 -> 1등
                results['1등'].append({
                    '회차': row['회차'],
                    '추첨일': row['추첨일'],
                    '당첨번호': draw_set
                })
            elif match_count == 5 and bonus_number in input_set:
                # 5개 + 보너스 번호 일치 -> 2등
                results['2등'].append({
                    '회차': row['회차'],
                    '추첨일': row['추첨일'],
                    '당첨번호': draw_set,
                    '보너스번호': bonus_number
                })
            elif match_count == 5:
                # 5개 일치 -> 3등
                results['3등'].append({
                    '회차': row['회차'],
                    '추첨일': row['추첨일'],
                    '당첨번호': draw_set
                })
            elif match_count == 4:
                # 4개 일치 -> 4등
                results['4등'].append({
                    '회차': row['회차'],
                    '추첨일': row['추첨일'],
                    '당첨번호': draw_set
                })

        # 결과 처리
        result_message = ""
        for rank, matches in results.items():
            if matches:
                result_message += f"\n=== {rank} ===\n"
                for match in matches:
                    result_message += f"회차: {match['회차']}, 추첨일: {match['추첨일']}, 당첨번호: {match['당첨번호']}"
                    if rank == '2등':  # 2등일 경우 보너스 번호 추가 표시
                        result_message += f", 보너스번호: {match['보너스번호']}"
                    result_message += "\n"
        
        if not result_message:
            result_message = "입력한 번호는 과거 당첨 번호와 일치하지 않았습니다."
        
        # 메시지 박스로 결과 표시
        messagebox.showinfo("결과", result_message)
    except ValueError as e:
        messagebox.showerror("입력 오류", str(e))

# GUI 생성
root = Tk()
root.title("로또 당첨 번호 확인")

# 입력 안내 레이블
label = Label(root, text="숫자 6개를 쉼표 또는 공백으로 구분하여 입력하세요 (예: 1, 2, 3, 4, 5, 6 또는 1 2 3 4 5 6):")
label.pack(pady=10)

# 사용자 입력 필드
input_var = StringVar()
entry = Entry(root, textvariable=input_var, width=40)
entry.pack(pady=5)

# 확인 버튼
button = Button(root, text="확인", command=check_user_numbers)
button.pack(pady=10)

# 창 실행
root.mainloop()
