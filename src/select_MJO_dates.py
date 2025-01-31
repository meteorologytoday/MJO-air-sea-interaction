import MJO_tools
import numpy as np


MJO_df = MJO_tools.getMJOData()



OMI = MJO_df[['OMI1', 'OMI2']].to_numpy()

RMM1, RMM2 = MJO_tools.toRMM(OMI[:, 0], OMI[:, 1], index="OMI")
phase_angle, phase = MJO_tools.computeMJOPhase(RMM1, RMM2)

verify_phase = MJO_df['phase'].to_numpy()


print(phase.shape)
print(verify_phase.shape)

print(np.all(phase == verify_phase))


MJO_evts = MJO_tools.detectMJOEvents(RMM1, RMM2)

print(MJO_evts)

print("There are %d MJO events detected." % (len(MJO_evts)))
for i, row in MJO_evts.iterrows():
    
    MJO_beg_idx, MJO_end_idx, MJO_len = row["beg_idx"], row["end_idx"], row["length"]
    
    print("Event %d: idx=[%d:%d], length=%d" % (i+1, MJO_beg_idx, MJO_end_idx, MJO_len,))
 
#selected_df = MJO_df.loc[ MJO_df['magnitude'] > 1 ]


#print(selected_df)










