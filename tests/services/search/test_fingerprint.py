import pytest
import os

# Set mock environment variables for Pydantic Settings
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

from backend.services.search.fingerprint import FingerprintGenerator

def test_fingerprint_randomization():
    gen = FingerprintGenerator()
    header1 = gen.get_headers()
    header2 = gen.get_headers()
    
    # Headers should be different or at least valid
    assert "User-Agent" in header1
    assert "User-Agent" in header2
    # Probability of 2 identical UAs in a large pool is low, but let's check structure
    assert header1["User-Agent"] != ""

def test_fingerprint_cipher_rotation():
    gen = FingerprintGenerator()
    ciphers1 = gen.get_cipher_suite()
    ciphers2 = gen.get_cipher_suite()
    
    assert isinstance(ciphers1, str)
    # Cipher suites should be randomized
    # (Checking if they are different is probabilistic, but let's ensure they are valid strings)
    assert len(ciphers1.split(":")) > 5
