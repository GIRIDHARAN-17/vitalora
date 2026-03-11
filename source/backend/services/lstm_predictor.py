from __future__ import annotations

from pathlib import Path

import numpy as np
import tensorflow as tf
from joblib import load


class LSTMPredictor:
    _instance: LSTMPredictor | None = None
    _model: tf.keras.Model | None = None
    _scaler: object | None = None
    _consciousness_encoder: object | None = None

    def __init__(self) -> None:
        if LSTMPredictor._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        self._load_models()

    @classmethod
    def get_instance(cls) -> LSTMPredictor:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_models(self) -> None:
        """Load LSTM model, scaler, and consciousness encoder."""
        models_dir = Path(__file__).parent.parent / "models"

        model_path = models_dir / "news_lstm_regression.h5"
        scaler_path = models_dir / "news_scaler.save"
        encoder_path = models_dir / "consciousness_encoder.save"

        if not model_path.exists():
            raise FileNotFoundError(
                f"LSTM model not found at {model_path}. "
                "Please place news_lstm_regression.h5 in backend/models/"
            )
        if not scaler_path.exists():
            raise FileNotFoundError(
                f"Scaler not found at {scaler_path}. "
                "Please place news_scaler.save in backend/models/"
            )
        if not encoder_path.exists():
            raise FileNotFoundError(
                f"Encoder not found at {encoder_path}. "
                "Please place consciousness_encoder.save in backend/models/"
            )

        # Try loading model normally first
        try:
            self._model = tf.keras.models.load_model(
                str(model_path), compile=False)
        except ValueError:
            # Model was saved with older TensorFlow version that used deprecated 'time_major' parameter
            # Monkey patch LSTM.from_config to filter out this parameter
            original_from_config = tf.keras.layers.LSTM.from_config
            original_from_config_func = original_from_config.__func__

            @classmethod
            def patched_from_config(cls, config):
                """Patched from_config that removes deprecated time_major parameter."""
                if isinstance(config, dict):
                    config = config.copy()
                    config.pop('time_major', None)
                return original_from_config_func(cls, config)

            tf.keras.layers.LSTM.from_config = patched_from_config
            try:
                self._model = tf.keras.models.load_model(
                    str(model_path), compile=False)
            finally:
                # Restore original method
                tf.keras.layers.LSTM.from_config = original_from_config

        self._scaler = load(str(scaler_path))
        self._consciousness_encoder = load(str(encoder_path))

    def predict_news_score(self, sequence: list[dict]) -> float:
        """
        Predict NEWS2 score from a 30-step vital sequence.

        Args:
            sequence: List of 30 vital dicts with keys:
                - respiration_rate: int
                - spo2: int
                - oxygen_support: int
                - systolic_bp: int
                - heart_rate: int
                - temperature: float
                - consciousness: str (A, V, P, U)

        Returns:
            Predicted NEWS2 score (1-10)
        """
        if len(sequence) != 30:
            raise ValueError(
                f"Sequence must have exactly 30 steps, got {len(sequence)}")

        # Prepare features array
        features = []
        for step in sequence:
            # Encode consciousness (LabelEncoder expects 1D input; returns scalar int)
            # Training pipeline uses LabelEncoder, so we keep it as a single numeric feature.
            consciousness_encoded = int(
                self._consciousness_encoder.transform(
                    [step["consciousness"]])[0]
            )

            # Extract numeric features
            feature_vector = [
                step["respiration_rate"],
                step["spo2"],
                step["oxygen_support"],
                step["systolic_bp"],
                step["heart_rate"],
                step["temperature"],
                consciousness_encoded,
            ]
            features.append(feature_vector)

        # Convert to numpy array and reshape for LSTM (samples, timesteps, features)
        X = np.array(features, dtype=np.float32)
        X = X.reshape(1, 30, -1)

        # Scale features
        X_scaled = self._scaler.transform(
            X.reshape(-1, X.shape[-1])).reshape(X.shape)

        # Predict
        prediction = self._model.predict(X_scaled, verbose=0)[0][0]

        # Clamp to NEWS2 range (1-10)
        return float(np.clip(prediction, 1.0, 10.0))


def predict_news_score(sequence: list[dict]) -> float:
    """Convenience function to get singleton instance and predict."""
    predictor = LSTMPredictor.get_instance()
    return predictor.predict_news_score(sequence)
