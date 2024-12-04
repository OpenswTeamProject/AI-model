import pandas as pd

place_df = pd.read_csv('24.06_대여소정보.csv')
place_df_ID = place_df[['대여소번호']]
downtown = ['강남구', '서초구', '종로구', '중구', '용산구', '성동구', '마포구', '영등포구', '양천구', '송파구','동대문구','성동구','광진구','성북구', '서대문구']

for i in range(6):
    day = 2401
    input_file = '자전거 이용정보(일별)/서울특별시 공공자전거 이용정보(일별)_'+ (str)(day+i) +'_utf8.csv'
    output_file = '자전거_1차필터링/2024/'+ (str)(day+i) +'.csv'

    df = pd.read_csv(input_file, index_col=False)
    df.columns = df.columns.str.strip()
    # 대여일자별로 합치기
    df = df.groupby(["대여일자", "대여소번호"], as_index=False)["이용건수"].sum()

    # 날짜변환 후 대여소 없어진거 없애기
    df = df[df['대여소번호'].isin(place_df_ID['대여소번호'])]
    df['대여일자'] = pd.to_datetime(df['대여일자'], errors='coerce')  # 자동으로 날짜 형식을 감지

    df['주말'] = df['대여일자'].dt.weekday.isin([5, 6])

    df = pd.merge(
        df,
        place_df,
        left_on='대여소번호',
        right_on='대여소번호',
        how='left'  # 'left'로 df를 기준으로 결합
    )

    df['대중교통'] = df['보관소(대여소)명'].str.contains('역|버스|기차|정류장', regex=True)

    df['도심_외곽'] = df['자치구'].apply(lambda x: True if x in downtown else False)

    columns_to_keep = ['대여일자', '대여소번호', '이용건수', '주말', '대중교통', '도심_외곽']
    df = df[columns_to_keep]

    df.to_csv(output_file, index=False)
    print(output_file + " 완료")

ended_file = '자전거_1차필터링/2024_demand_filtered.csv'
file_list = []
for i in range(6):
    day = 2401
    # 파일 리스트
    file_list.append('자전거_1차필터링/2024/'+ (str)(day+i) +'.csv')

# DataFrame 병합
df_list = [pd.read_csv(file) for file in file_list]
result = pd.concat(df_list, ignore_index=True)
result.to_csv(ended_file, index=False)