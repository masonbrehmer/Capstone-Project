# Agent Guidance For This Repository

This repository is an AWS capstone project for building a sports card investment analytics website.

## Project Context

The goal is to build a student-friendly, understandable, and cost-aware serverless web application for analyzing sports card investment data.

## Working Rules

1. Explain what each AWS service does before using it in architecture, code, infrastructure, or deployment steps.
2. Keep the system architecture simple, practical, and serverless by default.
3. Warn about cost risks before recommending or adding any AWS resource that could materially affect the budget.
4. Treat the AWS account as budget-constrained with a hard limit of `$200`, and optimize for low-cost services and low operational complexity.
5. Avoid expensive or unnecessary services unless the user explicitly approves them. This especially includes:
   - Large EC2 instances
   - GPU instances
   - NAT Gateway
   - OpenSearch
6. Prefer managed serverless AWS services when they fit the requirement, especially:
   - S3
   - Lambda
   - DynamoDB
   - API Gateway
   - CloudWatch
   - SNS
7. Test each step before moving to the next one. Do not stack multiple unverified infrastructure or application changes when a smaller validated step is possible.
8. Explain the purpose of each file, template, script, and command that is added or used so the student can understand how the system works.

## Architecture Expectations

- Favor simple request flows such as `frontend -> API Gateway -> Lambda -> DynamoDB/S3`.
- Prefer static frontend hosting and lightweight APIs over always-on servers.
- Minimize operational overhead, background services, and hidden networking costs.
- Choose services that fit a capstone scope and can be explained clearly.

## Communication Expectations

- When proposing architecture, include a short explanation of why each service is used.
- When running commands, explain what the command does and what result to expect.
- When creating files, explain why the file exists and how it fits into the project.
- When there is a cheaper alternative, mention it.

## Cost Guardrails

- Call out recurring-cost services before implementation.
- Avoid designs that require idle infrastructure running 24/7.
- Prefer pay-per-request and free-tier-friendly options when possible.
- If a requested change could exceed the project budget, stop and warn clearly before proceeding.
