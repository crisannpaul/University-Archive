import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('winequality.csv', sep=';')

# Count the instances for each quality level
quality_counts = df['quality'].value_counts().sort_index()
# Plot the distribution
plt.figure(figsize=(10, 6))
quality_counts.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Dispersion of Instances Over Quality Levels', fontsize=16)
plt.xlabel('Quality Levels', fontsize=14)
plt.ylabel('Number of Instances', fontsize=14)
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
output_path = "quality_dispersion.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"Figure saved as {output_path}")