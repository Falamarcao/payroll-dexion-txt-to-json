from txt_parser import crazy_txt_to_json
from json import dump, dumps
from logging import exception


class TestTheData:
    def __init__(self):
        self.schema = { 
                "id": str,
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
                "status": {
                    "type": str,
                    "description": str,
                    "date": str,
                    "period": dict,
                },
                "netSalary": {
                    "unit": str,
                    "value": float
                },
                "grossSalary": {
                    "unit": str,
                    "value": float
                },
                "values": {
                    "earnings": dict,
                    "discounts": dict,
                    "totals": dict
            }

        }
        self.str_units = ['fraction']

    def run(self, data, print_errors=True, save_log=False):
        try:
            schema_errors = []
            for idx in range(len(data)):
                for k, v in data[idx].items():
                    try:
                        if k == 'values':
                            for sub_key in ['earnings', 'discounts', 'totals']:
                                for k, v in data[idx]['values'][sub_key].items():

                                    item = data[idx]['values'][sub_key][k]

                                    if isinstance(item, list):
                                        for idx2 in range(len(item)):
                                            if not (item[idx2]['unit'] in self.str_units or isinstance(item[idx2]['value'], float)):
                                                schema_errors.append({data[idx]['id']: f"[{k}] => '{item[idx2]['value']}'"})

                        elif isinstance(v, dict):
                            for k2, v2 in v.items():
                                if not isinstance(v2, self.schema[k][k2]):
                                    schema_errors.append({data[idx]['id']: f"[{k}][{k2}] => '{data[idx][k][k2]}'"}) 
                                            
                        elif not isinstance(v, self.schema[k]):
                            schema_errors.append({data[idx]['id']: f'[{k}] => \"{data[idx][k]}\"'})
                    except KeyError:
                        pass
            
            has_errors = len(schema_errors) > 0
            if print_errors and has_errors:
                print('Schema Errors: ', '\n', dumps(schema_errors, indent=4, ensure_ascii=False), '\n')

            if save_log:
                f = open('errors.log', 'w', encoding='utf-8')
                f.close()
                with open('errors.log', 'w', encoding='utf-8') as f:
                    if has_errors:
                        dump(schema_errors, f, indent=4, ensure_ascii=False)
                    else:
                        f.write('NO ERRORS')

            return has_errors
        
        except:
            exception('Error during running tests on data.')
            return True

if __name__ == '__main__':
    from os.path import join
    from tqdm import tqdm
    from os import walk

    path = 'E:/Users/falamarcao/Desktop/SomosINFRACEA/RH/Folha de Pagamento/025 - FOLHAS DE PAGAMENTOS - EXPORTAR'

    files = []
    for (dirpath, dirnames, filenames) in walk(path):
        if len(filenames) > 0:
            for filename in filenames:
                files.append(join(dirpath, filename))


    data = {"data":[]}
    for file in tqdm(files):
        if 'aeroportos-07-2021' in file:
            json_generator = crazy_txt_to_json(open(file, 'r', encoding='cp1252').read(), is_dynamodb=False)
            data['data'] = data['data'] + [json for json in json_generator]
    
    test_the_data = TestTheData()
    has_errors = test_the_data.run(data['data'], print_errors=False, save_log=True)

    # if has_errors:
    f = open('output.json', 'w', encoding='utf-8')
    f.close()
    with open('output.json', 'w', encoding='utf-8') as json_file:
        dump(data['data'], json_file, indent=4, ensure_ascii=False)
    # print(dumps(data['data'], indent=4, ensure_ascii=False))







        

