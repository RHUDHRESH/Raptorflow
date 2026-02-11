import os
from upstash_redis import Redis

def verify_upstash():
    url = os.getenv("UPSTASH_REDIS_URL")
    token = os.getenv("UPSTASH_REDIS_TOKEN")
    print(f"Connecting to Upstash Redis at {url}...")
    try:
        redis = Redis(url=url, token=token)
        response = redis.ping()
        if response:
            print("✅ Upstash Redis connection successful!")
        else:
            print("❌ Upstash Redis ping failed.")
    except Exception as e:
        print(f"❌ Upstash Redis connection failed: {e}")

if __name__ == "__main__":
    # Load env manually since we are in a sub-script
    def load_env(env_path):
        if not os.path.exists(env_path):
            return
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    load_env('.env')
    verify_upstash()
