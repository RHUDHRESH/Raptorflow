import os
from dotenv import load_dotenv
import base64
import json
import time
from supabase import create_client

load_dotenv()

# Use service role key to check project settings
url = os.getenv('SUPABASE_URL')
service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, service_key)

print('Getting project information...')

try:
    # The anon key should be available in the project settings
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    print(f'Current anon key: {anon_key[:20]}...{anon_key[-10:] if anon_key else "NONE"}')
    
    # The anon key should start with 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    if anon_key and anon_key.startswith('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'):
        print('Anon key format looks correct')
        
        try:
            # Decode the JWT payload
            parts = anon_key.split('.')
            if len(parts) >= 2:
                payload = json.loads(base64.b64decode(parts[1] + '=='))
                print('JWT payload:', payload)
                
                # Check if it's expired
                if 'exp' in payload and payload['exp'] < time.time():
                    print('❌ Anon key is EXPIRED!')
                    print(f'Expired at: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(payload["exp"]))}')
                    print(f'Current time: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}')
                else:
                    print('✅ Anon key should be valid')
                    if 'exp' in payload:
                        print(f'Expires at: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(payload["exp"]))}')
        except Exception as e:
            print(f'Error decoding JWT: {e}')
    else:
        print('❌ Anon key format is invalid')
        
except Exception as e:
    print(f'Error: {e}')
