import json
import joblib
import numpy as np
import logging
from collections import defaultdict
import os

print("Current working directory: ", os.getcwd())  

# Load the LabelEncoders for categorical features
service_encoder = joblib.load('/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/notebooks/service_encoder.joblib')
flag_encoder = joblib.load('/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/notebooks/flag_encoder.joblib')

# Display the original-to-encoded mappings for each encoder
def display_encoder_mapping(encoder, column_name):
    original_to_encoded = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))
    print(f"Mapping for {column_name}:")
    for original, encoded in original_to_encoded.items():
        print(f"  {original} -> {encoded}")

# Display mappings
display_encoder_mapping(service_encoder, "service")
display_encoder_mapping(flag_encoder, "flag")


# import joblib
# import numpy as np

# # Load the scaler
# scaler = joblib.load('/Users/lucky/GitHub/DDoS-Hybrid-Detection-System/models/xgb/standard_scaler.joblib')

# # Sample data you provided
# sample_data = np.array([
#     [-0.6231403252961637, 0.772988222530456, -0.02416949471541725, -0.05230874700047722],
#     [0.8026534204988017, 0.772988222530456, -0.025239331962467176, -0.05230874700047722],
#     [1.0742331816026047, -0.9059612585963958, -0.025692074681508595, -0.05230874700047722],
#     [-0.4194555044683115, 0.772988222530456, -0.024972647895086613, 0.10906570503816887],
#     [-0.4194555044683115, 0.772988222530456, -0.025074980153500088, -0.043995577632608786]
# ])

# # Apply the scaler's transform (optional if the data is already scaled)
# # scaled_data = scaler.transform(sample_data)
# scaled_data = sample_data

# # Inverse transform to check if scaling is correct
# inverse_data = scaler.inverse_transform(scaled_data)

# # Display the results
# # print("Scaled data:\n", scaled_data)
# print("Inverse transformed data:\n", inverse_data)