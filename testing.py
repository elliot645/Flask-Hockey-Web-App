from apiExtraction import eventCollection as ec

df = ec.shotDataFrame()

df.update_over_range('1998-01-01', '1998-01-05')
print(df)
df2 = ec.shotDataFrame(df.df)
print(df2)