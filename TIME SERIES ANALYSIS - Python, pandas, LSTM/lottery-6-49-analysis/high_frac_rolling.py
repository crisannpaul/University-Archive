import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Prepare output folder
output_dir = os.path.join('plots', 'high_frac')
os.makedirs(output_dir, exist_ok=True)

# 2. Load & clean draws
draws = pd.read_csv('RawDataset.csv')
draws['Date'] = pd.to_datetime(
    draws['Data tragerii'].str.strip(),
    format='%Y-%m-%d', errors='coerce'
)
draws = draws.sort_values('Date')
cols = ['Nr.1','Nr.2','Nr.3','Nr.4','Nr.5','Nr.6']
draws['HighFrac'] = draws[cols].gt(31).mean(axis=1)

# 3. Load & clean wins (keep Prize)
wins = pd.read_csv('wins.csv')
wins['Date'] = pd.to_datetime(
    wins['Date'].str.strip(),
    format='%d.%m.%y', errors='coerce'
)
wins['Prize'] = wins['Prize'].astype(str).str.replace(',','.').astype(float)
wins = wins.sort_values('Date')

# 4. Determine first win date & trim
first_win = wins['Date'].iloc[0]
draws = draws[draws['Date'] >= first_win].reset_index(drop=True)
wins   = wins[wins['Date'] >= first_win].reset_index(drop=True)

# recompute HighFrac if you like (not strictly necessary)
# draws['HighFrac'] already computed above

# 5. Precompute global max prize for sizing
max_prize = wins['Prize'].max()
size_scale = 200

# 6. For each rolling window 5…20, compute and plot
for window in range(5, 21):
    ma_col = f'HighFrac_MA{window}'
    draws[ma_col] = draws['HighFrac'].rolling(window).mean()
    
    # align each win to its last rolling‐mean value
    draws_sorted = draws[['Date', ma_col]].sort_values('Date')
    wins_sorted  = wins[['Date','Prize']].sort_values('Date')
    wins_with_ma = pd.merge_asof(
        wins_sorted,
        draws_sorted,
        on='Date',
        direction='backward'
    )
    # size by prize
    wins_with_ma['Size'] = wins_with_ma['Prize'] / max_prize * size_scale

    # plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(
        draws['Date'], draws[ma_col],
        label=f'Rolling {window}-draw avg frac >31',
        color='blue'
    )
    ax.scatter(
        wins_with_ma['Date'], wins_with_ma[ma_col],
        s=wins_with_ma['Size'],
        color='red', edgecolor='k', alpha=0.7,
        label='Wins (size ∝ prize)'
    )

    ax.set_title(f'Window={window}: High-Number Fraction from First Win Onward')
    ax.set_xlabel('Date')
    ax.set_ylabel('Fraction >31')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize='small')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    plt.tight_layout()

    # save
    fname = f'high_frac_MA{window}_from_first_win.png'
    path = os.path.join(output_dir, fname)
    plt.savefig(path, dpi=300)
    plt.close(fig)
    print(f'Saved window {window} plot to {path}')
