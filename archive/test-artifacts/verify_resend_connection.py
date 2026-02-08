import os
import requests

api_key = "re_De99YTsk_6K4bRLYqUyuDVGSNXs287gdF"

def verify_resend():
    print(f"Connecting to Resend...")
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    # We can't really "ping" without sending an email or listing something.
    # Let's try to list domains if possible, or just a dummy request to check auth.
    try:
        response = requests.get("https://api.resend.com/domains", headers=headers)
        if response.status_code == 200:
            print("✅ Resend connection successful!")
            print(f"Domains: {response.json()}")
        else:
            print(f"❌ Resend connection failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Resend connection failed: {e}")

if __name__ == "__main__":
    verify_resend()
