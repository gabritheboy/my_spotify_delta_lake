"""
AWS Lambda function to fetch Spotify recently played tracks and store them in S3.

This function:
1. Gets a Spotify access token using refresh token
2. Fetches recently played tracks from Spotify API
3. Stores the data in S3 with date-based partitioning

Environment Variables Required:
- SPOTIFY_CLIENT_ID: Spotify app client ID
- SPOTIFY_CLIENT_SECRET: Spotify app client secret  
- SPOTIFY_REFRESH_TOKEN: Spotify user refresh token
- RAW_S3_BUCKET_NAME: S3 bucket name for storing raw data
- AWS_REGION: AWS region (defaults to eu-north-1)
"""

import requests
import base64
import os
import json
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')
RAW_S3_BUCKET_NAME = os.getenv('RAW_S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION', 'eu-north-1')
TRACKS_LIMIT = 50  # Production limit

def get_spotify_token():
    """
    Get access token from Spotify using refresh token.
    
    Returns:
        str: Access token if successful
        dict: Error response if failed
    """
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    try:
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {b64_auth}"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": SPOTIFY_REFRESH_TOKEN
            },
            timeout=10
        )

        if resp.status_code == 200:
            auth_data = resp.json()
            print("Token Generated")
            return auth_data['access_token']
        else:
            print({'statusCode': resp.status_code, 'body': resp.text})
            return {'statusCode': resp.status_code, 'body': resp.text}
            
    except requests.RequestException as e:
        return {'statusCode': 500, 'body': f'Request failed: {str(e)}'}
    

def get_recent_tracks(access_token):
    """
    Fetch recently played tracks from Spotify API.
    
    Args:
        access_token (str): Spotify access token
        
    Returns:
        dict: Spotify API response with recent tracks
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            "https://api.spotify.com/v1/me/player/recently-played",
            headers=headers,
            params={"limit": TRACKS_LIMIT},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch recent tracks: {str(e)}")


def save_to_s3(data, today_date):
    """
    Save data to S3 with date-based partitioning.
    
    Args:
        data (dict): Data to save
        today_date (str): Date string in YYYY-MM-DD format
        
    Returns:
        dict: Response with status code and message
    """
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        key = f'{today_date}/{today_date}_recent_tracks.json'
        
        s3.put_object(
            Bucket=RAW_S3_BUCKET_NAME, 
            Key=key, 
            Body=json.dumps(data, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200, 
            'body': f'Data saved to s3://{RAW_S3_BUCKET_NAME}/{key}'
        }
        
    except Exception as e:
        raise Exception(f"Failed to save to S3: {str(e)}")


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        dict: Response with status code and body
    """
    try:
        # Get current date for partitioning
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get Spotify access token
        access_token = get_spotify_token()
        if isinstance(access_token, dict):  # Error response
            return access_token
            
        # Fetch recent tracks
        recent_tracks = get_recent_tracks(access_token)
        
        # Save to S3
        result = save_to_s3(recent_tracks, today_date)
        
        # Add metadata to response
        result['metadata'] = {
            'date': today_date,
            'tracks_count': len(recent_tracks.get('items', [])),
            'bucket': RAW_S3_BUCKET_NAME
        }
        print(result)
        return result

    except Exception as e:
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': str(e)})
        }


