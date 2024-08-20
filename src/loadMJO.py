import numpy as np
import pandas as pd
import os

data_dir = "data"

default_MJO_raw = "omi.era5.1x.webpage.4023.txt"
default_MJO_csv = "%s.csv" % (default_MJO_raw,)

default_MJO_raw = os.path.join(data_dir, default_MJO_raw)
default_MJO_csv = os.path.join(data_dir, default_MJO_csv)



def getMJOData(raw_file=default_MJO_raw, csv_file=default_MJO_csv, force_load=False):


    if not os.path.isfile(csv_file) or force_load:

        print("Parsing raw data file: ", raw_file)

        y, m, d, RMM1, RMM2, phase, magnitude = np.loadtxt(raw_file, unpack=True)

        dts = [
            pd.Timestamp(year=int(y[i]), month=int(m[i]), day=int(d[i]))
            for i in range(len(y))
        ]



        MJO_df = pd.DataFrame(data=dict(
            date=dts,
            RMM1 = RMM1,
            RMM2 = RMM2,
            phase = phase,
            magnitude = magnitude,
        ))

        MJO_df.set_index('date')
        
        print("Save parsed data to file: ", csv_file)
        MJO_df.to_csv(csv_file, index=False)

        MJO_df = None


        
    print("Loading data file: ", csv_file)
    MJO_df = pd.read_csv(csv_file)

    return MJO_df
