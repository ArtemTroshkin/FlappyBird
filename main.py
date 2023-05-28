import sys
import time
import random

import pygame as pg

pg.init()
WIDTH, HEIGHT = 800, 600
FPS = 60

window = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

"""Добавление иконки и названия игры"""
pg.display.set_caption('Flappy bird')
pg.display.set_icon(pg.image.load(r'images/icon.png'))

"""Загрузка изображений"""
img_bg = pg.image.load(r'images/background.png')
img_bird = pg.image.load(r'images/bird.png')
img_pipe_top = pg.image.load(r'images/pipe_top.png')
img_pipe_bottom = pg.image.load(r'images/pipe_bottom.png')

"""Загрузка звука"""
pg.mixer.music.load(r'sounds/music.mp3')  # Музыка загружена, но не воспроизводится
pg.mixer.music.set_volume(0.1)  # Громкость музыки
pg.mixer.music.play(-1)  # Запуск звука -1 для зацикленности музыки

sound_fall = pg.mixer.Sound(r'sounds/fall.wav')

"""Механика персонажа"""
player_position_y, player_speed_y, player_acceleration_y = HEIGHT // 2, 0, 0
player = pg.Rect(WIDTH // 3, player_position_y, 34, 24)
frame = 0
state = 'start'

"""Загрузка шрифта"""
min_font = pg.font.Font(None, 35)
max_font = pg.font.Font(None, 80)

pipes = list()
backgrounds = list()
lives = 3
scores = 0
pipes_scores = list()

"""Скорость движения труб"""
pipe_speed = 3

"""Добавление первого фона перед циклом"""
backgrounds.append(pg.Rect(0, 0, 288, 600))

play = True
while play:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            play = False

    screen = window.get_rect()

    """Изменение номера кадра"""
    frame = (frame + 0.2) % 4

    """Перемещение труб"""
    for pipe in reversed(pipes):
        pipe.x -= pipe_speed  # Вместо 3 отнимаем значение pipe_speed

        """Уничтожение игры если труба вышла за экран"""
        if pipe.right < screen.left:
            pipes.remove(pipe)

    """Перемещение фона"""
    for bg in reversed(backgrounds):
        bg.x -= pipe_speed // 2  # Для перемещения фона обязательно целочисленное деление

        """Уничтожение игры если труба вышла за экран"""
        if bg.right < screen.left:
            backgrounds.remove(bg)

        if backgrounds[-1].right <= screen.right:
            backgrounds.append(pg.Rect(backgrounds[-1].right, 0, 288, 600))

    """Обработка нажатия на левую кнопку мыши"""
    press = pg.mouse.get_pressed()
    keys = pg.key.get_pressed()
    click = press[0] or keys[pg.K_SPACE]

    if click:
        player_acceleration_y = -2
    else:
        player_acceleration_y = 0

    """Работа с состояниями игры"""
    if state == 'start':
        if click:
            state = 'play'

        """Обновление положения, скорости и ускорения"""
        player_position_y += (
                HEIGHT // 2 - player_position_y)
        player.y = player_position_y
        player_speed_y = 0
        player_acceleration_y = 0

    elif state == 'play':
        """Механика падения"""
        player_position_y += player_speed_y
        player_speed_y = (player_speed_y + player_acceleration_y + 1) * 0.98

        player.y = player_position_y

        """Проверка списка труб"""
        if len(pipes) == 0 or pipes[-1].x < screen.width - 200:
            correction = random.randint(-60, 60)
            pipes.append(pg.Rect(screen.width, screen.top, 52, 200 + correction))
            pipes.append(pg.Rect(screen.width, screen.bottom - 200 + correction, 52, 200))

        """Отслеживание падения птички вверх, либо вниз"""
        if player.top <= screen.top or player.bottom >= screen.bottom:
            sound_fall.play()  # Проигрывание звука падения один раз
            state = 'fall'
            time.sleep(1)

        """Столкновение птички с трубами"""
        for pipe in pipes:
            if player.colliderect(pipe):
                sound_fall.play()  # Проигрывание звука падения один раз
                state = 'fall'
                pipes_scores.clear()
                scores = 0
                time.sleep(1)

            """Отслеживание перелета через трубу"""
            if pipe.right <= player.left and pipe not in pipes_scores:
                pipes_scores.append(pipe)
                scores += 5
                pipe_speed = 3 + scores // 100  # Каждые 100 очков к скорости будет прибавляться 1

    elif state == 'fall':
        pipes.clear()
        """Вычитание жизней"""
        lives -= 1
        if lives > 0:
            state = 'start'
        else:
            state = 'game over'

    else:  # Game Over
        play = False

    """Отрисовка"""
    # window.fill(pg.Color('black'))  # Нет необходимости закрашивать экран
    for bg in backgrounds:
        window.blit(img_bg, bg)

    """Отрисовка труб (обязательно перед игроком для того, чтобы при столкновении птица была на переднем фоне"""
    for pipe in pipes:
        """Отображение труб в виде картинки"""
        if pipe.y == 0:
            rect = img_pipe_top.get_rect(bottomleft=pipe.bottomleft)
            window.blit(img_pipe_top, rect)
        else:
            rect = img_pipe_bottom.get_rect(topleft=pipe.topleft)
            window.blit(img_pipe_bottom, rect)

    image = img_bird.subsurface(34 * int(frame), 0, 34, 24)

    """Наклон птички вверх и вниз"""
    image = pg.transform.rotate(image, -player_speed_y * 2)

    window.blit(image, player)

    """Отрисовка очков и жизней"""
    score_text = min_font.render(f'Очки: {scores}', True, pg.Color('black'))
    window.blit(score_text, (screen.left + 10, screen.top + 10))

    lives_text = min_font.render(f'Жизни: {lives}', True, pg.Color('black'))
    window.blit(lives_text, (screen.left + score_text.get_rect().width + 30, screen.top + 10))

    pg.display.update()
    clock.tick(FPS)

pg.quit()
