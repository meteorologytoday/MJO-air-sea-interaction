import loadMJO
import numpy as np






MJO_df = loadMJO.getMJOData()

selected_df = MJO_df.loc[ MJO_df['phase'].isin([3,4])  & (MJO_df['magnitude'] > 1) ]


print(selected_df)










