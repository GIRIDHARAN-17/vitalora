"""
Train LSTM model for NEWS2 score prediction.

Usage:
    python -m backend.scripts.train_lstm
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Input, LSTM
from tensorflow.keras.models import Sequential

# ==============================
# CONFIG
# ==============================
TIME_STEPS = 30
FEATURES = 7


def calculate_news(row: pd.Series) -> int:
    """Calculate NEWS2 score from vital signs."""
    score = 0

    # Respiration Rate
    if row["respiration_rate"] <= 8 or row["respiration_rate"] >= 25:
        score += 3
    elif 9 <= row["respiration_rate"] <= 11 or 21 <= row["respiration_rate"] <= 24:
        score += 2

    # SpO2
    if row["spo2"] <= 91:
        score += 3
    elif 92 <= row["spo2"] <= 93:
        score += 2
    elif 94 <= row["spo2"] <= 95:
        score += 1

    # Oxygen Support
    if row["oxygen_support"] == 1:
        score += 2

    # Systolic BP
    if row["systolic_bp"] <= 90 or row["systolic_bp"] >= 220:
        score += 3
    elif 91 <= row["systolic_bp"] <= 100:
        score += 2
    elif 101 <= row["systolic_bp"] <= 110:
        score += 1

    # Heart Rate
    if row["heart_rate"] <= 40 or row["heart_rate"] >= 131:
        score += 3
    elif 41 <= row["heart_rate"] <= 50 or 111 <= row["heart_rate"] <= 130:
        score += 2
    elif 91 <= row["heart_rate"] <= 110:
        score += 1

    # Temperature
    if row["temperature"] <= 35.0:
        score += 3
    elif 35.1 <= row["temperature"] <= 36.0:
        score += 1
    elif 38.1 <= row["temperature"] <= 39.0:
        score += 1
    elif row["temperature"] >= 39.1:
        score += 2

    # Consciousness (encoded: A=0, V=1, P=2, U=3)
    if row["consciousness"] != 0:
        score += 3

    # Scale to 1–10
    return min(max(score, 1), 10)


def main() -> None:
    """Train LSTM model and save to backend/models/."""
    # Get paths
    script_dir = Path(__file__).parent.parent
    dataset_path = script_dir / "dataset" / "synthetic_icu_timeseries.csv"
    models_dir = script_dir / "models"
    models_dir.mkdir(exist_ok=True)

    # ==============================
    # 1. Load Dataset
    # ==============================
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)

    # Sort by patient and time
    df = df.sort_values(["patient_id", "timestamp"])

    # ==============================
    # 2. Encode Consciousness
    # ==============================
    print("Encoding consciousness labels...")
    le = LabelEncoder()
    df["consciousness"] = le.fit_transform(df["consciousness"])

    # ==============================
    # 3. NEWS2 Score Calculation
    # ==============================
    print("Calculating NEWS2 scores...")
    df["news_score"] = df.apply(calculate_news, axis=1)

    # ==============================
    # 4. Create Sequences
    # ==============================
    print("Creating sequences...")
    feature_cols = [
        "respiration_rate",
        "spo2",
        "oxygen_support",
        "systolic_bp",
        "heart_rate",
        "temperature",
        "consciousness"
    ]

    X, y = [], []

    for patient in df["patient_id"].unique():
        patient_data = df[df["patient_id"] == patient].copy()

        for i in range(len(patient_data) - TIME_STEPS):
            seq = patient_data.iloc[i:i+TIME_STEPS][feature_cols].values
            target = patient_data.iloc[i+TIME_STEPS]["news_score"]

            X.append(seq)
            y.append(target)

    X = np.array(X)
    y = np.array(y)

    print(f"Created {len(X)} sequences")

    # ==============================
    # 5. Normalize Features
    # ==============================
    print("Normalizing features...")
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X.reshape(-1, FEATURES))
    X_scaled = X_scaled.reshape(-1, TIME_STEPS, FEATURES)

    # Normalize target (1–10 → 0–1)
    y = y / 10.0

    # ==============================
    # 6. Train-Test Split
    # ==============================
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # ==============================
    # 7. Build LSTM Model (Regression)
    # ==============================
    print("Building LSTM model...")
    model = Sequential([
        Input(shape=(TIME_STEPS, FEATURES)),
        LSTM(64),
        Dense(32, activation='relu'),
        Dense(1, activation='linear')   # regression output
    ])

    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )

    early_stop = EarlyStopping(patience=3, restore_best_weights=True)

    # ==============================
    # 8. Train Model
    # ==============================
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=20,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1
    )

    # ==============================
    # 9. Evaluate
    # ==============================
    print("\nEvaluating model...")
    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss (MSE): {test_loss:.4f}")
    print(f"Test MAE: {test_mae:.4f}")

    # ==============================
    # 10. Save Model
    # ==============================
    print("\nSaving model and artifacts...")
    model_path = models_dir / "news_lstm_regression.h5"
    scaler_path = models_dir / "news_scaler.save"
    encoder_path = models_dir / "consciousness_encoder.save"

    model.save(str(model_path))
    joblib.dump(scaler, str(scaler_path))
    joblib.dump(le, str(encoder_path))

    print(f"Model saved: {model_path}")
    print(f"Scaler saved: {scaler_path}")
    print(f"Encoder saved: {encoder_path}")
    print("\nModel trained and saved successfully!")


if __name__ == "__main__":
    main()
