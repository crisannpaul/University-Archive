import matplotlib.pyplot as plt
import pandas as pd
from torchvision import datasets, transforms


transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
mnist_train = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
# Count the instances for each label
labels = [label for _, label in mnist_train]
label_counts = pd.Series(labels).value_counts().sort_index()
# Plot the distribution
plt.figure(figsize=(10, 6))
label_counts.plot(kind='bar', color='lightgreen', edgecolor='black')
plt.title('Dispersion of Instances Over MNIST Labels', fontsize=16)
plt.xlabel('Digit Labels', fontsize=14)
plt.ylabel('Number of Instances', fontsize=14)
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
output_path = "mnist_dispersion.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"Figure saved as {output_path}")