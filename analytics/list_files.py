import pyspark
import subprocess
import os
import subprocess
from pyspark.sql import SQLContext
from pyspark import SparkContext
import pyspark
import ast
import pandas as pd 

def main():
    print('Hello world')
    
    cmd = 'hdfs dfs -ls /jsons/'

    files = subprocess.check_output(cmd, shell=True)
    files = files.strip()
    files = files.decode().split('\n')

    out = []

    for path in files:
        f = path.split(" ")[-1]
        if '.json' in f: out.append(f)

    for i in out:

        print(i)

    # Reading JSON

    sc = SparkContext()
    sqlContext = SQLContext(sc)

    COLUMNS = ['id',
            'extension',
            'image_path',
            'source',
            'text',
            'url',
            'date',
            'title',
            'popularity',
            'tags']

    ans = []
    for json in out:
        df = sqlContext.read.option("multiline", True).option("mode", "PERMISSIVE").json(json)
        df = df.toPandas()
        if df.loc[0, "source"] == "memedroid":
            row = []
            d = ast.literal_eval(df.loc[0, 'additional_data'])
            for col in COLUMNS:
                if col in list(df.columns):
                    row.append(df.loc[0, col])
                else: 
                    row.append(d[col])

            ans.append(row)

    ans = pd.DataFrame(ans, columns=COLUMNS)
    print(ans.head())
    print(ans.loc[:, 'text'])

if __name__ == "__main__":
    main()
