import json
import pytest
from get_spotify_api_data import lambda_function

# 1️⃣ Test: il file si importa correttamente e le funzioni esistono
def test_functions_exist():
    assert callable(lambda_function.get_spotify_token)
    assert callable(lambda_function.get_recent_tracks)
    assert callable(lambda_function.save_to_s3)
    assert callable(lambda_function.lambda_handler)


# 2️⃣ Test: get_spotify_token() ritorna qualcosa (anche se fallisce)
def test_get_spotify_token_returns():
    result = lambda_function.get_spotify_token()
    assert result is not None


# 3️⃣ Test: get_recent_tracks() solleva eccezione se token errato
def test_get_recent_tracks_invalid_token():
    with pytest.raises(Exception):
        lambda_function.get_recent_tracks("invalid_token")


# 4️⃣ Test: save_to_s3() solleva eccezione se manca il bucket
def test_save_to_s3_missing_bucket(monkeypatch):
    # Disattiva il nome bucket
    monkeypatch.setattr(lambda_function, "RAW_S3_BUCKET_NAME", "")
    with pytest.raises(Exception):
        lambda_function.save_to_s3({"foo": "bar"}, "2025-10-27")


# 5️⃣ Test: lambda_handler() ritorna un dict con statusCode
def test_lambda_handler_output():
    result = lambda_function.lambda_handler({}, {})
    assert isinstance(result, dict)
    assert "statusCode" in result
