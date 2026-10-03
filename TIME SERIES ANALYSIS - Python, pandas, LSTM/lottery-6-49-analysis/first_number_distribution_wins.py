import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Create output folder for charts if it doesn't exist
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# 2. Load and preprocess the draws data
draws = pd.read_csv('RawDataset.csv')
draws['Data tragerii'] = pd.to_datetime(draws['Data tragerii'], dayfirst=True, errors='coerce')

# 3. Load and preprocess the wins data
wins = pd.read_csv('wins.csv')
wins['Date'] = pd.to_datetime(wins['Date'], dayfirst=True, errors='coerce')

# 4. Merge draws and wins on the draw date
#    Keep only the draws that ended up with a win
win_draws = pd.merge(
    wins[['Date']],
    draws,
    left_on='Date',
    right_on='Data tragerii',
    how='inner'
)

# 5. Classify each winning draw by its first number (Nr.1)
#    "<31" if Nr.1 < 31, otherwise ">=31"
win_draws['Category'] = win_draws['Nr.1'].apply(lambda x: '<31' if x < 31 else '>=31')

# 6. Count how many wins fall into each category
counts = win_draws['Category'].value_counts().reindex(['<31','>=31']).fillna(0)

# 7. Plot the bar chart
plt.figure(figsize=(6, 4))
plt.bar(counts.index, counts.values, color=['skyblue','salmon'], edgecolor='black')
plt.title('Wins by First Number Position: <31 vs ≥31')
plt.xlabel('First Number in Winning Draw')
plt.ylabel('Number of Wins')
for i, v in enumerate(counts.values):
    plt.text(i, v + 0.5, str(int(v)), ha='center')

plt.tight_layout()

# 8. Save the chart
output_path = os.path.join(output_dir, 'wins_first_number_lt31_vs_ge31.png')
plt.savefig(output_path, dpi=300)
print(f'Chart saved to: {output_path}')

# 9. Display the chart
plt.show()
