import random
import time

import pygame as pg


class FlappyBirdGame:
    def __init__(self):
        """Инициализация настроек игры"""
        pg.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60

        self.window = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pg.time.Clock()

        self.screen = self.window.get_rect()

        self.state = 'start'

        self.pipes = list()
        self.backgrounds = list()
        self.lives = 3
        self.scores = 0
        self.pipes_scores = list()

        """Скорость движения труб"""
        self.pipe_speed = 3

        """Добавление первого фона перед циклом"""
        self.backgrounds.append(pg.Rect(0, 0, 288, 600))

        self.play = True

        self._load_name_icon()
        self._load_images()
        self._load_sounds()
        self._bird_mechanic()
        self._load_fonts()

    def _load_name_icon(self):
        """Добавление иконки и названия игры"""
        pg.display.set_caption('Flappy bird')
        pg.display.set_icon(pg.image.load(r'images/icon.png'))

    def _load_images(self):
        """Загрузка изображений"""
        self.img_bg = pg.image.load(r'images/background.png')
        self.img_bird = pg.image.load(r'images/bird.png')
        self.img_pipe_top = pg.image.load(r'images/pipe_top.png')
        self.img_pipe_bottom = pg.image.load(r'images/pipe_bottom.png')

    def _load_sounds(self):
        """Загрузка звука"""
        pg.mixer.music.load(r'sounds/music.mp3')  # Музыка загружена, но не воспроизводится
        pg.mixer.music.set_volume(0.1)  # Громкость музыки
        pg.mixer.music.play(-1)  # Запуск звука -1 для зацикленности музыки

        self.sound_fall = pg.mixer.Sound(r'sounds/fall.wav')

    def _bird_mechanic(self):
        """Механика персонажа"""
        self.player_position_y, self.player_speed_y, self.player_acceleration_y = self.HEIGHT // 2, 0, 0
        self.player = pg.Rect(self.WIDTH // 3, self.player_position_y, 34, 24)
        self.frame = 0

    def _load_fonts(self):
        """Загрузка шрифта"""
        self.min_font = pg.font.Font(None, 35)
        self.max_font = pg.font.Font(None, 80)

    def _check_events(self):
        """Отслеживание событий"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.play = False

    def _frame_number_change(self):
        """Изменение номера кадра"""
        self.frame = (self.frame + 0.2) % 4

    def _move_pipes(self):
        """Перемещение труб"""
        for pipe in reversed(self.pipes):
            pipe.x -= self.pipe_speed  # Вместо 3 отнимаем значение pipe_speed

            """Уничтожение трубы если труба вышла за экран"""
            if pipe.right < self.screen.left:
                self.pipes.remove(pipe)

    def _move_background(self):
        """Перемещение фона"""
        for bg in reversed(self.backgrounds):
            bg.x -= self.pipe_speed // 2  # Для перемещения фона обязательно целочисленное деление

            """Уничтожение игры если труба вышла за экран"""
            if bg.right < self.screen.left:
                self.backgrounds.remove(bg)

            if self.backgrounds[-1].right <= self.screen.right:
                self.backgrounds.append(pg.Rect(self.backgrounds[-1].right, 0, 288, 600))

    def _move_bird(self):
        """Обработка нажатия на левую кнопку мыши и перемещение птички"""
        self.press = pg.mouse.get_pressed()
        self.keys = pg.key.get_pressed()
        self.click = self.press[0] or self.keys[pg.K_SPACE]

        if self.click:
            self.player_acceleration_y = -2
        else:
            self.player_acceleration_y = 0

    def _start_state(self):
        """Начало игры"""
        if self.click:
            self.state = 'play'

        """Обновление положения, скорости и ускорения"""
        self.player_position_y += (
                self.HEIGHT // 2 - self.player_position_y)
        self.player.y = self.player_position_y
        self.player_speed_y = 0
        self.player_acceleration_y = 0

    def _falling(self):
        """Механика падения"""
        self.player_position_y += self.player_speed_y
        self.player_speed_y = (self.player_speed_y + self.player_acceleration_y + 1) * 0.98

        self.player.y = self.player_position_y

    def _check_pipes(self):
        """Проверка списка труб"""
        if len(self.pipes) == 0 or self.pipes[-1].x < self.screen.width - 200:
            correction = random.randint(-60, 60)  # Рандомное положение труб
            """Заполнение списка труб для отрисовки"""
            self.pipes.append(pg.Rect(self.screen.width, self.screen.top, 52, 200 + correction))
            self.pipes.append(pg.Rect(self.screen.width, self.screen.bottom - 200 + correction, 52, 200))

    def _falling_bird(self):
        """Отслеживание падения птички вверх, либо вниз"""
        if self.player.top <= self.screen.top or self.player.bottom >= self.screen.bottom:
            self.sound_fall.play()  # Проигрывание звука падения один раз
            self.state = 'fall'
            time.sleep(1)

    def _bird_pipes_collision(self):
        """Столкновение птички с трубами"""
        for pipe in self.pipes:
            if self.player.colliderect(pipe):
                self.sound_fall.play()  # Проигрывание звука падения один раз
                self.state = 'fall'
                self.pipes_scores.clear()
                self.scores = 0
                time.sleep(1)

            """Отслеживание перелета через трубу"""
            if pipe.right <= self.player.left and pipe not in self.pipes_scores:
                self.pipes_scores.append(pipe)
                self.scores += 5
                self.pipe_speed = 3 + self.scores // 100  # Каждые 100 очков к скорости будет прибавляться 1

    def _play_state(self):
        """Игровое состояние"""
        self._falling()

        self._check_pipes()

        self._falling_bird()

        self._bird_pipes_collision()

    def _fall_state(self):
        """Проигрыш"""
        self.pipes.clear()
        """Вычитание жизней"""
        self.lives -= 1
        if self.lives > 0:
            self.state = 'start'
        else:
            self.state = 'game over'

    def _draw_background(self):
        """Отрисовка фона"""
        for bg in self.backgrounds:
            self.window.blit(self.img_bg, bg)

    def _draw_pipes(self):
        """Отрисовка труб"""
        for pipe in self.pipes:
            """Отображение труб в виде картинки"""
            if pipe.y == 0:
                rect = self.img_pipe_top.get_rect(bottomleft=pipe.bottomleft)
                self.window.blit(self.img_pipe_top, rect)
            else:
                rect = self.img_pipe_bottom.get_rect(topleft=pipe.topleft)
                self.window.blit(self.img_pipe_bottom, rect)

    def _draw_bird(self):
        """Отрисовка птички в определенном положении"""
        image = self.img_bird.subsurface(34 * int(self.frame), 0, 34, 24)

        """Наклон птички вверх и вниз"""
        image = pg.transform.rotate(image, -self.player_speed_y * 2)

        self.window.blit(image, self.player)

    def _draw_scores_lives(self):
        """Отрисовка очков и жизней"""
        score_text = self.min_font.render(f'Очки: {self.scores}', True, pg.Color('black'))
        self.window.blit(score_text, (self.screen.left + 10, self.screen.top + 10))

        lives_text = self.min_font.render(f'Жизни: {self.lives}', True, pg.Color('black'))
        self.window.blit(lives_text, (self.screen.left + score_text.get_rect().width + 30, self.screen.top + 10))

        pg.display.update()
        self.clock.tick(self.FPS)

    def run_game(self):
        """Запуск основного цикла игры"""
        while self.play:
            self._check_events()

            self._frame_number_change()

            self._move_pipes()

            self._move_background()

            self._move_bird()

            """Работа с состояниями игры"""
            if self.state == 'start':
                self._start_state()

            elif self.state == 'play':
                self._play_state()

            elif self.state == 'fall':
                self._fall_state()

            else:  # Game Over
                self.play = False

            self._draw_background()

            self._draw_pipes()

            self._draw_bird()

            self._draw_scores_lives()


if __name__ == '__main__':
    game = FlappyBirdGame()
    game.run_game()
