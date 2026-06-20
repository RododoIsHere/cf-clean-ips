import time
import json
import requests
from datetime import datetime

def main():
    result, has_error = collect()

    if has_error:
        print("Warning: An error occurred during data collection. Aborting save to protect existing data.")
        return

    if not result.get("ipv4"):
        print("Warning: No IPs collected (network error or empty response). Aborting save to protect existing data.")
        return

    try:
        with open('cf2dns_list.json', 'r') as f:
            old_data = json.load(f)
            old_ipv4 = old_data.get("ipv4", [])
    except (FileNotFoundError, json.JSONDecodeError):
        old_ipv4 = []

    old_data_set = {el["ip"] for el in old_ipv4}
    new_data_set = {el["ip"] for el in result["ipv4"]}

    if old_data_set == new_data_set:
        print("No new IPs found. Skipping save to keep history clean.")
        return

    with open('cf2dns_list.json', 'w') as json_file:
        json_file.write(json.dumps(result, indent=4))

    with open('cf2dns_list.txt', 'w') as text_file:
        text_file.write(f"Last Update: {result['last_update']}\n\nIPv4:\n")
        for el in result["ipv4"]:
            text_file.write(f" - {el['ip']:15s}  {el['operator']:5s}  {el['provider']}  {el['created_at']}\n")
            
    print("Successfully fetched and saved new data.")

def collect():
    result = {
        "last_update": "",
        "last_timestamp": 0,
        "ipv4": []
    }
    
    has_error = False

    try:
        with open('cf2dns_list.json', 'r') as f:
            existing_ips = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_ips = {"ipv4": []}

    last_update = 0

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    data = {"key": "o1zrmHAF", "type": "v4"}
    
    try:
        response = requests.post("https://api.hostmonit.com/get_optimization_ip", headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            resp_json = response.json()
            
            if resp_json.get("code") == 200:
                info = resp_json.get("info", {})
                
                for operator_key, ip_list in info.items():
                    for item in ip_list:
                        ip = item.get("ip")
                        
                        prev = next((el for el in existing_ips.get("ipv4", []) if el["ip"] == ip), None)
                        created_at = prev["created_at"] if prev else int(time.time())
                        last_update = created_at if created_at > last_update else last_update
                        
                        result["ipv4"].append({
                            "ip": ip,
                            "operator": "CFY",
                            "provider": "hostmonit.com",
                            "created_at": created_at
                        })
            else:
                print(f"API Error: Returned non-200 success code inside JSON: {resp_json.get('code')}")
                has_error = True
        else:
            print(f"HTTP Error: Received status code {response.status_code}")
            has_error = True
            
    except Exception as e:
        print(f"Error fetching IPv4: {e}")
        has_error = True

    if not has_error and result["ipv4"]:
        if last_update == 0:
            last_update = int(time.time())

        result["last_update"] = datetime.fromtimestamp(last_update).__str__()
        result["last_timestamp"] = last_update

        result["ipv4"].sort(key=lambda el: el["created_at"], reverse=True)
        result["ipv4"].sort(key=lambda el: el["operator"])

    return result, has_error

if __name__ == '__main__':
    main()
