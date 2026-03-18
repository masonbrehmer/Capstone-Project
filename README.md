# Sports Card Analytics on AWS

A full-stack sports card analytics application built with a serverless AWS architecture. The project combines a static frontend, API-driven backend, DynamoDB card data, and Bedrock-powered AI insights to help users explore pricing trends, market movers, and player-specific investment signals.

## Live Demo

Frontend: `http://<your-s3-website-url>`

API Base URL: `https://<your-api-id>.execute-api.us-east-1.amazonaws.com`

## Overview

This project analyzes 30,000+ sports card records and exposes them through a lightweight AWS stack designed for a capstone-friendly scope. Users can browse cards, filter by player, sort by market metrics, and request AI-generated investment commentary for a specific player. The design stays simple: static frontend on S3, HTTP API on API Gateway, business logic in Lambda, data in DynamoDB, and AI inference through AWS Bedrock.

## Features

- Browse a large sports card dataset through a simple web interface
- Filter cards by player name
- Sort card data by price, price change, sales volume, and total sales
- View dashboard-style sections for top gainers, top losers, and highest-volume cards
- Retrieve individual card details by `cardId`
- Generate short AI investment insights using AWS Bedrock and the Nova Micro model
- Use a fully serverless architecture with low operational overhead

## Architecture

This project uses managed AWS services to keep the system simple and cost-aware:

- `Amazon S3`
  Stores and serves the static frontend website files (`index.html`, `script.js`, `styles.css`).
- `Amazon API Gateway`
  Exposes public HTTP endpoints for the frontend and routes requests to Lambda.
- `AWS Lambda`
  Runs the backend API logic for filtering, sorting, fetching card records, and generating AI recommendations.
- `Amazon DynamoDB`
  Stores the sports card dataset using `cardId` as the primary key.
- `Amazon Bedrock`
  Generates short player-specific investment commentary using the `amazon.nova-micro-v1:0` model.
- `AWS CloudFormation`
  Defines infrastructure as code so the stack can be recreated consistently.

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python on AWS Lambda
- API: Amazon API Gateway (HTTP API)
- Database: Amazon DynamoDB
- AI: Amazon Bedrock Nova Micro
- Infrastructure: AWS CloudFormation
- Data Processing: Python scripts for CSV normalization and DynamoDB batch export

## Project Structure

- `frontend/`
  Static website assets for the client UI.
- `cloudformation/`
  Infrastructure as code templates for AWS resources.
- `data/`
  CSV exports, normalized datasets, and DynamoDB batch payloads.
- `docs/`
  Supporting architecture and project documentation.
- `scripts/`
  Local utilities for combining exports and generating DynamoDB import files.
- `lambda/`
  Reserved for Lambda-related code and future extracted handlers.

## API Endpoints

### `GET /cards`

Returns a list of card records with optional filtering and sorting.

Supported query parameters:

- `limit`
- `player`
- `sort`
- `direction`

Example:

```http
GET /cards?limit=10&player=LeBron&sort=price_change_percent&direction=desc
```

Example response:

```json
{
  "count": 2,
  "items": [
    {
      "cardId": "730aca51-68ff-463d-8a90-a87ec1e69d97",
      "player": "LeBron James",
      "card_name": "LeBron James 2003 Topps Chrome #111 Refractor",
      "grade": "Raw",
      "date": "20260207",
      "price": 4,
      "price_change_percent": -99.91,
      "number_of_sales": 13
    }
  ]
}
```

### `GET /cards/{cardId}`

Returns one card by primary key.

Example:

```http
GET /cards/730aca51-68ff-463d-8a90-a87ec1e69d97
```

Example response:

```json
{
  "cardId": "730aca51-68ff-463d-8a90-a87ec1e69d97",
  "player": "LeBron James",
  "card_name": "LeBron James 2003 Topps Chrome #111 Refractor",
  "grade": "Raw",
  "date": "20260207",
  "price": 4,
  "average_price": 5811.64,
  "number_of_sales": 13,
  "last_sale_date": "02/03/2026"
}
```

### `GET /recommendations`

Returns a short AI-generated investment insight for a player.

Example:

```http
GET /recommendations?player=LeBron%20James
```

Example response:

```json
{
  "player": "LeBron James",
  "insight": "LeBron James cards still benefit from strong collector demand, especially for iconic rookie-era releases. Prices can be volatile, so focus on liquidity, historical sales consistency, and entry point discipline."
}
```

## How It Works

1. Raw CSV exports are stored in `data/`.
2. Python scripts normalize the exports into a canonical schema and generate DynamoDB batch import files.
3. DynamoDB stores the final card records with `cardId` as the primary key.
4. API Gateway receives frontend requests and sends them to Lambda.
5. Lambda scans or retrieves DynamoDB records, applies filtering and sorting, and returns JSON responses.
6. For AI recommendations, Lambda sends a prompt to Amazon Bedrock and returns the generated insight to the frontend.
7. S3 hosts the frontend and the browser calls the API directly.

## Setup Instructions

### Local Development

1. Clone the repository.
2. Add AWS credentials locally with access to S3, Lambda, API Gateway, DynamoDB, CloudFormation, and Bedrock.
3. Review the infrastructure template in `cloudformation/capstone-infrastructure.yaml`.
4. Use the scripts in `scripts/` to prepare or regenerate data files in `data/`.
5. Open the static frontend in `frontend/` or upload it to S3 for hosted testing.

### AWS Deployment

1. Deploy the CloudFormation template.
   CloudFormation is AWS’s infrastructure-as-code service that creates the API Gateway, Lambda, DynamoDB table, IAM roles, and related resources from one template.
2. Upload the frontend files to an S3 bucket configured for static website hosting.
   S3 is AWS object storage and can host static websites cheaply for low-traffic projects.
3. Load card data into DynamoDB using the generated batch files.
   DynamoDB is AWS’s managed NoSQL database used here for flexible, serverless card record storage.
4. Confirm the API routes are reachable from the frontend.
5. If using Bedrock recommendations, ensure the AWS account has model access for `amazon.nova-micro-v1:0`.
   Bedrock is AWS’s managed foundation model service. It is usage-based, so monitor cost before enabling it broadly.

## Future Improvements

- Add pagination support using `LastEvaluatedKey` tokens returned to the frontend
- Add precomputed analytics summaries instead of computing dashboard views from live scans
- Improve recommendation prompts with recent market context and card-level signals
- Add authentication for admin-only ingestion or moderation workflows
- Replace scan-heavy access patterns with query-friendly indexes where appropriate
- Add charts for player trends, liquidity, and volatility

## Resume Bullet

- Built a full-stack sports card analytics platform on AWS using S3, API Gateway, Lambda, DynamoDB, CloudFormation, and Bedrock, serving 30k+ records with filtering, sorting, dashboard analytics, and AI-generated investment insights.
