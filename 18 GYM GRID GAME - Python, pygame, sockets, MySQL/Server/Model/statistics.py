import matplotlib.pyplot as plt


class Statistics:
    @staticmethod
    def get_scores_by_player_and_level(games):
        scores_by_player = {}

        for game in games:
            player_id = game[1]
            level = game[2]
            score = game[3]

            if player_id not in scores_by_player:
                scores_by_player[player_id] = {0: None, 1: None, 2: None}

            scores_by_player[player_id][level] = score

        return scores_by_player

    @staticmethod
    def plot_score_distribution_by_player(games):
        scores_by_player = Statistics.get_scores_by_player_and_level(games)
        levels = None

        for player_id, scores in scores_by_player.items():
            levels = sorted(list(scores.keys()))
            scores_list = [scores[level] for level in levels]
            plt.plot(levels, scores_list, marker='o', label=f'Player {player_id}')

        plt.xlabel('Levels')
        plt.ylabel('Score')
        plt.title('Score Distribution by Player and Level')
        plt.xticks(levels)
        plt.legend()
        plt.show()
