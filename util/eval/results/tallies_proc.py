import pandas as pd
import json
df = pd.read_csv('tallies.csv', header=[0,1])

df = df.sort_values(by=('anly','total'), ascending=False)

with open('results') as f:
    js = json.load(f) 
print(df)

