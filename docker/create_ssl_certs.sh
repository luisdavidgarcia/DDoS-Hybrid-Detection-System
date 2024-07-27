#!/bin/bash

CERT_DIR="./certificates"

mkdir -p $CERT_DIR

COUNTRY="US"
STATE="California"
LOCALITY="San Luis Obispo"
ORGANIZATION="Example Company"
ORG_UNIT="IT"
COMMON_NAME="localhost"
EMAIL="admin@example.com"

openssl genpkey -algorithm RSA -out $CERT_DIR/server.key -pkeyopt rsa_keygen_bits:2048

openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr \
    -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$ORG_UNIT/CN=$COMMON_NAME/emailAddress=$EMAIL"

openssl x509 -req -days 365 -in $CERT_DIR/server.csr -signkey $CERT_DIR/server.key -out $CERT_DIR/server.crt

rm $CERT_DIR/server.csr

echo "SSL certificate and key have been generated in the $CERT_DIR directory."