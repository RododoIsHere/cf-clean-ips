import time
import json
import requests
from datetime import datetime

def main():
    result = collect()

    with open('cf2dns_list.json', 'w') as json_file:
        json_file.write(json.dumps(result, indent=4))

    with open('cf2dns_list.txt', 'w') as text_file:
        text_file.write(f"Last Update: {result['last_update']}\n\nIPv4:\n")
        for el in result["ipv4"]:
            text_file.write(f" - {el['ip']:15s}  {el['operator']:5s}  {el['provider']}  {el['created_at']}\n")

def collect():
    result = {
        "last_update": "",
        "last_timestamp": 0,
        "ipv4": []
    }

    try:
        with open('cf2dns_list.json', 'r') as f:
            existing_ips = json.load(f)
    except FileNotFoundError:
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
    except Exception as e:
        print(f"Error fetching IPv4: {e}")

    if last_update == 0:
        last_update = int(time.time())

    result["last_update"] = datetime.fromtimestamp(last_update).__str__()
    result["last_timestamp"] = last_update

    result["ipv4"].sort(key=lambda el: el["created_at"], reverse=True)
    result["ipv4"].sort(key=lambda el: el["operator"])

    return result

if __name__ == '__main__':
    main()
