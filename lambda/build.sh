#! /bin/bash

mkdir reqs
pip install -r requirements.txt -t reqs/ 

mkdir -p build
zip -r build/lambda_function.zip lambda_function.py

cd reqs
zip -r ../build/lambda_function.zip ./*
cd ..

rm -rf reqs
