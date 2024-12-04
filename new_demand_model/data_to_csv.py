import csv
import requests
import chardet

tm1 = "20240101"    # 시작일
tm2 = "20240630"    # 종료일
stn = "0"           # 전체지점 => 0
help = "0"          # 필드 도움말 없으면 0
authKey = "dD7wQQpvQFa-8EEKbzBWRQ"        # 인증키

# URL 문자열
url = f'https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php?tm1={tm1}&tm2={tm2}&stn={stn}&help={help}&authKey={authKey}'
# GET 요청
response = requests.get(url)

# 응답의 Content-Type 확인
content_type = response.headers.get('Content-Type')
print("Content-Type:", content_type)

# 인코딩 감지 및 디코딩
encoding = chardet.detect(response.content)['encoding']  # 인코딩 감지
decoded_content = response.content.decode(encoding or 'EUC-KR')  # 인코딩으로 디코딩
print("응답 내용:", decoded_content)  # 응답 내용을 확인하여 형식 파악

# 헤더 설정
header = [
    "TM", "STN", "WS_AVG", "WR_DAY", "WD_MAX", "WS_MAX", "WS_MAX_TM",
    "WD_INS", "WS_INS", "WS_INS_TM", "TA_AVG", "TA_MAX", "TA_MAX_TM",
    "TA_MIN", "TA_MIN_TM", "TD_AVG", "TS_AVG", "TG_MIN", "HM_AVG",
    "HM_MIN", "HM_MIN_TM", "PV_AVG", "EV_S", "EV_L", "FG_DUR",
    "PA_AVG", "PS_AVG", "PS_MAX", "PS_MAX_TM", "PS_MIN", "PS_MIN_TM",
    "CA_TOT", "SS_DAY", "SS_DUR", "SS_CMB", "SI_DAY", "SI_60M_MAX",
    "SI_60M_MAX_TM", "RN_DAY", "RN_D99", "RN_DUR", "RN_60M_MAX",
    "RN_60M_MAX_TM", "RN_10M_MAX", "RN_10M_MAX_TM", "RN_POW_MAX",
    "RN_POW_MAX_TM", "SD_NEW", "SD_NEW_TM", "SD_MAX", "SD_MAX_TM",
    "TE_05", "TE_10", "TE_15", "TE_30", "TE_50"
]

selected_columns = [
    "TM",         # 관측 시각
    "TA_AVG",     # 일 평균 기온
    "TA_MAX",     # 최고 기온
    "TA_MIN",     # 최저 기온
    "RN_DAY",     # 일 강수량
    "RN_DUR",     # 강수 지속 시간
    "HM_AVG",     # 일 평균 상대습도
    "HM_MIN",     # 최저 습도
    "WS_AVG",     # 일 평균 풍속
    "WS_MAX",     # 최대 풍속
    "WS_INS",     # 최대 순간 풍속
    "SS_DAY",     # 일조 시간
    "SI_DAY",     # 일사량
    "PS_AVG",     # 일 평균 해면기압
    "PS_MIN",     # 최저 해면기압
    "PS_MAX"      # 최고 해면기압
]

# 데이터를 줄 단위로 나누기
lines = decoded_content.strip().split("\n")

# 필요한 데이터 추출
# 데이터 6시간 단위로 추출함
is_reading = False
filtered_data = []
line_counter = 0
for line in lines:
    if line.startswith("#START7777"):
        is_reading = True
        continue
    elif line.startswith("#END7777"):
        is_reading = False
        continue
    elif line.startswith("#") or not is_reading:
        continue

    # 12번째 줄마다 데이터를 추가
    line_counter += 1
    if line_counter % 12 == 0:
        filtered_data.append(line.split())

# CSV 파일로 저장
csv_file = f"weather_data_{tm1}_{tm2}.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)  # 헤더 작성
    writer.writerows(filtered_data)   # 데이터 작성

print(f"데이터가 '{csv_file}' 파일에 성공적으로 저장되었습니다.")
