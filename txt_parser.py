from helper import (convert_number, to_AWSDate, getData,
                    company_data, earnings_disconts, get_num_data_type)
from re import split, sub, DOTALL
from datetime import datetime, timezone
from test_data import TestTheData


def crazy_txt_to_json(file_content, is_dynamodb):
    num_data_type = get_num_data_type(is_dynamodb)
    
    # Data clean - Remove headers, stats and footers
    file_content = file_content.replace(f'{" "*16}TRABALHADORES{" "*37}PROVENTOS{" "*41}DESCONTOS', '')
    file_content = sub(r'___.*\s*INFRACEA\s.*\n.*\n.*Folha\sde\sPagamento\n.*\n.*PERÍODO.*A\s\d{2}\/\d{2}\/\d{4}', '', file_content)
    file_content = sub(r'INFRACEA.*\n.*-\s\d{2}:\d{2}:\d{2}', '', file_content)
    file_content = sub(r'Totalização(.*?)VALOR A COMPENSAR/RESTITUIR\s*:\s*\d+,\d{1,2}', '', file_content, flags=DOTALL)
    file_content = file_content.replace('_','')

    employees = split(r'.(?=[0-9]{6}([A-Z]*\s)*)', file_content)

    # Header (data) = employees.pop(0)
    header_column = [x.strip() for x in employees.pop(0).split('\n')]
    dates = header_column.pop(2).split(' '*26)

    period = dates.pop(2).split(' A ')

    # Data to append to each row
    payday = to_AWSDate(dates.pop(1).split(': ')[1])
    period = {'start': to_AWSDate(period.pop(0).split(' : ').pop(1)), 'end': to_AWSDate(period.pop(0))}
    company_name = header_column.pop(1).split(' -')[0]

    del dates
    del header_column

    for employee in employees:
        if employee != None:

            rows = [x for x in employee.replace(':','').split('\n') if x  != [] and x not in ['', ' ']]
    
            if len(rows) > 1:
                matrix = []
                for row in rows:
                    columns = list(filter(lambda x: False if x in [' ','',' :',':','-'] else True, '_{N/A}_'.join(row.replace(':','').split(' '*50)).split('   ')))
                    for idx_column in range(len(columns)):

                        # Split columns that have 2 empty spaces (' '*2) and not ' '*3
                        new_columns = list(filter(None, columns[idx_column].split('  ')))
                        if len(new_columns) == 2 and isinstance(convert_number(new_columns[0], num_data_type), num_data_type):
                            columns = columns[:idx_column] + new_columns + columns[idx_column + 2:]

                        # Set empty columns - cleaning wrong insertions of N/A
                        if columns[idx_column] == '_{N/A}_':
                            columns[idx_column] = None
                        else:
                            columns[idx_column] = columns[idx_column].replace('_{N/A}_','').strip().rstrip()              

                    matrix.append(columns)
                del rows
            
                item = {}
    
                id_name = matrix[0].pop(0)
                id = int(id_name[0:6])
                
                company = company_data(company_name)
                
                item.update({
                    'id': f"{id}{company.pop('_cnpj')}{payday.replace('-','')}",
                    'createdAt': datetime.now(timezone.utc).isoformat(),
                    'employeeId': str(id),
                    'payday': payday,
                    'period': period,
                    'company': company,
                    'fullName': id_name[6:],
                    'netSalary': {'unit': 'BRL', 'value': None},
                    'grossSalary': {'unit': 'BRL', 'value': None},
                })
                del id_name
                
                # get jobTitle, hiredAt or terminatedAt
                item.update(getData(matrix, year=payday[0:4]))
    
                item['values'] = {'earnings': {}, 'discounts': {}, 'totals': {}}

                # Set negative columns
                for columns in matrix:
                    try:
                        if ' '.join(columns[-2][0:8].split()) not in ['BASE DO', 'SALÁRIO']:
                            columns[-1] = f"-{columns[-1].replace(' ','')}"
                    except:
                        pass

                # Populate JSON
                for columns in matrix:
                    for column in columns.copy():
                        try:
                            column = columns.pop(0)

                            if column:
                            
                                """
                                In some cases we have columns with number of days followed by the value
                                """
                                if len(columns) > 1 and isinstance(convert_number(columns[1], num_data_type), num_data_type):
                                    column = column.replace("'","")
                                    days = columns.pop(0).split('(') 

                                    if len(days) == 1:
                                        item['values'][earnings_disconts(columns[0])].update({column:
                                                    [
                                                        {'unit': 'days', 'value': convert_number(days[0], num_data_type)},
                                                        {'unit': 'BRL', 'value': convert_number(columns.pop(0), num_data_type)}
                                                    ]  
                                        })
                                    else:
                                        item['values'][earnings_disconts(columns[0])].update({column:
                                                [
                                                    {'unit': 'days', 'value': convert_number(days[0], num_data_type)},
                                                    {'unit': 'fraction', 'value': days[1].replace(' ','').replace(')','')},
                                                    {'unit': 'BRL', 'value': convert_number(columns.pop(0), num_data_type)}
                                                ]  
                                        })
        
                                elif column[0:6] == 'FÉRIAS' or column[0:7] == 'RECISÃO':
                                    item['status'] = column
        
                                elif column in ['TOTAL DE PROVENTOS', 'TOTAL DE DESCONTOS', 'BASE DO INSS', 'BASE DO INSS MÊS', 'BASE DO FGTS', 'BASE DO FGTS MÊS', 'FGTS A RECOLHER MÊS', 'BASE DO IRRF MÊS']:
                                    item['values']['totals'].update({column: {'unit': 'BRL', 'value': convert_number(columns.pop(0), num_data_type)}})
                                
                                elif column == 'SALÁRIO LÍQUIDO':
                                    item['netSalary']['value'] = convert_number(columns.pop(0), num_data_type)
                                elif column == 'SALÁRIO BASE':
                                    item['grossSalary']['value'] = convert_number(columns.pop(0), num_data_type)

                                else:
                                    item['values'][earnings_disconts(columns[0])].update({column: {'unit': 'BRL', 'value': convert_number(columns.pop(0), num_data_type)}})
                                    if column == 'BASE DO IRRF MÊS':
                                        break
                                
                                if column == 'BASE DO IRRF MÊS' and bool(item):
                                    test_the_data = TestTheData(is_dynamodb)
                                    if test_the_data.run(item, save_log=is_dynamodb == False):
                                       yield item
                                    else:
                                        print(f":\n id: \"{item['id']}\", \"{item['payday']}\", \"{item['fullName']}\"\n")
                                        raise Exception("Error parsing file, check details above.\n\n")
                        
                        except IndexError:
                            next

