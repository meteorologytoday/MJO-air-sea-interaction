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

        y, m, d, OMI1, OMI2, phase, magnitude = np.loadtxt(raw_file, unpack=True)

        dts = [
            pd.Timestamp(year=int(y[i]), month=int(m[i]), day=int(d[i]))
            for i in range(len(y))
        ]

        phase_angle, phase_mycompute = computeMJOPhase(*toRMM(OMI1, OMI2, index="OMI"))

        if np.any(phase != phase_mycompute):
            raise Exception("Warning: the phase I compute is not consistent with the phase given from the dataset.")


        MJO_df = pd.DataFrame(data=dict(
            date=dts,
            OMI1 = OMI1,
            OMI2 = OMI2,
            phase = phase,
            phase_angle = phase_angle,
            magnitude = magnitude,
        ))

        MJO_df.set_index('date')
        
        print("Save parsed data to file: ", csv_file)
        MJO_df.to_csv(csv_file, index=False)

        MJO_df = None


        
    print("Loading data file: ", csv_file)
    MJO_df = pd.read_csv(csv_file)

    return MJO_df
    
@np.vectorize        
def computeMJOPhase(RMM1, RMM2):

    phase_angle = np.arctan2(RMM2, RMM1) * 180/np.pi + 180.0
    phase = int(np.floor( phase_angle / 45.0 ) + 1)

    return phase_angle, phase


def toRMM(i1, i2, index):
    
    if index == "RMM":
        RMM1 = i1
        RMM2 = i2
    elif index == "OMI":
        RMM1, RMM2 = i2, - i1


    return RMM1, RMM2


# Assume consecutive daily data
def detectMJOEvents(RMM1s, RMM2s, expand_day=1, phase_angle_tolerance_deg=45.0):

    phase_angles, phases = computeMJOPhase(RMM1s, RMM2s)
    amps = np.sqrt(RMM1s**2 + RMM2s**2)
    
    N_data = len(RMM1s)

    seg_id_cnt = 0

    seg_labels = np.zeros_like(amps)
    seg_labels[:] = -1

    seg_flag = False

    is_MJO_flags = amps >= 1.0
   
    print("There are %d MJO flagged" % (np.sum(is_MJO_flags),))
 
    # If day x is MJO day, then x+1 is MJO day.
    # This prevents the situation where MJO is revived the day
    # after it diminished suddenly.
    is_MJO_flags = is_MJO_flags.astype(int)
    is_MJO_flags[1:] = is_MJO_flags[1:] + is_MJO_flags[:-1]
    is_MJO_flags = is_MJO_flags.astype(bool)
    
    print("There are %d MJO flagged after processed" % (np.sum(is_MJO_flags),))
   
    MJO_evts = []
    
    detected_MJO = False
    MJO_evt_beg_idx = -1
    MJO_evt_end_idx = -1
    for i, (is_MJO_flag, RMM1, RMM2, phase_angle, phase) in enumerate(zip(is_MJO_flags, RMM1s, RMM2s, phase_angles, phases)):
       
        # Looking for beginning
        if not detected_MJO:
            
            if is_MJO_flag:
                MJO_evt_beg_idx = i
                detected_MJO = True
            else:
                pass # nothing to do        
        else:

            if is_MJO_flag:
                pass

            else:
                MJO_evt_end_idx = i - 1
                MJO_length = MJO_evt_end_idx - MJO_evt_beg_idx + 1
                MJO_evts.append((MJO_evt_beg_idx, MJO_evt_end_idx, MJO_length))

                detected_MJO = False
                MJO_evt_beg_idx = -1                
                MJO_evt_end_idx = -1                

    MJO_evts = pd.DataFrame(columns=['beg_idx', 'end_idx', 'length'], data=MJO_evts)

    return MJO_evts
                
                
        
        

