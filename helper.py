from datetime import datetime
from decimal import Decimal
from re import search


def convert_number(n, num_data_type):
    try:
        return num_data_type(n.replace('.','').replace(',','.'))
    except:
        return n

def to_AWSDate(date_string):
    match = search(r'\d{2}/\d{2}/\d{4}', date_string)
    return datetime.strptime(match.group(), '%d/%m/%Y').strftime('%Y-%m-%d') if match else None

def company_data(name: str):
    if name[0:14] == "INFRACEA SERVI":
        return {
            "name": "INFRACEA SERVIÇOS AEROPORTUÁRIOS EIRELI",
            "cnpj": "31.907.018/0001-03",
            "_cnpj": "31907018000103",
            "completeAddress": "EQS 114/115 - Edifício Casablanca, 09, Asa Sul, Brasília - DF, 70377-400"
        }
    elif name[0:17] == "INFRACEA CONTROLE":
        return {
            "name": "INFRACEA CONTROLE DO ESPAÇO AÉREO, AEROPORTOS E CAPACITAÇÃO LTDA",
            "cnpj": "17.469.843/0001-34",
            "_cnpj": "17469843000134",
            "completeAddress": "EQS 114/115 - Edifício Casablanca, 42, Asa Sul, Brasília - DF, 70377-400"
        }
        
    raise Exception("Error on helper.company_data: Employee's company not recognized")


def getData(matrix, include_locationCode=False):
    """
    Look for job title, location code and admission date
    """
    job_title = locationCode = None

    output = {}

    for i, columns in enumerate(matrix):
        for ii, column in enumerate(columns):
            if column != None:
                if column == '':
                    next
                elif column[0] == '/':
                    try:
                        job_title = matrix[i].pop(ii - 1)
                        locationCode = int(matrix[i].pop(ii - 1)[1:])
                        
                        if include_locationCode:
                            output.update({'jobTitle': job_title, 'locationCode': locationCode})
                        else:
                            output.update({'jobTitle': job_title})
                    except IndexError:
                        if include_locationCode:
                            output.update({'jobTitle': None, 'locationCode': int(job_title[1:])})
                        else:
                            output.update({'jobTitle': None})
                        
                if column[0:12] == 'ADMISSÃO EM ':
                    output.update({'hiredAt': to_AWSDate(matrix[i].pop(ii)[12:])})
                elif column[0:9] == 'RESCISÃO ':
                    output.update({'terminatedAt': to_AWSDate(matrix[i].pop(ii)[9:])})
                elif column[0:7] == 'FÉRIAS ':
                    period = matrix[i].pop(ii)[7:].split(' A ')
                    output.update({'vacationAt': {'start': to_AWSDate(period[0]), 'end': to_AWSDate(period[1])}})
                
                if len(output.keys()) > 2:
                    return output

    return output

def earnings_disconts(value):
    return 'discounts' if value[0] == '-' else 'earnings'
