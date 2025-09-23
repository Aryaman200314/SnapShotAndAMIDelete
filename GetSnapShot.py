import boto3
import csv

def list_snapshots(output_csv, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    snapshots = []
    paginator = ec2.get_paginator("describe_snapshots")
    
    # List only snapshots owned by you
    for page in paginator.paginate(OwnerIds=["self"]):
        for snapshot in page["Snapshots"]:
            snapshots.append({"SnapshotId": snapshot["SnapshotId"]})

    # Write to CSV
    with open(output_csv, "w", newline="") as outfile:
        fieldnames = ["SnapshotId"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(snapshots)

    print(f"Found {len(snapshots)} snapshots. Results written to {output_csv}")


if __name__ == "__main__":
    # Example usage
    list_snapshots("all_snapshots.csv", region="us-east-1")
