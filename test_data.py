from helper import get_num_data_type
from logging import exception
from json import dump, dumps

class TestTheData:
    def __init__(self, is_dynamodb):
        self.num_data_type = get_num_data_type(is_dynamodb)
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
                },
                "netSalary": {
                    "unit": str,
                    "value": self.num_data_type
                },
                "grossSalary": {
                    "unit": str,
                    "value": self.num_data_type
                },
                "values": {
                    "earnings": dict,
                    "discounts": dict,
                    "totals": dict
            }

        }
        self.str_units = ['fraction']

    def run(self, data, print_errors=True, save_log=False):
        """
        Return True if test passed.
        """
        try:
            schema_errors = []
            if isinstance(data, list):
                for idx in range(len(data)):
                    for k, v in data[idx].items():
                        try:
                            if k == 'values':
                                for sub_key in ['earnings', 'discounts', 'totals']:
                                    for k, v in data[idx]['values'][sub_key].items():
                                        item = data[idx]['values'][sub_key][k]

                                        if isinstance(item, list):
                                            for idx2 in range(len(item)):
                                                if not isinstance(item[idx]['value'], self.num_data_type) and item[idx]['unit'] not in self.str_units:
                                                    schema_errors.append({data[idx]['id']: f"[{k}] => '{item[idx2]['value']}'"})
                                        else:
                                            if not isinstance(item['value'], self.num_data_type) and item['unit'] not in self.str_units:
                                                schema_errors.append({data['id']: f"[{k}] => '{item['value']}'"})

                            elif isinstance(v, dict):
                                for k2, v2 in v.items():
                                    if not isinstance(v2, self.schema[k][k2]):
                                        schema_errors.append({data[idx]['id']: f"[{k}][{k2}] => '{data[idx][k][k2]}'"}) 
                                                
                            elif not isinstance(v, self.schema[k]):
                                schema_errors.append({data[idx]['id']: f'[{k}] => \"{data[idx][k]}\"'})
                        except KeyError:
                            pass
            else:
                for k, v in data.items():
                    try:
                        if k == 'values':
                            for sub_key in ['earnings', 'discounts', 'totals']:
                                for k, v in data['values'][sub_key].items():
                                    item = data['values'][sub_key][k]

                                    if isinstance(item, list):
                                        for idx in range(len(item)):
                                            if not isinstance(item[idx]['value'], self.num_data_type) and item[idx]['unit'] not in self.str_units:
                                                schema_errors.append({data['id']: f"[{k}] => '{item[idx]['value']}'"})
                                    else:
                                        if not isinstance(item['value'], self.num_data_type) and item['unit'] not in self.str_units:
                                            schema_errors.append({data['id']: f"[{k}] => '{item['value']}'"})

                        elif isinstance(v, dict):
                            for k2, v2 in v.items():
                                if not isinstance(v2, self.schema[k][k2]):
                                    schema_errors.append({data['id']: f"[{k}][{k2}] => '{data[k][k2]}'"}) 
                                            
                        elif not isinstance(v, self.schema[k]):
                            schema_errors.append({data['id']: f'[{k}] => \"{data[k]}\"'})
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

            return has_errors == False
        
        except:
            exception('Error during running tests on data.')
            return True
