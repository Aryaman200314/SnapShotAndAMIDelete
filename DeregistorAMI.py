import boto3
import csv
from botocore.exceptions import ClientError

def deregister_amis(input_csv, output_csv, region="us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)
    results = []

    with open(input_csv, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Handle both ImageId or imageId
            image_id = row.get("ImageId") or row.get("imageId")
            if not image_id:
                print("⚠️ Skipping row, no ImageId found:", row)
                continue

            try:
                ec2.deregister_image(ImageId=image_id)
                print(f"Deregistered AMI {image_id}")
                results.append({"ImageId": image_id, "Status": "Deregistered"})

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                print(f" Could not deregister {image_id}: {error_code}")
                results.append({"ImageId": image_id, "Status": "Not able to deregister"})

    # Write results CSV
    with open(output_csv, "w", newline="") as outfile:
        fieldnames = ["ImageId", "Status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n📄 Process complete. {len(results)} AMIs processed. Results written to {output_csv}")


if __name__ == "__main__":
    deregister_amis("all_amis.csv", "ami_deregistration_results.csv", region="us-east-1")
