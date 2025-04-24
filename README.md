# Guardian News API Data Pipeline

This repository contains code and instructions for setting up a data pipeline that:
1. Pulls data from the Guardian News API using an AWS Lambda function.
2. Processes and stores the data in Amazon S3 and catalogs it using AWS Glue for querying in Amazon Athena.
3. Loads the processed data into Amazon RDS for visualization in Power BI.

## Architecture Overview

1. **Guardian News API**: Source of news articles and data.
2. **AWS Lambda**: Serverless function to fetch and process data from the Guardian API.
3. **Amazon S3**: Storage for raw and processed data.
4. **AWS Glue**: Catalogs data stored in S3 for querying with Amazon Athena.
5. **Amazon Athena**: Used to query and analyze data directly from S3.
6. **Amazon RDS**: Relational database to store aggregated data for Power BI visualization.

## Prerequisites

Before you begin, ensure you have the following:
- An AWS account.
- Access to the Guardian News API. Sign up and get an API key [here](https://open-platform.theguardian.com/access/).
- AWS CLI installed and configured.
- Python 3.x installed on your local machine.

## Setup Instructions

### 1. Configure the Guardian News API
1. Visit the Guardian News API portal.
2. Register for an API key.
3. Note your API key for use in the Lambda function.

### 2. Create an AWS Lambda Function

#### Steps:
1. Navigate to the AWS Lambda console.
2. Create a new Lambda function.
3. Use the provided Python script (`lambda_function.py`) to fetch and process data from the Guardian News API.
4. Add the necessary environment variables:
   - `GUARDIAN_API_KEY`: Your Guardian API key.
   - `S3_BUCKET_NAME`: The name of your S3 bucket.
   - `S3_RAW_FOLDER`: Folder path for raw data.
   - `S3_PROCESSED_FOLDER`: Folder path for processed data.
5. Attach necessary permissions to the Lambda execution role:
   - S3 write access.
   - Glue and Athena access if required.

### 3. Configure AWS Glue
1. Create a Glue Crawler to scan the S3 bucket.
   - Set the data source to the S3 folder where raw data is stored.
   - Create or use an existing database in Glue.
2. Run the Glue Crawler to populate the Glue Data Catalog.

### 4. Query Data in Athena
1. Open the Athena console.
2. Select the Glue database and table created by the crawler.
3. Run SQL queries to analyze and transform the data.
4. Save the query results to a new S3 folder.


### 5. Visualize Data in Power BI
1. Connect Power BI to your RDS instance:
   - Use the "PostgreSQL" or "MySQL" connector.
   - Enter your RDS endpoint, username, and password.
2. Import tables and create dashboards.





