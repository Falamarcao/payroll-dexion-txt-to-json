from txt_parser import crazy_txt_to_json 
from test_data import TestTheData
from os.path import join
from json import dump, JSONEncoder
from decimal import Decimal
from tqdm import tqdm
from os import walk

is_dynamodb = False

path = 'E:/Users/falamarcao/Desktop/025 - FOLHAS DE PAGAMENTOS - EXPORTAR/SERVIÇOS/2021'

files = []
for (dirpath, dirnames, filenames) in walk(path):
    if len(filenames) > 0:
        for filename in filenames:
            files.append(join(dirpath, filename))

data = {"data":[]}
for file in tqdm(files):
    if 'folha-infracea-serviços-07-2021.TXT' in file:
        # The test has to be rb (bytes), because S3 is like that
        json_generator = crazy_txt_to_json(open(file, 'rb').read().decode('cp1252'), is_dynamodb=is_dynamodb)
        # json_generator = crazy_txt_to_json(open(file, 'r', encoding='cp1252').read(), is_dynamodb=is_dynamodb)
        data['data'] = data['data'] + [json for json in json_generator]

# To make Decimal JSON seralizable to test when is_dynamodb = True 
class DecimalEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

f = open('output.json', 'w', encoding='utf-8')
f.close()
with open('output.json', 'w', encoding='utf-8') as json_file:
    dump(data['data'], json_file, indent=4, ensure_ascii=False, cls=DecimalEncoder if is_dynamodb else None)
# print(dumps(data['data'], indent=4, ensure_ascii=False))
