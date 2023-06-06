import pygame
from pygame.sprite import Sprite


class Bang(Sprite):
    """
    Класс представляющий взрыв пришельца.
    """

    def __init__(self, ai_game, centerx, centery):
        """
        Инициализирует пришельца и задает его начальную позицию.
        """
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Звук взрыва
        self.bang_sound = pygame.mixer.Sound('sounds/bang.mp3')
        self.bang_sound.play()

        # Загрузка изображения взрыва.
        self.image = pygame.image.load('images/bang.png')
        self.rect = self.image.get_rect()

        # Каждый взрыв появляется на месте пришельца.
        self.rect.centerx = centerx
        self.rect.centery = centery

        # Засекаем время создания взрыва.
        self.start_time = pygame.time.get_ticks()

        # Сохранение точной горизонтальной позиции пришельца.
        self.x = float(self.rect.x)

    def update(self):
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x
