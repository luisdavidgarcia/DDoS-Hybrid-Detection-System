import json
import joblib
import numpy as np
import logging
from collections import defaultdict
import os

print("Current working directory: ", os.getcwd())  

# Load the LabelEncoders for categorical features
service_encoder = joblib.load('notebooks/service_encoder.joblib')
flag_encoder = joblib.load('notebooks/flag_encoder.joblib')

# Display the original-to-encoded mappings for each encoder
def display_encoder_mapping(encoder, column_name):
    original_to_encoded = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))
    print(f"Mapping for {column_name}:")
    for original, encoded in original_to_encoded.items():
        print(f"  {original} -> {encoded}")

# Display mappings
display_encoder_mapping(service_encoder, "service")
display_encoder_mapping(flag_encoder, "flag")