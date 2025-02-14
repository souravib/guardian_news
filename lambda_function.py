import json
import requests
import boto3
from datetime import datetime, timedelta

# S3 Configuration
s3_client = boto3.client("s3")
s3_bucket_name = "guardianews"  # Replace with your bucket name
s3_key = "guardian-news.json"  # File name in S3

# Amazon Comprehend client
comprehend_client = boto3.client("comprehend", region_name="us-east-1")

def analyze_sentiment_with_comprehend(text):
    """
    Analyzes the sentiment of a given text using Amazon Comprehend.

    Parameters:
        text (str): The text to analyze.

    Returns:
        dict: Sentiment classification and scores.
    """
    try:
        response = comprehend_client.detect_sentiment(
            Text=text,
            LanguageCode='en'  # Assuming English text
        )
        return {
            "sentiment": response["Sentiment"],
            "sentiment_scores": response["SentimentScore"]
        }
    except Exception as e:
        print(f"Error analyzing sentiment with Comprehend: {e}")
        return {
            "sentiment": "ERROR",
            "sentiment_scores": {}
        }

def fetch_guardian_news(api_key, query="latest", page_size=5, from_date=None):
    """
    Fetches news articles from The Guardian API for a specific date.

    Parameters:
        api_key (str): The API key for The Guardian.
        query (str): The search query for articles.
        page_size (int): Number of articles to fetch.
        from_date (str): The start date for fetching news (YYYY-MM-DD).

    Returns:
        list: A list of articles with headline, summary, URL, and sentiment.
    """
    url = "https://content.guardianapis.com/search"
    params = {
        "api-key": api_key,
        "q": query,
        "page-size": page_size,
        "show-fields": "trailText",
        "from-date": from_date,
        "to-date": from_date,  # Fetch only for a single day
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["response"]["status"] == "ok":
            articles = []
            for result in data["response"]["results"]:
                summary = result["fields"].get("trailText", "No summary available")
                
                # Perform sentiment analysis using Amazon Comprehend
                sentiment_data = analyze_sentiment_with_comprehend(summary)
                
                article = {
                    "headline": result["webTitle"],
                    "summary": summary,
                    "url": result["webUrl"],
                    "sentiment": sentiment_data["sentiment"],
                    "sentiment_scores": sentiment_data["sentiment_scores"],
                    "publication_date": result["webPublicationDate"]
                }
                articles.append(article)
            return articles
        else:
            return {"error": "API response error", "message": data["response"].get("message", "Unknown error")}
    except requests.exceptions.RequestException as e:
        return {"error": "RequestException", "message": str(e)}

def write_to_s3(articles):
    """
    Writes articles to S3 in a Glue crawler-compatible JSON format.

    Parameters:
        articles (list): A list of articles to write to S3.
    """
    try:
        # Convert articles to Glue-compatible JSON (array of objects)
        json_lines = "\n".join([json.dumps(article) for article in articles])
        
        # Upload to S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
            Body=json_lines,
            ContentType="application/json"
        )
        print(f"Data written to S3: s3://{s3_bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error writing to S3: {e}")
        raise

def lambda_handler(event, context):
    """
    Lambda handler to fetch articles and store them in S3.

    Parameters:
        event (dict): Input event with API key, query, and page size.
        context (LambdaContext): Lambda context object.

    Returns:
        dict: Response indicating success or failure.
    """
    # Extract parameters from the event
    api_key = event.get("api_key")
    query = event.get("query", "latest")
    page_size = event.get("page_size", 5)

    if not api_key:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "API key is required"})
        }

    # Initialize an empty list to store articles
    all_articles = []

    # Get today's date and calculate the past 5 days
    today = datetime.utcnow()
    for i in range(5):
        target_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"Fetching news for date: {target_date}")
        
        # Fetch articles for the target date
        articles = fetch_guardian_news(api_key, query, page_size, from_date=target_date)
        
        if isinstance(articles, list):
            all_articles.extend(articles)  # Add to the overall list
        else:
            print(f"Error fetching articles for {target_date}: {articles}")

    if all_articles:
        # Write all articles to S3
        write_to_s3(all_articles)
        return {
            "statusCode": 200,
            "body": f"Data written to S3: s3://{s3_bucket_name}/{s3_key}"
        }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "No articles fetched"})
        }

