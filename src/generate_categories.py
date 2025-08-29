import MJO_tools
import numpy as np
import pandas as pd
import argparse



parser = argparse.ArgumentParser(
                    prog = 'plot_skill',
                    description = 'Plot prediction skill of GFS on AR.',
)

parser.add_argument('--months', type=int, nargs="+", help='Input directory that contains all cases', default=[-1,])
parser.add_argument('--no-display', action="store_true")

args = parser.parse_args()
print(args)


month_mapping = "JFMAMJJASOND"

if -1 in args.months:
    months_str = "All months"
    months = list(range(1, 13))
else:
    months_str = "".join([month_mapping[month-1] for month in args.months])
    months = args.months


MJO_df = MJO_tools.getMJOData()



OMI = MJO_df[['OMI1', 'OMI2']].to_numpy()

RMM1, RMM2 = MJO_tools.toRMM(OMI[:, 0], OMI[:, 1], index="OMI")
phase_angle, phase = MJO_tools.computeMJOPhase(RMM1, RMM2)

verify_phase = MJO_df['phase'].to_numpy()


print(phase.shape)
print(verify_phase.shape)

print(np.all(phase == verify_phase))


MJO_evts = MJO_tools.detectMJOEvents(RMM1, RMM2)

dts = MJO_df['date']

print(MJO_evts)

print("There are %d MJO events detected." % (len(MJO_evts)))

mjo_decay_idx = []

for i, row in MJO_evts.iterrows():
    
    MJO_beg_idx, MJO_end_idx, MJO_len = row["beg_idx"], row["end_idx"], row["length"]
    #print("Event %d: idx=[%d:%d], length=%d" % (i+1, MJO_beg_idx, MJO_end_idx, MJO_len,))

    beg_dt = pd.Timestamp(MJO_df['date'].iloc[MJO_beg_idx]) 

    if MJO_len >= 10 and beg_dt.month in months:
        mjo_decay_idx.append(MJO_end_idx)


decay_df = MJO_df.iloc[mjo_decay_idx]['phase_angle']
print(decay_df)
 

bins = np.linspace(0, 360, 17)
counts, _ = np.histogram(decay_df.to_numpy(), bins=bins)
phase_angles = (bins[:-1] + bins[1:]) / 2 * np.pi/180
  
print(phase_angles)
print(counts)
print("Loading Matplotlib...")
import matplotlib as mpl

"""
if args.no_display is False:
    mpl.use('TkAgg')
else:
    mpl.use('Agg')
    mpl.rc('font', size=15)
    mpl.rc('axes', labelsize=15)

print("Done.")
"""
mpl.use('Agg')
mpl.rc('font', size=15)
mpl.rc('axes', labelsize=13)

print("Done.")


import matplotlib as mplt
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Rectangle
import matplotlib.transforms as transforms
from matplotlib.dates import DateFormatter
import matplotlib.ticker as mticker

def setRMMFigure(ax):
    
    ax.set_theta_zero_location("W")  # Set 0 degrees at the top
    angles = np.array([0, 45, 90, 135, 180, 225, 270, 315]) * np.pi/180
    ax.set_xticks(angles)
    ax.set_xticklabels(["West Hem.", "", "Indian Ocean", "", "Maritime Continent", "", "Western Pacific", ""])
   
    rotate_angles = [-90, 0, 0, 0, 90, 0, 0, 0]
    
    for i, (label, angle, rotate_angle) in enumerate(zip(ax.get_xticklabels(), angles, rotate_angles)):
        x,y = label.get_position()
        text = label.get_text()

        if text != "":
            lab = ax.text( x, y, text, transform=label.get_transform(),
                          ha=label.get_ha(), va=label.get_va())
            
            lab.set_rotation(rotate_angle)

    ax.set_xticklabels([])
        
    transform = mplt.transforms.blended_transform_factory(ax.transData, ax.transAxes)
   
    rlim = ax.get_ylim()
    dr = rlim[1] - rlim[0] 
    for i in range(8):
                
        angle = (22.5 + 45.0 * i) * np.pi/180 
        ax.text(angle, rlim[0] + 1.1*dr, "%d" % (i+1,), fontsize=15, ha="center", va="center")

def wrapAround(arr):
    return np.concatenate( (arr, arr[0:1]) )

fig, ax = plt.subplots(
    1, 1,
    subplot_kw={'projection': 'polar'},
    figsize=(8, 6),
)

width = (2*np.pi) / len(bins)

ax.bar(phase_angles, counts, width=width, bottom=0.0, facecolor="#cccccc")

ax.plot(wrapAround(phase_angles), wrapAround(counts), linewidth=2, marker='o', color='k')

ax.set_title("Histogram of MJO Decay Phase Angle. %s" % (months_str,), pad=30)


#ax.set_theta_direction(-1)      # Clockwise direction
ax.grid(True)
ax.set_yticks([5, 10, 15])
ax.set_ylim([0, 20])

setRMMFigure(ax)


output_file = "MJO_decay_%s.svg" % (months_str.replace(' ', '_'),)

print("Output file: ", output_file)
fig.savefig(output_file)
