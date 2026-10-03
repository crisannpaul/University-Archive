import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score

def process_wine_quality():
    df = pd.read_csv('winequality.csv', sep=';')

    X = df.drop('quality', axis=1).values
    y = df['quality'].values - df['quality'].min()

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test

def train_and_evaluate_gb():
    X_train, X_test, y_train, y_test = process_wine_quality()

    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f"Gradient Boosting Model - Accuracy: {acc:.4f}, F1-Score: {f1:.4f}")

train_and_evaluate_gb()
