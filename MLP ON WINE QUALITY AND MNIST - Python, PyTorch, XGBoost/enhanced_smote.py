import matplotlib.pyplot as plt
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from imblearn.over_sampling import SMOTE
import numpy as np

class EnhancedMLP(nn.Module):
    def __init__(self, input_size, output_size):
        super(EnhancedMLP, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_size)
        )

    def forward(self, x):
        return self.model(x)

def train_model_with_scheduler(model, train_loader, criterion, optimizer, scheduler, epochs):
    model.train()
    epoch_losses = []
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            if len(inputs.shape) > 2:
                inputs = inputs.view(inputs.size(0), -1)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        scheduler.step()
        epoch_loss = running_loss / len(train_loader)
        epoch_losses.append(epoch_loss)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}, LR: {scheduler.get_last_lr()[0]:.6f}")
    return epoch_losses

def evaluate_model(model, test_loader):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            if len(inputs.shape) > 2:
                inputs = inputs.view(inputs.size(0), -1)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(targets.cpu().numpy())
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    return acc, f1

def process_wine_quality_smote():
    df = pd.read_csv('winequality.csv', sep=';')
    X = df.drop('quality', axis=1).values
    y = df['quality'].values - df['quality'].min()

    # Scale features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    # Apply SMOTE to oversample minority classes
    smote = SMOTE(random_state=42, k_neighbors=2)  # Adjust k_neighbors to handle small class sizes
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    # Train-test split after SMOTE
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

    train_dataset = DatasetFromNumpy(X_train, y_train)
    test_dataset = DatasetFromNumpy(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    input_size = X.shape[1]
    output_size = len(np.unique(y))

    return train_loader, test_loader, input_size, output_size

class DatasetFromNumpy(Dataset):
    def __init__(self, data, labels):
        self.data = torch.tensor(data, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load Wine Quality dataset with SMOTE
epochs = 30
wine_train_loader, wine_test_loader, wine_input_size, wine_output_size = process_wine_quality_smote()
wine_model = EnhancedMLP(input_size=wine_input_size, output_size=wine_output_size).to(device)

# Define loss, optimizer, and scheduler
wine_criterion = nn.CrossEntropyLoss()
wine_optimizer = optim.Adam(wine_model.parameters(), lr=0.001)
wine_scheduler = optim.lr_scheduler.StepLR(wine_optimizer, step_size=10, gamma=0.5)

# Train and evaluate
wine_losses = train_model_with_scheduler(wine_model, wine_train_loader, wine_criterion, wine_optimizer, wine_scheduler, epochs)
wine_acc, wine_f1 = evaluate_model(wine_model, wine_test_loader)

# Display results
print(f"Wine Quality Dataset with SMOTE - Accuracy: {wine_acc:.4f}, F1-Score: {wine_f1:.4f}")

# Plot training loss
plt.figure(figsize=(10, 6))
plt.plot(range(1, epochs + 1), wine_losses, label="Wine Quality Dataset", marker='o')
plt.title("Training Loss Over Epochs (Wine Quality Dataset with SMOTE)")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
output_path = "wine_smote_training_loss.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"Training loss plot saved as {output_path}")
