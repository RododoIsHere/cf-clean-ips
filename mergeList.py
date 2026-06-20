import json
import time
import glob
from datetime import datetime

def main():
    merged_ipv4 = []
    last_update_ts = 0

    list_files = glob.glob('*_list.json')

    def add_ips(ip_list):
        nonlocal last_update_ts
        for item in ip_list:
            merged_ipv4.append(item)
            
            created_at = item.get("created_at", 0)
            if created_at > last_update_ts:
                last_update_ts = created_at

    for filename in list_files:
        data = load_json(filename)
        add_ips(data.get("ipv4", []))

    if last_update_ts == 0:
        last_update_ts = int(time.time())

    merged_ipv4.sort(key=lambda el: el.get("created_at", 0), reverse=True)
    merged_ipv4.sort(key=lambda el: el.get("operator", ""))

    result = {
        "last_update": datetime.fromtimestamp(last_update_ts).__str__(),
        "last_timestamp": last_update_ts,
        "ipv4": merged_ipv4,
        "ipv6": []
    }

    with open('list.json', 'w') as json_file:
        json_file.write(json.dumps(result, indent=4))

    with open('list.txt', 'w') as text_file:
        text_file.write(f"Last Update: {result['last_update']}\n\nIPv4:\n")
        for el in result["ipv4"]:
            text_file.write(f"  - {el['ip']:15s}    {el['operator']:5s}    {el['provider']}    {el['created_at']}\n")

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"ipv4": []}

if __name__ == '__main__':
    main()
