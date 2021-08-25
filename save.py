from boto3 import resource
from json import dump


def save_json(s3_client, json_content):
    json_path = os_path.split(key)[1].split('.')[0] + '.json'
        
    with open('/tmp/' + json_path, 'w', encoding='utf-8') as json_file:
        dump([item for item in json_content], json_file, ensure_ascii=False)
    
    s3_client.upload_file('/tmp/' + json_path, Bucket=bucket_name, Key='RH/folha-de-pagamento/dexion/json/' + json_path)


def save_to_dynamodb(json_content, key):
    try:
        db = resource('dynamodb')
        table = db.Table('SomosINFRACEA_PayrollTable')

        with table.batch_writer(overwrite_by_pkeys=['id','payday']) as batch:
            for item in json_content:
                batch.put_item(Item=item)
    except Exception as e:
        print(f'An Error has occured on save_to_dynamodb for key: {key}')
        print(e)
    
    print(f'{key} was saved on DynamoDB.')
    