import pyspark
import subprocess
import os
import subprocess
from pyspark.sql import SQLContext
from pyspark import SparkContext
import pyspark
import ast
import pandas as pd
from pyspark.ml.feature import Word2Vec
from pyspark.sql import functions, SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

def main():
    print('Hello world')
    
    cmd = 'hdfs dfs -ls /jsons/'

    files = subprocess.check_output(cmd, shell=True)
    files = files.strip()
    files = files.decode().split('\n')

    out = []
    
    i = 0
    for path in files:
        i += 1
        if i == 50: break
        f = path.split(" ")[-1]
        if '.json' in f: out.append(f)

    #for i in out:

    #    print(i)

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
    #print(ans.head())
    #print(ans.loc[:, 'text'])

    # sc = SparkContext()
    spark = SparkSession(sc)
    ans = spark.createDataFrame(ans)
    split_col = functions.split(ans.text, ' ')
    ans = ans.withColumn("text", split_col)
    print(ans.select('text').show())
    
    word2Vec = Word2Vec(vectorSize=50, seed=42, inputCol="text", outputCol="features")
    model = word2Vec.fit(ans)
    ans = model.transform(ans)
    
    for i in range(2, 10):
        kmeans = KMeans(k = i)
        modelk = kmeans.fit(ans)
        predictions = modelk.transform(ans)
        print(predictions.select('text', 'prediction').show())

        evaluator = ClusteringEvaluator()
        silhouette = evaluator.evaluate(predictions)
        print("k=" + str(i))
        print("Silhouette = " + str(silhouette))

    #print(ans.select('model').show())
    #print(model.getVectors().count())
    #print(model.getVectors().show())
    #ans.printSchema()

if __name__ == "__main__":
     main()
