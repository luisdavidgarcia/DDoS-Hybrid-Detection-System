#!/bin/bash

rm logs/docker_stats_*.csv
rm logs/eve.json
rm logs/suricata.log

rm models/ae_xgb/*predictions.log
rm models/cnn_lstm/*predictions.log
rm models/dt/*predictions.log
rm models/rf/*predictions.log
rm models/xgb/*predictions.log
rm models/lr/*predictions.log