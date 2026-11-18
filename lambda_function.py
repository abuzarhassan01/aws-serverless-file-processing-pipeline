import json
import csv
import io
import urllib.parse
import boto3
from datetime import datetime

print('Loading function with multi-format support')

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # 1. Extract bucket name and object key dynamically from the S3 event trigger
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    # Safety check: Ensure file is in the input/ folder to avoid infinite loops
    if not key.startswith('input/'):
        print(f"Skipping file {key}: Not in the input/ folder.")
        return {'status': 'skipped', 'key': key}

    print(f"Processing file: {key} from bucket: {bucket}")

    try:
        # 2. Fetch file content from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        file_name = key.split('/')[-1]

        processed_data = {}

        # 3. Handle JSON files
        if key.endswith('.json'):
            data = json.loads(file_content)
            
            # Clean and normalize fields
            if 'user_id' in data:
                data['user_id'] = str(data['user_id']).strip()
            if 'email' in data:
                data['email'] = str(data['email']).strip().lower()
            if 'action' in data:
                data['action'] = str(data['action']).strip().lower()

            data['status'] = 'VALIDATED_AND_PROCESSED'
            data['processed_at'] = datetime.utcnow().isoformat() + 'Z'
            processed_data = data
            output_key = f"processed/processed_{file_name.replace('.json', '.json')}"

        # 4. Handle CSV files
        elif key.endswith('.csv'):
            f = io.StringIO(file_content)
            reader = csv.DictReader(f)
            rows = []
            
            for row in reader:
                cleaned_row = {}
                for col_name, val in row.items():
                    if col_name and val:
                        clean_col = col_name.strip().lower()
                        clean_val = val.strip()
                        if clean_col in ['email', 'action', 'status']:
                            clean_val = clean_val.lower()
                        cleaned_row[clean_col] = clean_val
                
                cleaned_row['row_status'] = 'VALIDATED'
                rows.append(cleaned_row)

            processed_data = {
                "source_file": file_name,
                "total_rows_processed": len(rows),
                "records": rows,
                "status": "VALIDATED_AND_PROCESSED",
                "processed_at": datetime.utcnow().isoformat() + 'Z'
            }
            output_key = f"processed/processed_{file_name.replace('.csv', '.json')}"

        else:
            print(f"Unsupported file format for key: {key}")
            return {'status': 'unsupported_format', 'key': key}

        # 5. Save the normalized output back to S3 in the processed/ folder
        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(processed_data, indent=2),
            ContentType='application/json'
        )

        print(f"Successfully processed {key} and saved to {output_key}")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully processed {key} -> {output_key}")
        }

    except Exception as e:
        print(f"ERROR processing file {key}: {str(e)}")
        raise e