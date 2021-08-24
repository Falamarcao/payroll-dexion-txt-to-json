from txt_parser import crazy_txt_to_json
from json import dump, dumps
from os.path import join
from tqdm import tqdm
from os import walk


files = []
for (dirpath, dirnames, filenames) in walk('../../025 - FOLHAS DE PAGAMENTOS - EXPORTAR'):
    if len(filenames) > 0:
        for filename in filenames:
            files.append(join(dirpath, filename))


data = {"data":[]}
for file in tqdm(files):
    file = '../../025 - FOLHAS DE PAGAMENTOS - EXPORTAR/INFRACEA Aeroportos/2018/folha-infracea-aeroportos-03-2018.TXT'
    json_generator = crazy_txt_to_json(open(file, 'r', encoding='cp1252').read(), is_dynamodb=False)
    data['data'] = data['data'] + [json for json in json_generator]


# TEST
schema = { 
            "id": str,
            "createdAt": str,
            "employeeId": str,
            "payday": str,
            "period": {
                "start": str,
                "end": str
            },
            "company": {
                "name": str,
                "cnpj": str,
                "completeAddress": str
            },
            "fullName": str,
            "status": (None, str),
            "netSalary": {
                "unit": "BRL",
                "value": float
            },
            "grossSalary": {
                "unit": "BRL",
                "value": float
            },
            "jobTitle": str,
            "hiredAt": str,
            "terminatedAt": str,
            "values": {
                "earnings": dict,
                "discounts": dict,
                "totals": dict
            }

        }

schema_errors = []
for idx in range(len(data['data'])):
    for k, v in data['data'][idx].items():

        if k == 'values':
            for sub_key in ['earnings', 'discounts', 'totals']:
                for k, v in data['data'][idx]['values'][sub_key].items():

                    item = data['data'][idx]['values'][sub_key][k]

                    if isinstance(item, list):
                        for idx2 in range(len(item)):
                            if not isinstance(item[idx2]['value'], float):
                                schema_errors.append({data['data'][idx]['id']: item[idx2]['value']})
        
        # elif not isinstance(v, schema[k]):
        #     schema_errors.append({data['data'][idx]['id']: data['data'][idx][k]})


if len(schema_errors) > 0:
    print('Schema Errors: ', '\n', dumps(schema_errors, indent=4, ensure_ascii=False), '\n')

# Record to file
with open('output.json', 'w', encoding='utf-8') as json_file:
    dump(data, json_file, indent=4, ensure_ascii=False)

    # print(dumps(json, indent=4, ensure_ascii=False))






        

