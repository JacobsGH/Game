class Settings:
    """
    Класс для хранения всех настроек игры.
    """

    def __init__(self):
        # Общие настройки
        self.screen_width = 1920
        self.screen_height = 928
        self.bg_color = (0, 0, 0)
        self.bg_speed = 0.1
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        # Корабль
        self.ship_speed = 2
        self.ship_limit = 5

        # Снаряды
        self.bullet_speed = 5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 10, 10)
        self.bullets_allowed = 5

        # Флот
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10

        self.init_dynamic_settings()

    def init_dynamic_settings(self):
        self.ship_speed_factor = 1.5
        self.bullet_speed_factor = 4.0
        self.alien_speed_factor = 1.0

        # Направление флота: 1 вправо, -1 влево.
        self.fleet_direction = 1

        self.alien_points = 50

    def inc_speed(self):
        """
        Увеличение скорости игры.
        """
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
