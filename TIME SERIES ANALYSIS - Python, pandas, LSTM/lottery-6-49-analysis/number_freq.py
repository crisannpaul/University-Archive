import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm

# 1. Create output folder for charts if it doesn't exist
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# 2. Load the draws dataset
df = pd.read_csv('RawDataset.csv')

# 3. Extract all numbers from the 6 columns and count occurrences
number_columns = ['Nr.1', 'Nr.2', 'Nr.3', 'Nr.4', 'Nr.5', 'Nr.6']
all_numbers = pd.concat([df[col] for col in number_columns], ignore_index=True)
counts = all_numbers.value_counts().reindex(range(1, 50), fill_value=0).sort_index()

# 4. Prepare a colormap so bright = many occurrences, dark = few
cmap = plt.get_cmap('viridis')               # use plt.get_cmap to avoid deprecation warning
norm = Normalize(vmin=counts.min(), vmax=counts.max())
bar_colors = cmap(norm(counts.values))

# 5. Plot the bar chart of occurrences with colored bars
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(counts.index.astype(str), counts.values,
              color=bar_colors, edgecolor='black', alpha=0.9)

# 6. Add a colorbar legend for reference
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # only needed for the colorbar itself
cbar = fig.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('Count of Occurrences')

# 7. Formatting
ax.set_title('Occurrence of Each Number (1–49) with Color Intensity by Frequency')
ax.set_xlabel('Number')
ax.set_ylabel('Count of Occurrences')
ax.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()

# 8. Save the chart
output_path = os.path.join(output_dir, 'number_occurrences_colored.png')
plt.savefig(output_path, dpi=300)
print(f'Chart saved to: {output_path}')

# 9. Display the chart
plt.show()
