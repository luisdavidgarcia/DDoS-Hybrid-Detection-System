#!/bin/bash

echo "Creating Docker network..."
docker network create ddos_network

echo "Building Snort container..."
cat <<EOF > Dockerfile.snort
FROM ubuntu:latest
RUN apt-get update && apt-get install -y snort
# If you have custom configurations, uncomment and provide the files
# COPY snort.conf /etc/snort/snort.conf
# COPY rules/ /etc/snort/rules/
CMD ["snort", "-i", "eth0"]
EOF

docker build -f Dockerfile.snort -t snort_image .

echo "Building Apache server container..."
cat <<EOF > Dockerfile.apache
FROM httpd:2.4
COPY httpd-ssl.conf /usr/local/apache2/conf/extra/httpd-ssl.conf
COPY certificates/ /usr/local/apache2/conf/certificates/
RUN echo "Include conf/extra/httpd-ssl.conf" >> /usr/local/apache2/conf/httpd.conf
EXPOSE 80 443
EOF

docker build -f Dockerfile.apache -t apache_server_image .

echo "Building Grafana container..."
docker pull grafana/grafana

echo "Building attacker containers..."
cat <<EOF > Dockerfile.attacker
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip hping3
RUN pip3 install scapy
COPY attack_scripts/ /app/attack_scripts/
WORKDIR /app/attack_scripts
CMD ["python3", "attack_script.py"]
EOF

docker build -f Dockerfile.attacker -t attacker_image .

echo "Building normal traffic container..."
cat <<EOF > Dockerfile.normal_traffic
FROM python:3.10
WORKDIR /app
COPY normal_traffic.py /app/
CMD ["python", "normal_traffic.py"]
EOF

docker build -f Dockerfile.normal_traffic -t normal_traffic_image .

echo "Building traditional ML model container..."
cat <<EOF > Dockerfile.ml_model
FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "ml_model.py"]
EOF

docker build -f Dockerfile.ml_model -t ml_model_image .

echo "Building deep learning model container..."
cat <<EOF > Dockerfile.dl_model
FROM tensorflow/tensorflow:latest-gpu
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "dl_model.py"]
EOF

docker build -f Dockerfile.dl_model -t dl_model_image .

echo "Docker network setup and image building completed successfully."