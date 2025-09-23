import boto3
import csv

def list_amis(output_csv, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)

    amis = []
    paginator = ec2.get_paginator("describe_images")

    # Only list AMIs owned by you
    for page in paginator.paginate(Owners=["self"]):
        for image in page["Images"]:
            amis.append({"ImageId": image["ImageId"]})

    # Write to CSV
    with open(output_csv, "w", newline="") as outfile:
        fieldnames = ["ImageId"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(amis)

    print(f"Found {len(amis)} AMIs. Results written to {output_csv}")


if __name__ == "__main__":
    list_amis("all_amis.csv", region="us-east-1")
