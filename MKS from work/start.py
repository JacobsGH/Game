import sys
import pygame
from time import sleep

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard
from bang import Bang


class AlienInvasion:
    """
    Класс для управления ресурсами
    """

    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Звук
        self.bg_sound = pygame.mixer.Sound('sounds/bg.mp3')

        # Управление фоном
        self.background = pygame.image.load('images/space-long.jpg')
        self.background_rect = self.background.get_rect()
        self.background_y = -self.background_rect.height // 2
        self.screen.blit(self.background, (0, int(self.background_y)))

        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Симулятор МКС")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bangs = pygame.sprite.Group()

        self._create_fleet()

        # Создание кнопки Play
        self.play_button = Button(self, "Сыграть")

    def run_game(self):
        """
        Запуск основного цикла игры.
        """

        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_background()
                self._update_bullets()
                self._update_aliens()
                self._check_bangs()
                self._update_bangs()

            self._update_screen()

    def _check_events(self):
        """
        Обрабатывает нажатия клавиш и события мыши.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        """
        Реагирует на нажатие клавиш.
        """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """
        Реагирует н отпускание клавиш.
        """
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key in (pygame.K_q, pygame.K_ESCAPE):
            sys.exit()
        elif event.key == pygame.K_p:
            self._start_game()

    def _update_bullets(self):
        self.bullets.update()

        # Удаление снарядов, вышедших за край экрана.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """
        Обработка коллизий снарядов с пришельцами.
        """
        # Проверка попаданий в пришельцев.
        # При обнаружении попадания удалить снаряд и пришельца.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

                for alien in aliens:
                    self._create_bang(alien)

            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Уничтожение существующих снарядов и создание нового флота.
            self.bullets.empty()
            self._create_fleet()
            # Увеличиваем скорость игры.
            self.settings.inc_speed()

            # Увеличиваем уровень.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        Обновляет позиции всех пришельцев во флоте.
        Включая проверку достижения пришельцами края экрана.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизии пришелец-корабль
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверка достиг ли флот нижнего края экрана
        self._check_aliens_bottom()

    def _update_bangs(self):
        """
        Обновляет позиции взрывов с учетом движения флота.
        """
        self.bangs.update()

    def _check_bangs(self):
        """
        Проверяет взрывы.
        """
        current_time = pygame.time.get_ticks()

        for bang in self.bangs:
            if current_time - bang.start_time > 300:
                self.bangs.remove(bang)

    def _update_screen(self):
        """
        Обновляет изображения на экране и отображает новый экран.
        """

        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)
        self.bangs.draw(self.screen)
        self.sb.show_score()

        # Показываем кнопку Play, если игра неактивна.
        if not self.stats.game_active:
            pygame.mouse.set_visible(True)
            self.play_button.draw_button()

        # Отображение последнего прорисованного экрана.
        pygame.display.flip()

    def _update_background(self):
        """
        Обновляет космическое небо.
        """

        self.background_y += self.settings.bg_speed
        if self.background_y > 0:
            self.background_y = -self.background_rect.height // 2
            self._ship_hit()
            

        self.screen.blit(self.background, (0, int(self.background_y)))
        

    def _fire_bullet(self):
        """
        Создание нового снаряда и включение его в группу bullets.
        """
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """
        Создает флот вторжения.
        """
        # Создание пришельца и вычисление количества пришельцев в ряду.
        # Интервал между соседними пришельцами равен ширине пришельца.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (3 * alien_width)
        number_aliens_x = available_space_x // (3 * alien_width)

        # Определяем количество рядов, которые помещаются на экране
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (6 * alien_height)

        # Создание флота вторжения
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """
        Создание пришельца и размещение его в ряду.
        """
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = 4 * alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _create_bang(self, alien):
        """
        Создает взрыв на месте пришельца.
        """
        bang = Bang(self, alien.rect.centerx, alien.rect.centery)
        self.bangs.add(bang)

        # TODO: нужен звук

    def _check_fleet_edges(self):
        """
        Реагирует на достижение пришельцем края экрана.
        """
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottom(self):
        """
        Проверяет, добрались ли пришельцы до нижнего края экрана.
        """
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        """
        Опускает весь флот и меняет направление флота.
        """
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """
        Обрабатывает столкновение корабля с пришельцем.
        """
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Очистка пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещение корабля в центре.
            self._create_fleet()
            self.ship.center_ship()

            # Пауза
            sleep(0.3)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(False)

    def _start_game(self):
        """
        Запуск игры.
        """
        # Сброс игровой статистики
        self.stats.reset_stats()
        self.settings.init_dynamic_settings()
        self.stats.game_active = True

        # Очистка пришельцев и снарядов.
        self.aliens.empty()
        self.bullets.empty()

        # Создание нового флота и размещение корабля в центре
        self._create_fleet()
        self.ship.center_ship()

        # Скрываем указатель мыши
        pygame.mouse.set_visible(False)

        # Выводим уровень
        self.sb.prep_level()
        self.sb.prep_score()
        self.sb.prep_high_score()
        self.sb.prep_ships()

        self.bg_sound.play()
        self.bg_sound.set_volume(0.6)

    def _check_play_button(self, mouse_pos):
        """
        Запускает новую игру при нажатии на кнопку Play.
        """
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_game()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
