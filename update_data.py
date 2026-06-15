import csv
import json
import urllib.request
from datetime import datetime

url = "https://data.gov.hk/tc-data/dataset/hk-immd-set5-statistics-daily-passenger-traffic/resource/b341ea9a-7a34-4e33-95f7-5b297845ef43/download/transport_immigration_clearance_entry_exit.csv"
urllib.request.urlretrieve(url, '/tmp/data.csv')

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_count = 0
existing_keys = set(data.keys())
with open('/tmp/data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date_str = row['日期']
        try:
            dt = datetime.strptime(date_str, '%d-%m-%Y')
            key = dt.strftime('%Y-%m-%d')
            if key in existing_keys:
                continue
            direction = row['入境 / 出境']
            hk = int(row['香港居民'] or 0)
            mainland = int(row['內地訪客'] or 0)
            other = int(row['其他訪客'] or 0)
            total = int(row['總計'] or 0)
            if key not in data:
                data[key] = {'inbound': {'hk':0,'mainland':0,'other':0,'total':0}, 'outbound': {'hk':0,'mainland':0,'other':0,'total':0}}
            if direction == '入境':
                data[key]['inbound']['hk'] += hk
                data[key]['inbound']['mainland'] += mainland
                data[key]['inbound']['other'] += other
                data[key]['inbound']['total'] += total
            else:
                data[key]['outbound']['hk'] += hk
                data[key]['outbound']['mainland'] += mainland
                data[key]['outbound']['other'] += other
                data[key]['outbound']['total'] += total
            new_count += 1
        except:
            continue

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print(f"Updated {new_count} records")
