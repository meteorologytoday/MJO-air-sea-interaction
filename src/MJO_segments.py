import loadMJO
import numpy as np

MJO_df = loadMJO.getMJOData()


# Select MJO strong enough
MJO_df = MJO_df.loc[ MJO_df['magnitude'] > 1 ]

# Detect a segment of MJO days
threshold_days = 3












#print(selected_df)










