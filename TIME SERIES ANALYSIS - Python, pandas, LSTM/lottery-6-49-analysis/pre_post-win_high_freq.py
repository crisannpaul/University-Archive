import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. Create output folder for pre-post highfrac plots
output_dir = os.path.join('plots', 'pre_post_highfrac')
os.makedirs(output_dir, exist_ok=True)

# 2. Locate and load draws data
draws_path = 'RawDataset.csv'
if not os.path.exists(draws_path):
    print(f"Error: '{draws_path}' not found. Please place your RawDataset.csv in the working directory.")
else:
    draws = pd.read_csv(draws_path)
    draws['Date'] = pd.to_datetime(
        draws['Data tragerii'].str.strip(),
        format='%Y-%m-%d', errors='coerce'
    )
    draws = draws.sort_values('Date').reset_index(drop=True)
    cols = ['Nr.1','Nr.2','Nr.3','Nr.4','Nr.5','Nr.6']
    draws['HighFrac'] = draws[cols].gt(31).mean(axis=1)

    # 3. Locate and load wins data
    wins_path = 'wins.csv'
    if not os.path.exists(wins_path):
        print(f"Error: '{wins_path}' not found. Please place your wins.csv in the working directory.")
    else:
        wins = pd.read_csv(wins_path)
        wins['Date'] = pd.to_datetime(
            wins['Date'].str.strip(),
            format='%d.%m.%y', errors='coerce'
        )
        wins = wins.sort_values('Date').reset_index(drop=True)

        # 4. For each window size from 5 to 15, compute pre/post means and plot
        for window in range(5, 16):
            pre_means = []
            post_means = []

            for win_date in wins['Date']:
                idx_list = draws.index[draws['Date'] == win_date].tolist()
                if not idx_list:
                    continue
                i = idx_list[0]
                if i >= window and i + window < len(draws):
                    pre_means.append(draws.loc[i-window:i-1, 'HighFrac'].mean())
                    post_means.append(draws.loc[i+1:i+window, 'HighFrac'].mean())

            if not pre_means or not post_means:
                print(f"Not enough data for window={window}, skipping.")
                continue

            cmp = pd.DataFrame({
                'Period': ['Pre-win'] * len(pre_means) + ['Post-win'] * len(post_means),
                'HighFrac': pre_means + post_means
            })

            plt.figure(figsize=(6,4))
            cmp.boxplot(by='Period', column='HighFrac')
            plt.suptitle('')
            plt.title(f'HighFrac: {window} draws before vs after wins')
            plt.ylabel('Fraction of numbers > 31')
            plt.tight_layout()

            fname = f'pre_post_highfrac_window_{window}.png'
            path = os.path.join(output_dir, fname)
            plt.savefig(path, dpi=300)
            plt.close()

        print(f'Plots saved for windows 5 to 15 in: {output_dir}')
