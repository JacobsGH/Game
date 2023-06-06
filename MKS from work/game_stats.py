from os.path import exists


class GameStats:
    """
    Отслеживание статистики
    """
    HIGH_SCORE_FILE = "high_score.txt"

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        self.score = 0

        # Рекорд не сбрасывается.
        self.high_score = 0
        self.load_high_score()

        self.game_active = False

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def save_high_score(self):
        """
        Сохраняет рекорд.
        """
        with open(GameStats.HIGH_SCORE_FILE, "w+") as high_score_file:
            high_score_file.write(str(self.high_score))

    def load_high_score(self):
        """
        Подгружает рекорд из файла.
        """
        if exists(GameStats.HIGH_SCORE_FILE):
            with open(GameStats.HIGH_SCORE_FILE, "r") as high_score_file:
                self.high_score = int(high_score_file.read()) or 0
        else:
            self.high_score = 0

