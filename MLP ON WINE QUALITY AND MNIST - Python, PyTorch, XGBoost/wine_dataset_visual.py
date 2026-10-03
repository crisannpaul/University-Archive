import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

wine_data = pd.read_csv("winequality.csv", sep=';')

correlation_matrix = wine_data.corr()

plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Feature Correlation Heatmap", fontsize=16)

output_file = "feature_correlation_heatmap.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")

plt.show()

print(f"Heatmap saved as {output_file}")
