import pandas as pd

def dict_to_excel(dict_of_dataframes, filename):
    writer = pd.ExcelWriter(filename, engine='openpyxl') 
    for df_name, df in dict_of_dataframes.items():
        df.to_excel(writer, sheet_name=df_name)
    writer.save()