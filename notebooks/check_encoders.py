# import json
# import joblib
# import numpy as np
# import logging
# from collections import defaultdict
# import os

# print("Current working directory: ", os.getcwd())  

# # Load the LabelEncoders for categorical features
# service_encoder = joblib.load('notebooks/service_encoder.joblib')
# flag_encoder = joblib.load('notebooks/flag_encoder.joblib')

# # Display the original-to-encoded mappings for each encoder
# def display_encoder_mapping(encoder, column_name):
#     original_to_encoded = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))
#     print(f"Mapping for {column_name}:")
#     for original, encoded in original_to_encoded.items():
#         print(f"  {original} -> {encoded}")

# # Display mappings
# display_encoder_mapping(service_encoder, "service")
# display_encoder_mapping(flag_encoder, "flag")
import joblib
import numpy as np

# Load the scaler
scaler = joblib.load('/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/models/xgb/standard_scaler.joblib')

# Sample data provided
sample_data = np.array([[24, 1, 108, 58]])

# Apply the scaler to the data
scaled_data = scaler.transform(sample_data)

# Inverse transform to check if scaling is correct
inverse_data = scaler.inverse_transform(scaled_data)

# Display the results
print("Scaled data:", scaled_data)
print("Inverse transformed data:", inverse_data)