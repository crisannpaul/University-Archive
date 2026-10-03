import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Create the output folder for charts if it doesn't exist
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# 2. Load and preprocess the draws data
df = pd.read_csv('RawDataset.csv')
# Convert the draw date column to datetime and sort chronologically
df['Data tragerii'] = pd.to_datetime(df['Data tragerii'], dayfirst=True, errors='coerce')
df = df.sort_values('Data tragerii')

# 3. Count how many even numbers each draw had
df['EvenCount'] = (
    df[['Nr.1', 'Nr.2', 'Nr.3', 'Nr.4', 'Nr.5', 'Nr.6']]
    .applymap(lambda x: x % 2 == 0)
    .sum(axis=1)
)

# 4. Aggregate: how many draws had 0, 1, …, 6 even numbers
distribution = df['EvenCount'].value_counts().sort_index()

# 5. Plot the distribution as a bar chart
plt.figure(figsize=(8, 5))
plt.bar(distribution.index.astype(str), distribution.values,
        edgecolor='black', alpha=0.7)
plt.title('Distribution of Even Numbers per Draw (6/49)')
plt.xlabel('Number of Even Numbers in Draw')
plt.ylabel('Number of Draws')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

# 6. Save the chart to the plots folder
output_path = os.path.join(output_dir, 'even_number_distribution.png')
plt.savefig(output_path, dpi=300)
print(f'Chart saved to: {output_path}')

# 7. (Optional) Display the chart
plt.show()
