from dataclasses import dataclass, asdict


class Player(object):
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@dataclass
class PlayerDAO:
    id: int = 1
    username: str = ""
    email: str = ""
    password: str = ""
    total_score: int = 0
    role: str = "PLAYER"

    def __init__(self, player: Player):
        self.username = player.username
        self.email = player.email
        self.password = player.password
