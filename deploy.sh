#!/bin/bash

sam build
sam package --output-template-file packaged.yaml --s3-bucket "frab-api-artifact" --template "template-with-bastion.yaml"
sam deploy --template-file packaged.yaml --capabilities CAPABILITY_IAM --stack-name "frab-api"
    