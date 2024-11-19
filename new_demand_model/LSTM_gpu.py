import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# GPU 확인 및 설정
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print("Using GPU:", gpus[0])
    except RuntimeError as e:
        print(e)
else:
    print("No GPU found. Using CPU.")

# 기존 LSTM 코드
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

data = pd.read_csv('demand_bike_dataset_2022_2024.csv')

# 2. 데이터 전처리
data['대여일자'] = pd.to_datetime(data['대여일자'])  # 날짜 형식 변환
data.set_index('대여일자', inplace=True)  # 대여일자를 인덱스로 설정

# 대여소 번호를 정수로 변환 (카테고리 변수 처리)
data['대여소번호'] = data['대여소번호'].astype('category').cat.codes

# 데이터 정규화
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# 3. 시계열 데이터 준비
sequence_length = 7  # 지난 7일 데이터를 입력으로 사용
X, y = [], []

for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i])  # 지난 7일 데이터
    y.append(scaled_data[i, data.columns.get_loc('이용건수')])  # 다음날의 이용 건수

X, y = np.array(X), np.array(y)

# 4. 데이터 분할
split = int(len(X) * 0.8)  # 80% 학습 데이터, 20% 테스트 데이터
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 5. LSTM 모델 정의
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(50),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# 6. 모델 학습
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), verbose=1)

# 7. 예측
y_pred = model.predict(X_test)

# 8. 역정규화
y_pred_rescaled = scaler.inverse_transform(
    np.hstack((np.zeros((y_pred.shape[0], scaled_data.shape[1] - 1)), y_pred))
)[:, -1]
y_test_rescaled = scaler.inverse_transform(
    np.hstack((np.zeros((y_test.shape[0], scaled_data.shape[1] - 1)), y_test.reshape(-1, 1)))
)[:, -1]

# 9. 성능 평가
rmse = np.sqrt(mean_squared_error(y_test_rescaled, y_pred_rescaled))
print(f"LSTM RMSE: {rmse:.2f}")

# 10. 예측 결과 시각화
plt.figure(figsize=(12, 6))
plt.plot(range(len(y_test_rescaled)), y_test_rescaled, label="Actual", marker='o')
plt.plot(range(len(y_pred_rescaled)), y_pred_rescaled, label="Predicted", marker='x')
plt.title("LSTM Predictions vs Actual")
plt.xlabel("Test Data Index")
plt.ylabel("Usage Count")
plt.legend()
plt.show()
