import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. Încărcarea și procesarea datelor de extrageri ---
draws = pd.read_csv('RawDataset.csv')
draws['Data tragerii'] = pd.to_datetime(draws['Data tragerii'], dayfirst=True, errors='coerce')
draws = draws.sort_values(by='Data tragerii')
draws['Suma'] = draws[['Nr.1', 'Nr.2', 'Nr.3', 'Nr.4', 'Nr.5', 'Nr.6']].sum(axis=1)

# --- 2. Încărcarea și procesarea datelor de câștiguri ---
wins = pd.read_csv('wins.csv')
wins['Date'] = pd.to_datetime(wins['Date'], dayfirst=True, errors='coerce')
wins = wins.sort_values(by='Date')

# Convertim coloana 'Prize' la float (înlocuind virgula cu punct, dacă este cazul)
wins['Prize'] = wins['Prize'].astype(str).str.replace(',', '.').astype(float)
max_prize = wins['Prize'].max()
# Stabilim mărimea maximă a punctelor (poți ajusta factorul de scalare, aici 300)
scatter_sizes = wins['Prize'] / max_prize * 300

# --- 3. Funcție pentru calculul mediei ultimelor n extrageri anterioare unui câștig ---
def avg_sum_before_win(win_date, draws_df, n):
    prev_draws = draws_df[draws_df['Data tragerii'] < win_date].tail(n)
    if len(prev_draws) < n:
        return None
    return prev_draws['Suma'].mean()

# --- 4. Generarea graficelor pentru fiecare moving average de la 2 la 10 ---
for window in range(2, 20):
    # Calculăm moving average-ul pentru setul de extrageri folosind fereastra curentă
    ma_values = draws['Suma'].rolling(window=window).mean()

    # Calculăm pentru fiecare câștig media sumei pe ultimele n extrageri (folosind același window)
    wins_ma_before = wins['Date'].apply(lambda d: avg_sum_before_win(d, draws, n=window))
    
    # Creăm figura și axele
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plotăm linia cu moving average-ul
    ax1.plot(draws['Data tragerii'], ma_values, label=f'MA{window} (moving average)', linewidth=2, color='blue')
    
    # Plotăm punctele roșii pentru câștiguri; dimensiunea punctului este proporțională cu Prize
    ax1.scatter(wins['Date'], wins_ma_before, color='red', label='Win events', s=scatter_sizes, zorder=5)
    
    # Configurăm axele și etichetele
    ax1.set_xlabel('Date')
    ax1.set_ylabel(f'MA{window} (Suma numerelor)')
    ax1.grid(True)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    ax1.legend(loc='best')
    plt.title(f'Moving Average (window = {window}) and Win Events')
    
    # Salvăm graficul într-un fișier
    plt.tight_layout()
    plt.savefig(f'moving_average/plot_MA{window}.png')
    plt.close(fig)
