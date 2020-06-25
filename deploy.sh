sam build && 
sam package --output-template-file packaged.yaml --s3-bucket kiel-api-bucket-2 &&
sam deploy --template-file packaged.yaml --capabilities CAPABILITY_IAM --stack-name kiel-frab-api