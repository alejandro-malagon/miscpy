import os
import glob
import pandas as pd
import pyodbc
from sqlalchemy import create_engine

os.chdir("REPLACE")

csv_files = glob.glob('*.csv')
print(csv_files)

xlsx_files = glob.glob('*.xlsx')
print(xlsx_files)

list_data = []

for filename in csv_files:
    data = pd.read_csv(filename, parse_dates = True)
    # print(data.shape)
    list_data.append(data)


for filename in xlsx_files:
    data = pd.read_excel(filename, header = 0)
    # print(str(filename) + str(data.shape))
    list_data.append(data)

df_data = pd.concat(list_data)
df_columns = list(df_data)
# print(df_columns)
# print(df_csv_data.info())

for i, value in enumerate(df_columns):
    if value in ('Escrow', 'Principal', 'Interest', 'NetInterest', 'DepositedRemitted'):
        df_data[df_columns[i]] = df_data[df_columns[i]].str.replace(",", "")
        df_data[df_columns[i]] = df_data[df_columns[i]].str.replace("(", "-")
        df_data[df_columns[i]] = df_data[df_columns[i]].str.replace(")", "")
        df_data[df_columns[i]] = pd.to_numeric(df_data[df_columns[i]])

engine = create_engine("mssql+pyodbc://10110-LT-80159\\MSSQLSERVER2016/APPL_BANK_DATA?driver=SQL+Server+Native+Client+11.0?Trusted_Connection=yes")
con = engine.connect()
df_data.to_sql("tbl_Loan_Pyoffs", engine, if_exists = 'replace', index = False)