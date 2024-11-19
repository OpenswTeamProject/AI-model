# 날씨 데이터와 수요 데이터를 합친다.
import pandas as pd
import numpy as np

day = 2022

for i in range(3):
    demand_file = '자전거_1차필터링/' +(str)(day + i)+ '_demand_filtered.csv'
    weather_file = 'weather/'+(str)(day + i)+ '_weather_filtered.csv'
    output_file = '자전거_최종필터링/'+(str)(day + i)+'_demand_merged.csv'

    demand_df = pd.read_csv(demand_file)
    weather_df = pd.read_csv(weather_file)

    merged_df = pd.merge(
        demand_df,  # 대여 데이터프레임
        weather_df,  # 날씨 데이터프레임
        left_on='대여일자',  # df의 기준 열
        right_on='일',  # weather_2022의 기준 열
        how='inner'  # 일치하는 데이터만 병합 (outer, left, right 가능)
    )
    merged_df = merged_df.drop(columns=['일'])

    # 평균 관련 칼럼 선택
    columns_to_modify = [
        '평균 기온 평균', '최고 기온 평균', '최저 기온 평균', '평균 풍속 평균',
        '최대 풍속 평균', '최대 순간 풍속 평균'
    ]

    columns_to_modify_mid = [
        '평균 습도 평균', '최저 습도 평균'
    ]

    columns_to_modify_big = [
        '평균 해면기압 평균',
        '최저 해면기압 평균', '최고 해면기압 평균'
    ]

    # 강수량 관련 칼럼
    precipitation_columns = ['강수량 합산', '강수 지속시간 합산']

    # 각 값에 -1 ~ +10 범위의 랜덤 값 추가
    for col in columns_to_modify:
        merged_df[col] += np.random.uniform(-2, 2, size=len(merged_df))

    for col in columns_to_modify_mid:
        merged_df[col] += np.random.uniform(-5, 5, size=len(merged_df))

    for col in columns_to_modify_big:
        merged_df[col] += np.random.uniform(-50, 50, size=len(merged_df))

    # 강수량 및 강수 지속시간 조정
    for col in precipitation_columns:
        mask = merged_df[col] != 0  # 값이 0이 아닌 경우만 선택
        random_values = np.random.uniform(0, 2, size=mask.sum())  # 강수량은 0~2 범위로 설정
        merged_df.loc[mask, col] += random_values

    # 강수량 합산이 음수인 경우 0으로 조정
    merged_df['강수량 합산'] = merged_df['강수량 합산'].clip(lower=0)

    # 강수 지속시간 합산이 24를 초과하면 24로 조정
    merged_df['강수 지속시간 합산'] = merged_df['강수 지속시간 합산'].clip(upper=24)

    # 최저와 최고 값의 관계 조정
    # 벡터화 방식으로 최저값과 최고값 정렬
    for min_col, max_col, avg_col in [
        ('최저 기온 평균', '최고 기온 평균', '평균 기온 평균'),
        ('최저 습도 평균', '평균 습도 평균', '평균 습도 평균'),  # 습도는 최저-평균 관계로 가정
        ('최저 해면기압 평균', '최고 해면기압 평균', '평균 해면기압 평균'),
        ('평균 풍속 평균', '최대 풍속 평균', '평균 풍속 평균')  # 풍속 데이터 처리
    ]:
        # 최저와 최고 값 비교하여 정렬
        merged_df[[min_col, max_col]] = np.sort(merged_df[[min_col, max_col]].values, axis=1)

        # 평균 값 계산
        merged_df[avg_col] = (merged_df[min_col] + merged_df[max_col]) / 2

    merged_df.to_csv(output_file, index=False)
    print(output_file + "완료")