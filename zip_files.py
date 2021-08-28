from zipfile import ZipFile


zipObj = ZipFile('somosinfracea-payroll.zip', 'w')

for file in ['lambda_function.py','helper.py','txt_parser.py','save.py','test_data.py']:
    zipObj.write(file)

zipObj.close()