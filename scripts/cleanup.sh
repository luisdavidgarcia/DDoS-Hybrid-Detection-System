#!/bin/bash

rm logs/docker_stats_*.csv
rm logs/eve.json
rm logs/suricata.log

rm models/ae_xgb/ae_xgb_binary_model_predictions.log
rm models/cnn_lstm/cnn_lstm_binary_model_predictions.log
rm models/dt/decision_tree_binary_model_predictions.log
rm models/rf/random_forest_binary_model_predictions.log
rm models/xgb/xgboost_binary_model_predictions.log
rm models/lr/logistic_regression_binary_model_predictions.log