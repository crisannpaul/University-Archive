import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# 1. Create output folder
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# 2. Load & clean wins
wins = pd.read_csv('wins.csv')
wins['Date'] = pd.to_datetime(wins['Date'], dayfirst=True, errors='coerce')
wins['Prize'] = (wins['Prize']
                  .astype(str)
                  .str.replace(',', '.')
                  .astype(float))
wins = wins.sort_values('Date').reset_index(drop=True)

# 3. Compute days between wins
wins['DaysDiff'] = wins['Date'].diff().dt.days.fillna(0)

# 4. Prepare colormap
#    we’ll map DaysDiff to colors in the "viridis" colormap
cmap = plt.get_cmap('viridis')
norm = plt.Normalize(vmin=wins['DaysDiff'].min(), vmax=wins['DaysDiff'].max())

# 5. Plot
fig, ax = plt.subplots(figsize=(12,6))

# a) draw each line segment in the color for its gap
for i in range(1, len(wins)):
    x0, y0 = wins.loc[i-1, ['Date', 'Prize']]
    x1, y1 = wins.loc[i,   ['Date', 'Prize']]
    gap = wins.loc[i, 'DaysDiff']
    ax.plot([x0, x1], [y0, y1],
            color=cmap(norm(gap)),
            linewidth=2)

# b) draw the markers on top
sc = ax.scatter(wins['Date'], wins['Prize'],
                c=wins['DaysDiff'], cmap=cmap, norm=norm,
                edgecolor='k', s=80, zorder=5)

# 6. Formatting
ax.set_title('Prize Evolution (line‐segments colored by days since last win)')
ax.set_xlabel('Date of Win')
ax.set_ylabel('Prize Amount')
ax.grid(True, alpha=0.3)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
fig.autofmt_xdate()

# 7. Colorbar
cbar = fig.colorbar(sc, ax=ax, pad=0.02)
cbar.set_label('Days since previous win')

# 8. Save & show
out = os.path.join(output_dir, 'prize_timeline_colored_by_gap.png')
plt.tight_layout()
plt.savefig(out, dpi=300)
print(f"Saved to {out}")
plt.show()
