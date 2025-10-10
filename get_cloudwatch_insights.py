import boto3
import time
import pandas as pd
from datetime import datetime, timedelta, timezone

LOG_GROUP = '/aws/eks/apsoutheast01/cluster' 
QUERY = 'fields @timestamp, @message, @logStream | sort @timestamp asc'  
REGION = 'us-east-1'
OUTPUT_FILE = 'cloudwatch_logs_fixed.xlsx'

# last 6 hours 
HOURS = 1
CHUNK_MINUTES = 30  


client = boto3.client('logs', region_name=REGION)

# end_time = int(time.time())
# start_time = end_time - (HOURS * 3600)
start_time = int(datetime(2025, 10, 10, 6, 48, 12, 709000, tzinfo=timezone.utc).timestamp())
end_time = int(datetime(2025, 10, 10, 7, 1, 3, 39000, tzinfo=timezone.utc).timestamp())

results_all = []


def run_query(start, end):
    response = client.start_query(
        logGroupName=LOG_GROUP,
        startTime=start,
        endTime=end,
        queryString=QUERY,
        limit=10000
    )
    query_id = response['queryId']

    while True:
        res = client.get_query_results(queryId=query_id)
        if res['status'] in ['Complete', 'Failed', 'Cancelled']:
            return res
        time.sleep(2)

print("Fetching logs in time chunks...")

chunk_seconds = CHUNK_MINUTES * 60
t = start_time

while t < end_time:
    start = t
    end = min(t + chunk_seconds - 1, end_time)  
    print(f"⏱️ Querying {datetime.utcfromtimestamp(start)} → {datetime.utcfromtimestamp(end)}")

    response = run_query(start, end)

    if response['status'] == 'Complete':
        for r in response['results']:
            row = {f['field']: f['value'] for f in r}
            results_all.append(row)
    else:
        print(f"⚠️ Query failed for {datetime.utcfromtimestamp(start)} → {datetime.utcfromtimestamp(end)}")

    t = end + 1

print(f"\n✅ Total raw records fetched: {len(results_all)}")

if results_all:
    df = pd.DataFrame(results_all)

    if '@timestamp' in df.columns and '@message' in df.columns:
        df.drop_duplicates(subset=['@timestamp', '@message'], inplace=True)
    else:
        df.drop_duplicates(inplace=True)

    print(f"✅ After removing duplicates: {len(df)} unique records")


    if '@timestamp' in df.columns:
        df.sort_values(by='@timestamp', inplace=True)


    df.to_excel(OUTPUT_FILE, index=False)
    print(f"💾 All unique logs saved to {OUTPUT_FILE}")
else:
    print("⚠️ No records found.")
