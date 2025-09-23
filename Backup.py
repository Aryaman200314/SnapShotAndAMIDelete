import boto3
import csv
from botocore.exceptions import ClientError

def delete_snapshots(input_csv, output_csv, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)
    results = []

    with open(input_csv, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Handle both "snapshotID" and "SnapshotId"
            snapshot_id = row.get("snapshotID") or row.get("SnapshotId")
            if not snapshot_id:
                print("⚠️ Skipping row, no snapshot ID found:", row)
                continue

            try:
                # Try deleting the snapshot
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot {snapshot_id}")
                results.append({"SnapshotId": snapshot_id, "Status": "Deleted"})

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                print(f"Could not delete {snapshot_id}: {error_code}")
                # Treat all failures as AWS Backup managed per your request
                results.append({"SnapshotId": snapshot_id, "Status": "Not able to delete - AWS Backup Managed"})

    # Write results CSV
    with open(output_csv, "w", newline="") as outfile:
        fieldnames = ["SnapshotId", "Status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nProcess complete. {len(results)} snapshots processed. Results written to {output_csv}")


if __name__ == "__main__":
    delete_snapshots("all_snapshots.csv", "snapshot_deletion_results.csv", region="us-east-1")
