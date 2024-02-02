from pygame.math import Vector2
import pygame
import math


# _____Функция, которая выводит текст (например: кол-во денег, жизней)_____
def texting(screen, text, font, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


# _____Класс отвечающий за вывод финального экрана_____
class screen_slide:
    # _____Здесь мы выгружаем картинку и отрсовываем ее плавно на экран_____
    def __init__(self, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (1080, 720))

        self.x, self.y = 0, -720

    def draw(self, screen):
        if self.y != 0:
            self.y += 10
        screen.blit(self.image, (self.x, self.y))


# _____Класс, отвечающий за кнопки (покупки, начала раунда и т.д.)_____
class Buttons:
    def __init__(self, x, y, name, click):
        if name == "start_button.png":
            self.image = pygame.transform.scale(pygame.image.load(name), (210, 80))
        else:
            self.image = pygame.image.load(name)

        self.x, self.y = x, y

        self.clicked = False
        self.one = click

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    # _____В функции проверяем если нажата кнопка и соответсвенно отрисовка_____
    def draw(self, screen):
        check = False
        position = pygame.mouse.get_pos()

        if (
            self.rect.collidepoint(position)
            and pygame.mouse.get_pressed()[0] == 1
            and self.clicked is False
        ):
            if self.one:
                self.clicked = True
            check = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return check


# _____В этом классе у нас идет отрисовка и анимация башен_____
# _____В нем выполняется функция наведения и улучшения башни_____
class Tower(pygame.sprite.Sprite):
    image = [
        pygame.image.load("turret_animation_level_1.png"),
        pygame.image.load("turret_animation_level_2.png"),
        pygame.image.load("turret_animation_level_3.png"),
    ]

    def __init__(self, x, y):
        super().__init__(tower_group)
        self.level = 1
        self.frames = [Tower.image[0], Tower.image[1], Tower.image[2]]

        self.x, self.y = (x + 0.5) * 48, (y + 0.5) * 48
        self.time = pygame.time.get_ticks()

        self.selected = False
        self.target = None

        self.wait_shot = upgrades[self.level][1]
        self.reload = pygame.time.get_ticks()
        self.range = upgrades[self.level][0]

        self.animation = self.load_frames(self.frames[self.level - 1])
        self.number = 0

        self.angle = 90
        self.animation_image = self.animation[self.number]

        self.image = pygame.transform.rotate(self.animation_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        self.circle_range = pygame.Surface((self.range * 2, self.range * 2))
        self.circle_range.fill((0, 0, 0))
        self.circle_range.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            self.circle_range, (220, 220, 220), (self.range, self.range), self.range
        )
        self.circle_range.set_alpha(65)

        self.circle_rect = self.circle_range.get_rect()
        self.circle_rect.center = self.rect.center

    def update(self, enemies):
        if self.target:
            self.animation_tower()
        else:
            if pygame.time.get_ticks() - self.reload > self.wait_shot:
                self.target_enemies(enemies)

    def load_frames(self, image):
        frames = 8
        s = []

        pixels = image.get_height()
        for i in range(frames):
            animated = image.subsurface(i * pixels, 0, pixels, pixels)
            s.append(animated)
        return s

    def animation_tower(self):
        self.animation_image = self.animation[self.number]
        if pygame.time.get_ticks() - self.time > 50:
            self.time = pygame.time.get_ticks()
            self.number += 1
            if self.number == 8:
                self.number = 0
                self.reload = pygame.time.get_ticks()
                self.target = None

    def draw(self, screen):
        self.image = pygame.transform.rotate(self.animation_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        screen.blit(self.image, self.rect)
        if self.selected:
            screen.blit(self.circle_range, self.circle_rect)

    def target_enemies(self, enemies):
        x, y = 0, 0
        for i in enemies:
            if i.health > 0:
                x = i.position[0] - self.x
                y = i.position[1] - self.y
                distance_to_target = math.sqrt(x**2 + y**2)
                if distance_to_target < self.range:
                    self.target = i
                    self.angle = math.degrees(math.atan2(-y, x))
                    self.target.health -= damage
                    break

    def upgrade(self):
        self.level += 1

        self.wait_shot = upgrades[self.level][1]
        self.range = upgrades[self.level][0]

        self.animation = self.load_frames(self.frames[self.level - 1])
        self.animation_image = self.animation[self.number]

        self.circle_range = pygame.Surface((self.range * 2, self.range * 2))
        self.circle_range.fill((0, 0, 0))
        self.circle_range.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            self.circle_range, (220, 220, 220), (self.range, self.range), self.range
        )
        self.circle_range.set_alpha(65)

        self.circle_rect = self.circle_range.get_rect()
        self.circle_rect.center = self.rect.center


# _____Класc отвечает за спавн врагов и берет инвормацию из словарей_____
class Enemy(pygame.sprite.Sprite):
    image = [
        pygame.image.load("enemy_easy.png"),
        pygame.image.load("enemy_medium.png"),
        pygame.image.load("enemy_hard.png"),
    ]

    def __init__(self, points, type):
        super().__init__(enemy_group)
        self.type = type

        self.points = points
        self.position = Vector2(self.points[0])

        self.angle = 0
        self.number = 1

        self.speed = enemies_information[self.type + 1][1]
        self.health = enemies_information[self.type + 1][0]

        self.image = Enemy.image[self.type]
        self.rotate_image = self.image

        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self, information):
        self.move(information)
        self.rotate()
        self.check_health(information)

    def move(self, information):
        if self.number < len(self.points):
            self.target = Vector2(self.points[self.number])
            self.moving = self.target - self.position
        else:
            information.health -= 1
            information.missed += 1
            self.kill()

        if self.moving.length() >= self.speed:
            self.position += self.moving.normalize() * self.speed
        else:
            self.number += 1

    def rotate(self):
        self.angle = math.degrees(
            math.atan2(
                -(self.target - self.position)[1], (self.target - self.position)[0]
            )
        )

        self.image = pygame.transform.rotate(self.rotate_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def check_health(self, information):
        if self.health <= 0:
            information.money += 5
            information.killed += 1

            information.final_kills += 1
            self.kill()


# _____Класс, отвечающий за основные перемнны игры_____
class Mechanics:
    def __init__(self, health, money):
        self.health = health
        self.money = money

        self.killed = 0
        self.missed = 0

        self.final_level = 0
        self.final_upgrades = 0
        self.final_towers = 0
        self.final_kills = 0


pygame.init()
pygame.display.set_caption("Tower Defense")

size = 1080, 720
screen = pygame.display.set_mode(size)

# _____Настройка фреймов_____
clock = pygame.time.Clock()
fps = 120

# _____Открытие файла txt_____
file = open("database.txt", "r", encoding="utf8")
count = 1
for i in file.readlines():
    count += 1
file = open("database.txt", "a", encoding="utf8")


# _____Важные списки_____
points = [
    (625, 0),
    (625, 190),
    (480, 190),
    (480, 95),
    (95, 95),
    (95, 480),
    (240, 480),
    (240, 290),
    (385, 290),
    (385, 335),
    (670, 335),
    (670, 625),
    (530, 625),
    (530, 480),
    (385, 480),
    (385, 625),
    (0, 625),
]

grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0],
    [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 0],
    [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 0],
    [0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0],
    [0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0],
    [0, 2, 2, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0],
    [0, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2],
    [0, 2, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2],
    [0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2],
    [0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 0, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

# _____Словари с информацией о механиках_____
upgrades = {1: [100, 1200], 2: [160, 950], 3: [200, 650]}

enemies_information = {1: [10, 1.5], 2: [15, 2.5], 3: [30, 4]}

levels = {
    1: [15, 0, 0],
    2: [30, 0, 0],
    3: [20, 5, 0],
    4: [30, 15, 0],
    5: [5, 20, 0],
    6: [15, 10, 5],
    7: [20, 25, 5],
    8: [10, 20, 15],
    9: [15, 10, 5],
    10: [1, 99, 1],
    11: [25, 25, 5],
    12: [100, 0, 15],
    13: [20, 20, 20],
    14: [60, 25, 10],
    15: [60, 100, 45],
}

# _____Создание групп со спрайтами_____
enemy_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()

# _____Тип переменных: bool_____
writing = True
level_started = False
selected_tower = None
buying = False
game_over = False
game = False

# _____Переменные, связанные с созданием врагов_____
last_spawn = pygame.time.get_ticks()
spawn_cooldown = 950
spawned = 0

# _____Переменные, отвечающие за уровень, победу_____
game_number = count
game_outcome = 0
level = 1

# _____Переменные, отвечающие за цены_____
buy_price = 125
upgrade_price = 200
showing_price = buy_price

# _____Спрайты кнопок_____
buy_button = Buttons(750, 315, "buy_button.png", True)
cancel_button = Buttons(750, 370, "cancel_button.png", True)
upgrade_button = Buttons(750, 370, "upgrade_button.png", True)
begin_button = Buttons(750, 640, "begin_button.png", True)
restart_button = Buttons(860, 630, "restart_button.png", True)
start_button = Buttons(865, 635, "start_button.png", True)

# _____Спрайты экранов_____
background = pygame.image.load("map.png")
game_over_screen = pygame.image.load("game_over.jpg")
win_screen = pygame.image.load("win.jpg")

# _____Спрайты текстов_____
text1 = pygame.font.SysFont("Consolas", 24, bold=True)
text2 = pygame.font.SysFont("Consolas", 36, bold=True)

# _____Остальное_____
logo = pygame.transform.scale(pygame.image.load("logotype.png"), (720, 720))
upgrade = pygame.transform.scale(pygame.image.load("upgrade.png"), (25, 25))
heart = pygame.transform.scale(pygame.image.load("heart.png"), (50, 50))
coin = pygame.transform.scale(pygame.image.load("coin.png"), (100, 62.5))
shop_coin = pygame.transform.scale(pygame.image.load("coin.png"), (60, 37.5))
shop_tower = pygame.transform.scale(pygame.image.load("tower.png"), (120, 120))

# _____Создание списка с информацией о врагах_____
spawning = []
enemies = levels[level]
for i in enemies:
    for j in range(i):
        spawning.append(enemies.index(i))

# _____Объекты классов_____
game_over_final_screen = screen_slide(game_over_screen)
win_final_screen = screen_slide(win_screen)

# _____Переменные, отвечающие за внутриигровые механики_____
information = Mechanics(25, 650)
damage = 5

running = True
while running:
    screen.fill((105, 5, 55))
    screen.blit(logo, (0, 0))
    texting(screen, "Проект реализован:", text1, (255, 255, 255), 730, 5)
    texting(screen, "Алессандро Каванья", text1, (0, 205, 0), 730, 60)
    texting(screen, "Арина Макарова", text1, (0, 205, 0), 730, 80)

    if start_button.draw(screen):
        game = True

    if game:
        screen.fill((105, 5, 55))

        # _____Отрисовка спрайтов_____
        screen.blit(background, (0, 0))
        screen.blit(shop_tower, (765, 190))
        screen.blit(shop_coin, (790, 145))
        screen.blit(heart, (730, 5))
        screen.blit(coin, (707, 45))
        texting(screen, str(information.health), text2, (255, 255, 255), 785, 13)
        texting(screen, str(information.money), text2, (255, 255, 255), 785, 60)
        texting(screen, f"LEVEL: {level}", text1, (0, 205, 0), 955, 5)
        texting(screen, str(showing_price), text1, (255, 255, 255), 762, 153)
        texting(screen, f"#0-game-0{game_number}", text1, (0, 205, 0), 753, 610)

        # _____Отрисовка других элементов_____
        pygame.draw.rect(screen, (255, 255, 255), (764, 185, 120, 120), 5)

        # _____Проверка на проигрыш_____
        if game_over is False:
            if information.health <= 0:
                game_over = True
                game_outcome = -1
            if level == 16:
                game_over = True
                game_outcome = 1

            if game_outcome == 0:
                # _____Обновления спрайтов_____
                enemy_group.update(information)
                tower_group.update(enemy_group)

                # _____Отрисовка многочисленных спрайтов_____
                enemy_group.draw(screen)
                for i in tower_group:
                    i.draw(screen)

                # _____Появление противников_____
                if level_started is False:
                    if begin_button.draw(screen):
                        level_started = True
                else:
                    if pygame.time.get_ticks() - last_spawn > spawn_cooldown:
                        if spawned < len(spawning):
                            type = spawning[spawned]
                            enemy = Enemy(points, type)
                            last_spawn = pygame.time.get_ticks()
                            spawned += 1

                # _____Проверка нового уровня, ресет переменных_____
                if information.killed + information.missed == len(spawning):
                    level_started = False
                    last_spawn = pygame.time.get_ticks()

                    information.money += 75
                    information.killed = 0
                    information.missed = 0
                    spawned = 0

                    spawning = []
                    enemies = levels[level]
                    for i in enemies:
                        for j in range(i):
                            spawning.append(enemies.index(i))

                    level += 1

                # _____Проверка на покупку_____
                if buy_button.draw(screen) and information.money >= buy_price:
                    buying = True

                # _____Отмена покупки_____
                if buying:
                    if (
                        0 <= pygame.mouse.get_pos()[0] <= 720
                        and 0 <= pygame.mouse.get_pos()[1] <= 720
                    ):
                        cursor = shop_tower.get_rect()
                        cursor.center = pygame.mouse.get_pos()

                        screen.blit(shop_tower, cursor)
                    if cancel_button.draw(screen):
                        buying = False

                # _____Проверка башни, показывает ренджу_____
                if selected_tower:
                    selected_tower.selected = True

                # _____Улучшение башни_____
                if selected_tower:
                    if selected_tower.level < 3 and information.money >= upgrade_price:
                        showing_price = upgrade_price
                        screen.blit(upgrade, (835, 202))
                        if upgrade_button.draw(screen):
                            selected_tower.upgrade()
                            information.money -= upgrade_price
                            information.final_upgrades += 1
                    if selected_tower.level == 3:
                        showing_price = buy_price
                else:
                    showing_price = buy_price
        else:
            information.final_level = level
            if game_outcome == -1:
                game_over_final_screen.draw(screen)
            if game_outcome == 1:
                win_final_screen.draw(screen)
                information.final_level = information.final_level - 1
            if game_over_final_screen.y == 0 or win_final_screen.y == 0:
                texting(
                    screen,
                    f"LEVEL: {information.final_level}",
                    text2,
                    (255, 255, 255),
                    280,
                    440,
                )
                texting(
                    screen,
                    f"KILLS: {information.final_kills}",
                    text2,
                    (255, 255, 255),
                    280,
                    480,
                )
                texting(
                    screen,
                    f"TOWERS: {information.final_towers}",
                    text2,
                    (255, 255, 255),
                    280,
                    520,
                )
                texting(
                    screen,
                    f"UPGRADES: {information.final_upgrades}",
                    text2,
                    (255, 255, 255),
                    280,
                    560,
                )

                score_one = information.final_kills * information.final_level
                score_two = information.final_towers + information.final_upgrades
                final_score = score_one * score_two
                texting(
                    screen,
                    f"FINAL SCORE: {final_score}",
                    text2,
                    (200, 20, 20),
                    280,
                    640,
                )

                total = (
                    f"result = {game_outcome};"
                    f"level = {information.final_level};"
                    f"kills = {information.final_kills};"
                    f"towers = {information.final_towers};"
                    f"upgrades = {information.final_upgrades};"
                    f"final_score = {final_score}.\n"
                )

                if writing:
                    file.write(total)
                    writing = False

                if restart_button.draw(screen):
                    # _____Обозначаем заново переменные_____
                    grid = [
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0],
                        [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 0],
                        [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 0],
                        [0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0],
                        [0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0],
                        [0, 2, 2, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0],
                        [0, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                        [0, 2, 2, 0, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2],
                        [0, 2, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2, 2],
                        [0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2],
                        [0, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2],
                        [0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 0, 2, 2],
                        [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2],
                        [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    ]

                    enemy_group = pygame.sprite.Group()
                    tower_group = pygame.sprite.Group()

                    writing = True
                    level_started = False
                    selected_tower = None
                    buying = False
                    game_over = False

                    last_spawn = pygame.time.get_ticks()
                    spawn_cooldown = 600
                    spawned = 0

                    game_outcome = 0
                    level = 1

                    spawning = []
                    enemies = levels[level]
                    for i in enemies:
                        for j in range(i):
                            spawning.append(enemies.index(i))

                    information = Mechanics(25, 650)

                    game_over_final_screen = screen_slide(game_over_screen)
                    win_final_screen = screen_slide(win_screen)

                    file = open("database.txt", "r", encoding="utf8")
                    count = 1
                    for i in file.readlines():
                        count += 1
                    file = open("database.txt", "a", encoding="utf8")

                    game_number += count

    # _____События_____
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            position = event.pos

            # _____Если клик именно на карте_____
            if position[0] <= 720 and position[1] <= 720:
                selected_tower = None
                for i in tower_group:
                    i.selected = False
                # _____Покупка_____
                if grid[position[1] // 48][position[0] // 48] == 0 and buying:
                    buying = False
                    grid[position[1] // 48][position[0] // 48] = 1
                    tower = Tower(position[0] // 48, position[1] // 48)
                    information.final_towers += 1
                    information.money -= buy_price
                elif grid[position[1] // 48][position[0] // 48] == 1 and not buying:
                    for i in tower_group:
                        if (
                            i.x == (position[0] // 48 + 0.5) * 48
                            and i.y == (position[1] // 48 + 0.5) * 48
                        ):
                            selected_tower = i
                else:
                    selected_tower = None

    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
