import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Create output folder for charts if it doesn't exist
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# 2. Load and preprocess the draws data
draws = pd.read_csv('RawDataset.csv')
draws['Data tragerii'] = pd.to_datetime(draws['Data tragerii'], errors='coerce')
draws = draws.sort_values('Data tragerii')

# 3. Load and preprocess the wins data
wins = pd.read_csv('wins.csv')
wins['Date'] = pd.to_datetime(wins['Date'], dayfirst=True, errors='coerce')

# 4. Merge draws for win dates only
#    (keeps only those rows in draws where Data tragerii matches a win Date)
win_draws = draws[draws['Data tragerii'].isin(wins['Date'])].copy()

# 5. Count how many even numbers each winning draw had
win_draws['EvenCount'] = (
    win_draws[['Nr.1', 'Nr.2', 'Nr.3', 'Nr.4', 'Nr.5', 'Nr.6']]
    .applymap(lambda x: x % 2 == 0)
    .sum(axis=1)
)

# 6. Aggregate: how many winning draws had 0, 1, …, 6 even numbers
distribution = win_draws['EvenCount'].value_counts().sort_index()

# 7. Plot the distribution as a bar chart
plt.figure(figsize=(8, 5))
plt.bar(distribution.index.astype(str), distribution.values,
        edgecolor='black', alpha=0.7)
plt.title('Distribution of Even Numbers in Winning Draws')
plt.xlabel('Number of Even Numbers in Winning Draw')
plt.ylabel('Number of Winning Draws')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

# 8. Save the chart to the plots folder
output_path = os.path.join(output_dir, 'win_even_number_distribution.png')
plt.savefig(output_path, dpi=300)
print(f'Chart saved to: {output_path}')

# 9. (Optional) Display the chart
plt.show()
