#!/bin/bash

# Set variables
COUNTRY="PT" 
STATE="MAFRA"
CITY="LISBON"
ORGANIZATION="My Company"
ORG_UNIT="IT Department"
COMMON_NAME="iwatch Client"
IP_ADDRESS=$(hostname -i | awk '{print $1}')

# Generate the OpenSSL configuration file
echo "[req]" > openssl.cnf
echo "req_extensions = v3_req" >> openssl.cnf
echo "" >> openssl.cnf
echo "[v3_req]" >> openssl.cnf
echo "subjectAltName = @alt_names" >> openssl.cnf
echo "" >> openssl.cnf
echo "[alt_names]" >> openssl.cnf
echo "IP.1 = $IP_ADDRESS" >> openssl.cnf
