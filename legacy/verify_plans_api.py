import requests
import json
import sys

def verify_plans():
    url = "http://localhost:3000/api/plans"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            plans = data.get('plans', [])
            print(f"Found {len(plans)} plans:")
            for plan in plans:
                print(f" - {plan.get('name')} ({plan.get('id')}): {plan.get('price_monthly_paise')}")
                
            if len(plans) >= 3:
                print("SUCCESS: 3+ Plans found!")
                sys.exit(0)
            else:
                print("WARNING: Less than 3 plans found.")
                sys.exit(1)
        else:
            print(f"ERROR: API returned {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Failed to fetch API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_plans()
