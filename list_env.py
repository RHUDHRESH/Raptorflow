import os

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
load_env('backend/.env')

for key, value in os.environ.items():
    if key.startswith("REDIS") or key.startswith("UPSTASH"):
        print(f"{key}: {value}")
