# =============================================================================
# TESTING SECTION - Only runs when script is executed directly
# =============================================================================

from moto import mock_aws
import boto3

def test_with_mocked_s3():
    """
    Test the S3 functionality using moto to mock AWS services.
    This allows testing without real AWS credentials or resources.
    """
  
    
    @mock_aws
    def _test_s3_operations():
        """Internal function to test S3 operations within mock context"""
        # Sample Spotify API response data
        test_data = {
            "items": [
                {
                    "track": {
                        "id": "4iV5W9uYEdYUVa79Axb7Rh",
                        "name": "Never Gonna Give You Up",
                        "artists": [{"id": "4Z8W4fKeB5YxbusRsdQVPb", "name": "Rick Astley"}],
                        "album": {"name": "Whenever You Need Somebody", "release_date": "1987-07-27"},
                        "duration_ms": 213573
                    },
                    "played_at": "2024-01-15T14:30:00.000Z",
                    "context": None
                },
                {
                    "track": {
                        "id": "7qiZfU4dY1lWllzX7mPBI3",
                        "name": "Shape of You",
                        "artists": [{"id": "6eUKZXaKkcviH0Ku9w2n3V", "name": "Ed Sheeran"}],
                        "album": {"name": "÷ (Deluxe)", "release_date": "2017-03-03"},
                        "duration_ms": 233713
                    },
                    "played_at": "2024-01-15T14:25:00.000Z",
                    "context": None
                }
            ],
            "next": "https://api.spotify.com/v1/me/player/recently-played?before=1642255500000&limit=2",
            "cursors": {"after": "1642255500000", "before": "1642255500000"},
            "limit": 2,
            "href": "https://api.spotify.com/v1/me/player/recently-played?limit=2"
        }
        
        test_date = "2024-01-15"
        
        # Test S3 operations with mocked environment
        s3 = boto3.client('s3', region_name='us-east-1')  # Use default region for moto
        
        # Create bucket (required for moto)
        try:
            s3.create_bucket(Bucket=RAW_S3_BUCKET_NAME)
            print(f"✅ Created test bucket: {RAW_S3_BUCKET_NAME}")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"✅ Test bucket already exists: {RAW_S3_BUCKET_NAME}")
        
        # Test save operation
        result = save_to_s3(test_data, test_date)
        print(f"✅ Save operation successful: {result['body']}")
        
        # Verify data was stored
        response = s3.get_object(Bucket=RAW_S3_BUCKET_NAME, Key=f'{test_date}/recent_tracks.json')
        stored_data = json.loads(response['Body'].read().decode('utf-8'))
        
        print(f"✅ Verification successful: {len(stored_data['items'])} tracks stored")
        print(f"✅ First track: {stored_data['items'][0]['track']['name']} by {stored_data['items'][0]['track']['artists'][0]['name']}")
        
        return True
    
    return _test_s3_operations()


if __name__ == "__main__":
    print("🧪 Testing Spotify Lambda Function with Mocked AWS Environment")
    print("=" * 70)
    
    try:
        # Test with mocked S3
        test_with_mocked_s3()
        print("=" * 70)
        print("✅ All tests passed! Function is ready for AWS Lambda deployment.")
        print("\n📋 Next steps:")
        print("1. Set up environment variables in AWS Lambda")
        print("2. Deploy this function to AWS Lambda")
        print("3. Configure EventBridge/CloudWatch Events for scheduling")
        
    except ImportError:
        print("❌ Moto not installed. Install with: pip install moto")
        print("   This is required for testing AWS services locally.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("   Check your environment variables and dependencies.")