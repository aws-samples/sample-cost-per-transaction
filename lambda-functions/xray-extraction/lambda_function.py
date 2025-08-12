import json
import boto3
import os
import re
import hashlib
from datetime import datetime, timedelta

# Initialize X-Ray client using standard boto3
xray_client = boto3.client('xray')

def sanitize_trace_data(trace_data):
    """Sanitize trace data to remove sensitive information"""
    if isinstance(trace_data, dict):
        sanitized = {}
        for key, value in trace_data.items():
            # Remove or hash sensitive fields
            if key in ['email', 'phone', 'ssn', 'credit_card', 'password']:
                sanitized[key] = '[REDACTED]'
            elif key in ['user_id', 'customer_id', 'account_id']:
                sanitized[key] = hashlib.sha256(str(value).encode()).hexdigest()[:16]
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_trace_data(value)
            else:
                sanitized[key] = value
        return sanitized
    elif isinstance(trace_data, list):
        return [sanitize_trace_data(item) for item in trace_data]
    else:
        return trace_data

def lambda_handler(event, context):
    """
    Secure Lambda function to extract X-Ray trace data from the last 72 hours
    with proper input validation and data sanitization
    """
    try:
        # Input validation
        if not isinstance(event, dict):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid request format',
                    'success': False
                })
            }
        
        # Set overall time range (last 72 hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=72)
        
        print(f"Extracting X-Ray data from {start_time} to {end_time} (72 hours)")
        
        # Get and validate filter expression from event
        filter_expression = event.get('filterExpression', None)
        if filter_expression:
            # Sanitize filter expression to prevent injection
            filter_expression = re.sub(r'[<>"\';\\]', '', str(filter_expression)[:500])
        
        # Split the 72-hour period into three 24-hour chunks
        time_chunks = []
        chunk_start = start_time
        
        while chunk_start < end_time:
            chunk_end = min(chunk_start + timedelta(hours=24), end_time)
            time_chunks.append((chunk_start, chunk_end))
            chunk_start = chunk_end
        
        print(f"Split into {len(time_chunks)} time chunks for API compliance")
        
        # Process each time chunk and collect all trace summaries
        all_trace_summaries = []
        
        for i, (chunk_start, chunk_end) in enumerate(time_chunks):
            print(f"Processing chunk {i+1}/{len(time_chunks)}: {chunk_start} to {chunk_end}")
            
            # Initialize pagination for this chunk
            next_token = None
            chunk_summaries = []
            
            # Paginate through all trace summaries for this time chunk
            while True:
                # Prepare query parameters
                params = {
                    'StartTime': chunk_start,
                    'EndTime': chunk_end,
                    'TimeRangeType': 'TraceId'
                }
                
                # Add filter expression if provided
                if filter_expression:
                    params['FilterExpression'] = filter_expression
                    
                # Add next token if available
                if next_token:
                    params['NextToken'] = next_token
                    
                # Query X-Ray traces
                response = xray_client.get_trace_summaries(**params)
                
                # Add results to our collection
                chunk_summaries.extend(response['TraceSummaries'])
                
                # Check if there are more results
                if 'NextToken' in response:
                    next_token = response['NextToken']
                    print(f"Retrieved batch of {len(response['TraceSummaries'])} summaries, continuing pagination...")
                else:
                    break
            
            print(f"Found {len(chunk_summaries)} trace summaries in chunk {i+1}")
            all_trace_summaries.extend(chunk_summaries)
        
        total_summaries = len(all_trace_summaries)
        print(f"Total trace summaries across all time chunks: {total_summaries}")
        
        # Get detailed trace data in batches (X-Ray API limits to 5 traces per request)
        all_traces = []
        trace_ids = [summary['Id'] for summary in all_trace_summaries]
        
        # Process in batches of 5
        batch_size = 5
        total_batches = (len(trace_ids) + batch_size - 1) // batch_size  # Ceiling division
        
        print(f"Retrieving detailed trace data in {total_batches} batches")
        
        for i in range(0, len(trace_ids), batch_size):
            batch_ids = trace_ids[i:i+batch_size]
            if batch_ids:
                batch_num = (i // batch_size) + 1
                if batch_num % 20 == 0:  # Log every 20th batch to avoid excessive logging
                    print(f"Processing batch {batch_num}/{total_batches}")
                
                trace_result = xray_client.batch_get_traces(TraceIds=batch_ids)
                all_traces.extend(trace_result['Traces'])
                
                # Check for pagination within batch_get_traces
                while 'NextToken' in trace_result:
                    trace_result = xray_client.batch_get_traces(
                        TraceIds=batch_ids,
                        NextToken=trace_result['NextToken']
                    )
                    all_traces.extend(trace_result['Traces'])
        
        print(f"Retrieved {len(all_traces)} detailed traces")
        
        # Process and sanitize the trace data
        processed_data = []
        for trace in all_traces:
            trace_info = {
                'traceId': trace['Id'],
                'duration': trace['Duration'],
                'segments': []
            }
            
            for segment in trace['Segments']:
                doc = json.loads(segment['Document'])
                segment_info = {
                    'name': doc.get('name', ''),
                    'startTime': doc.get('start_time', 0),
                    'endTime': doc.get('end_time', 0),
                    'origin': doc.get('origin', ''),
                    'aws': sanitize_trace_data(doc.get('aws', {})),
                    'annotations': sanitize_trace_data(doc.get('annotations', {})),
                    'metadata': sanitize_trace_data(doc.get('metadata', {}))
                }
                
                # Extract and sanitize subsegments if available
                if 'subsegments' in doc:
                    segment_info['subsegments'] = sanitize_trace_data(doc['subsegments'])
                
                trace_info['segments'].append(segment_info)
            
            processed_data.append(trace_info)
        
        # Store data in S3 (recommended for 72 hours of data)
        if os.environ.get('S3_BUCKET'):
            s3_client = boto3.client('s3')
            bucket_name = os.environ['S3_BUCKET']
            timestamp = end_time.strftime('%Y-%m-%d-%H-%M-%S')
            
            # For large datasets, split into multiple files
            if len(processed_data) > 1000:
                result_files = []
                
                # Split into chunks of 1000 traces
                for chunk_index, i in enumerate(range(0, len(processed_data), 1000)):
                    chunk = processed_data[i:i+1000]
                    key = f"xray-data/72hr-{timestamp}-part{chunk_index+1}.json"
                    
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=key,
                        Body=json.dumps(chunk),
                        ContentType='application/json'
                    )
                    result_files.append(key)
                
                # Create a manifest file
                manifest_key = f"xray-data/72hr-{timestamp}-manifest.json"
                manifest = {
                    'totalTraces': len(processed_data),
                    'files': result_files,
                    'timeRange': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat()
                    }
                }
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=manifest_key,
                    Body=json.dumps(manifest),
                    ContentType='application/json'
                )
                
                result = {
                    'message': f'Successfully stored {len(processed_data)} X-Ray traces in S3 (split into {len(result_files)} files)',
                    'bucket': bucket_name,
                    'manifestKey': manifest_key,
                    'files': result_files
                }
            else:
                # Store as a single file if small enough
                key = f"xray-data/72hr-{timestamp}.json"
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=json.dumps(processed_data),
                    ContentType='application/json'
                )
                
                result = {
                    'message': f'Successfully stored {len(processed_data)} X-Ray traces in S3',
                    'bucket': bucket_name,
                    'key': key
                }
        else:
            # Return directly if dataset is small enough and no S3 bucket configured
            # Note: This may fail for large datasets due to Lambda response size limits
            result = {
                'message': 'Successfully retrieved X-Ray trace data',
                'traceCount': len(processed_data),
                'timeRange': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'traces': processed_data if len(processed_data) < 100 else 'Data too large to return directly. Configure S3_BUCKET environment variable.'
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            },
            'body': json.dumps(result, default=str)
        }
    
    except ValueError as e:
        # Handle validation errors
        print(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid input data',
                'success': False
            })
        }
    
    except Exception as e:
        # Log error for monitoring (without exposing details to client)
        print(f"Internal error extracting X-Ray data: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'success': False
            })
        }