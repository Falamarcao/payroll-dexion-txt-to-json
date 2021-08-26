from txt_parser import crazy_txt_to_json 
from test_data import TestTheData
from os.path import join
from json import dump
from tqdm import tqdm
from os import walk

is_dynamodb = True

path = 'E:/Users/falamarcao/Desktop/SomosINFRACEA/RH/Folha de Pagamento/025 - FOLHAS DE PAGAMENTOS - EXPORTAR'

files = []
for (dirpath, dirnames, filenames) in walk(path):
    if len(filenames) > 0:
        for filename in filenames:
            files.append(join(dirpath, filename))

data = {"data":[]}
for file in tqdm(files):
    # if 'aeroportos-07-2021' in file:
    json_generator = crazy_txt_to_json(open(file, 'r', encoding='cp1252').read(), is_dynamodb=is_dynamodb)
    data['data'] = data['data'] + [json for json in json_generator]

if not is_dynamodb:
    f = open('output.json', 'w', encoding='utf-8')
    f.close()
    with open('output.json', 'w', encoding='utf-8') as json_file:
        dump(data['data'], json_file, indent=4, ensure_ascii=False)
    # print(dumps(data['data'], indent=4, ensure_ascii=False))
