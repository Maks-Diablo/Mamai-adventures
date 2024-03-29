import configparser
import random

import pygame


class Aleksis_bot():
    def __init__(self, x, y, flip, data, sprite_sheet, animation_steps):
        self.size_w = data[0]
        self.size_h = data[1]
        self.image_scale = data[2]
        self.offset = data[3]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 184, 150))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.run_cooldown = 0
        self.hit = False
        self.health = 30
        self.alive = True
        self.health_damage = 10

        # проверка уровня
        self.level = 0  # 0 - игра, 1 - пройден

        # проверка удара
        self.attack_run = False
        self.ultra_attack = 0

        # проверка звука
        self.sound_punch = False

    def load_images(self, sprite_sheet, animation_steps):
        # extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size_w, y * self.size_h, self.size_w, self.size_h)
                temp_img_list.append(
                    pygame.transform.scale(temp_img, (self.size_w * self.image_scale, self.size_w * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, ultra):
        SPEED = 5
        GRAVITY = 2
        dx = 0
        dy = 0
        self.rect_fighter = target.rect
        self.alive_fighter = target.alive
        self.running = False
        self.attack_type = 0
        self.jump_fighter = target.jump
        self.attacking_fighter = target.attacking
        key = pygame.key.get_pressed()
        rand_attack_type = random.randint(0, 1)

        # может выполнять действия только если не атакует
        if self.attacking == False and not self.attack_run:
            # movement
            attacking_rect = 80
            if self.rect.x + attacking_rect != self.rect_fighter.x and self.run_cooldown == 0:
                if (self.rect.x + attacking_rect) < self.rect_fighter.x:
                    dx = SPEED
                    self.running = True
                if (self.rect.x - attacking_rect) > self.rect_fighter.x:
                    dx = -SPEED
                    self.running = True
            elif self.rect.x == self.rect_fighter.x:
                self.run_cooldown = 30
            elif self.run_cooldown != 0:
                self.run_cooldown -= 1

            # прыжок
            if self.jump_fighter == True and self.jump == False:
                self.vel_y = -30
                self.jump = True

            # атака
            config = configparser.ConfigParser()
            config.read("fighter.ini")
            ultra = int(config.get("fighter", "ultra"))

            if (abs(self.rect.x - self.rect_fighter.x) <= attacking_rect) and (self.alive_fighter == True):
                self.attack(surface, target)
                # опредление вида атаки
                if ultra != 3:
                    self.attack_type = 1
                    self.health_damage = 10
                else:
                    self.attack_type = 2
                    self.health_damage = 20

                self.attack_run = True
        else:
            # movement
            self.running = True
            dx = -SPEED * 4

        # добавление гравитации
        self.vel_y += GRAVITY
        dy += self.vel_y

        # остановка персонажа на краях
        if self.rect.bottom + dy > screen_height - 70:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 70 - self.rect.bottom

        # убеждаемся, что персонажи смотрят друг на друга
        if self.alive == True and not self.attack_run:
            if target.rect.centerx > self.rect.centerx:
                self.flip = False
            else:
                self.flip = True
        else:
            self.flip = True

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # обновляем позицию игрока
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        # проверка мертв или нет бот
        if self.alive == False:
            self.level = 1
        # проверка какая анимация
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # Death
        elif self.hit == True:
            self.update_action(5)
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)  # Attack1
            elif self.attack_type == 2:
                self.update_action(4)  # Attack2
        elif self.jump == True:
            self.update_action(2)  # Jump
        elif self.running == True:
            self.update_action(1)  # Run
        else:
            self.update_action(0)  # Idle

        animation_cooldown = 115

        # update image
        self.image = self.animation_list[self.action][self.frame_index]

        # проверка прошло ли достаточно времени с момента последнего обновления
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # проврека закончилась ли анимация
        if self.frame_index >= len(self.animation_list[self.action]):
            # если герой умер последний кадр анимации смерти
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # была ли атака выполнена
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    if self.action == 4:
                        self.attack_cooldown = 40
                    elif self.action == 3:
                        self.attack_cooldown = 20
                # если была нанесена атака
                if self.action == 5:
                    self.hit = False
                    # если боец находился в середине атаки тогда атака остановлена
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (1 / 3 * self.rect.width * self.flip), self.rect.y,
                                         1 / 3 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= self.health_damage
                target.hit = True

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            # обновить настройки анимации
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (
            self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
