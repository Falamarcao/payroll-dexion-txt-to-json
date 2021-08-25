from txt_parser import crazy_txt_to_json
from save import save_to_dynamodb
from test import TestTheData
import os.path as os_path
from boto3 import client
import urllib.parse


s3 = client('s3')
bucket_name = 'somos-infracea'


def lambda_handler(event, context):
    """
    Convert Dexion txt crazy table to JSON
    """

    # Get the object from the event and show its content type
    # bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        txt_file = s3.get_object(Bucket=bucket_name, Key=key)
        
        print(key)
        json_generator = crazy_txt_to_json(txt_file['Body'].read().decode('cp1252'))

        # Test Data
        test_the_data = TestTheData()
        data = [data for data in json_generator]
        has_errors = test_the_data.run(data)
        del data
        
        if not has_errors:
            save_to_dynamodb(json_generator, key)
        
    except Exception as e:
        print(e)
        raise e
