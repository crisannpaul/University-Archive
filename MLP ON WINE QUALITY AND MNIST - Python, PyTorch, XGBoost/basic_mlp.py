import matplotlib.pyplot as plt
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from torchvision import datasets, transforms

class BasicMLP(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(BasicMLP, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.model(x)

def train_model(model, train_loader, criterion, optimizer, epochs):
    model.train()
    epoch_losses = []
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            if len(inputs.shape) > 2:  # Flatten inputs if image data
                inputs = inputs.view(inputs.size(0), -1)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        epoch_loss = running_loss / len(train_loader)
        epoch_losses.append(epoch_loss)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}")
    return epoch_losses

def evaluate_model(model, test_loader):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            if len(inputs.shape) > 2:  # Flatten inputs if image data
                inputs = inputs.view(inputs.size(0), -1)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(targets.cpu().numpy())
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    return acc, f1

def process_mnist():
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    input_size = 28 * 28
    output_size = 10
    return train_loader, test_loader, input_size, output_size

def process_wine_quality():
    df = pd.read_csv('winequality.csv', sep=';')
    X = df.drop('quality', axis=1).values
    y = df['quality'].values - df['quality'].min()
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    train_dataset = DatasetFromNumpy(X_train, y_train)
    test_dataset = DatasetFromNumpy(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    input_size = X.shape[1]
    output_size = len(set(y))
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

epochs = 30

wine_train_loader, wine_test_loader, wine_input_size, wine_output_size = process_wine_quality()
wine_model = BasicMLP(input_size=wine_input_size, hidden_size=128, output_size=wine_output_size).to(device)
wine_criterion = nn.CrossEntropyLoss()
wine_optimizer = optim.SGD(wine_model.parameters(), lr=0.01)
wine_losses = train_model(wine_model, wine_train_loader, wine_criterion, wine_optimizer, epochs)
wine_acc, wine_f1 = evaluate_model(wine_model, wine_test_loader)

mnist_train_loader, mnist_test_loader, mnist_input_size, mnist_output_size = process_mnist()
mnist_model = BasicMLP(input_size=mnist_input_size, hidden_size=128, output_size=mnist_output_size).to(device)
mnist_criterion = nn.CrossEntropyLoss()
mnist_optimizer = optim.SGD(mnist_model.parameters(), lr=0.01)
mnist_losses = train_model(mnist_model, mnist_train_loader, mnist_criterion, mnist_optimizer, epochs)
mnist_acc, mnist_f1 = evaluate_model(mnist_model, mnist_test_loader)

plt.figure(figsize=(10, 6))
plt.plot(range(1, epochs + 1), wine_losses, label="Wine Quality Dataset", marker='o')
plt.plot(range(1, epochs + 1), mnist_losses, label="MNIST Dataset", marker='x')
plt.title("Training Loss Over Epochs")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
output_path = "aggregated_training_loss.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"Wine Quality Dataset - Accuracy: {wine_acc:.4f}, F1-Score: {wine_f1:.4f}")
print(f"MNIST Dataset - Accuracy: {mnist_acc:.4f}, F1-Score: {mnist_f1:.4f}")
