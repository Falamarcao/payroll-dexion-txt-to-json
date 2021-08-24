from boto3 import resource
import json

def save_json(s3_client, json_content):
    json_path = os_path.split(key)[1].split('.')[0] + '.json'
        
    with open('/tmp/' + json_path, 'w', encoding='utf-8') as json_file:
        json.dump([item for item in json_content], json_file, ensure_ascii=False)
    
    s3_client.upload_file('/tmp/' + json_path, Bucket=bucket_name, Key='RH/folha-de-pagamento/dexion/json/' + json_path)


def save_to_dynamodb(json_content):
    db = resource('dynamodb')
    table = db.Table('SomosINFRACEA_PayrollTable')

    with table.batch_writer(overwrite_by_pkeys=['id','payday']) as batch:
        for item in json_content:
            batch.put_item(Item=item)
    