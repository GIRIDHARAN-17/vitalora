# Model Files Directory

Place your trained LSTM model files in this directory:

- `news_lstm_regression.h5` - Trained TensorFlow/Keras LSTM model
- `news_scaler.save` - Scikit-learn scaler (saved with joblib)
- `consciousness_encoder.save` - Consciousness label encoder (saved with joblib)

These files are required for the LSTM prediction service to work.

**Note:** These files are excluded from git (see `.gitignore`) due to their size.
