# Remove log files from the logs directory
Remove-Item "logs/docker_stats_*.csv" -Force -ErrorAction SilentlyContinue
Remove-Item "logs/eve.json" -Force -ErrorAction SilentlyContinue
Remove-Item "logs/suricata.log" -Force -ErrorAction SilentlyContinue

# Remove model prediction logs from each model's directory
Remove-Item "models/ae_xgb/ae_xgb_binary_model_predictions.log" -Force -ErrorAction SilentlyContinue
Remove-Item "models/cnn_lstm/cnn_lstm_binary_model_predictions.log" -Force -ErrorAction SilentlyContinue
Remove-Item "models/dt/decision_tree_binary_model_predictions.log" -Force -ErrorAction SilentlyContinue
Remove-Item "models/rf/random_forest_binary_model_predictions.log" -Force -ErrorAction SilentlyContinue
Remove-Item "models/xgb/xgboost_binary_model_predictions.log" -Force -ErrorAction SilentlyContinue
Remove-Item "models/lr/logistic_regression_binary_model_predictions.log" -Force -ErrorAction SilentlyContinue