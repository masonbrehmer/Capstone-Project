# Architecture

## System Summary

This project is a serverless sports card analytics application built on AWS. The goal is to keep the system understandable, low-maintenance, and cost-aware while still supporting a realistic full-stack workflow: static frontend, API backend, NoSQL storage, and AI-generated recommendations.

## AWS Services Used

- `Amazon S3`
  Hosts the static frontend files and serves the website to users.
- `Amazon API Gateway`
  Receives browser requests and routes them to Lambda.
- `AWS Lambda`
  Executes backend logic for listing cards, fetching a specific card, and generating AI recommendations.
- `Amazon DynamoDB`
  Stores normalized sports card records keyed by `cardId`.
- `Amazon Bedrock`
  Generates short investment insights for a player using a managed foundation model.
- `AWS CloudFormation`
  Defines the infrastructure in code so the environment can be recreated consistently.

## Request Flow

```text
user -> API Gateway -> Lambda -> DynamoDB / Bedrock -> response
```

## Detailed Flow

1. A user loads the static frontend from S3.
2. The frontend sends an HTTP request to API Gateway.
3. API Gateway invokes the Lambda function.
4. Lambda does one of the following:
   - reads card data from DynamoDB
   - requests an AI recommendation from Bedrock
5. Lambda formats the response as JSON and returns it through API Gateway.
6. The frontend displays the results as cards, dashboard metrics, or recommendation text.

## Data Flow

- Raw CSV exports are stored in `data/`.
- Python scripts normalize those files into a canonical schema.
- The normalized dataset is transformed into DynamoDB batch write payloads.
- DynamoDB becomes the serving layer for the live API.

## Why This Design Works

- It stays fully serverless, so there are no always-on servers to manage.
- It is simple enough for a capstone project but still demonstrates real AWS architecture patterns.
- Each service has a focused role, which makes the system easier to explain, extend, and debug.
