from typing import List
import pygame
import random

LARGURA = 900
ALTURA = 500

# Explosão
explosao_img = pygame.image.load("assets/EXPLOSÃO.png")
explosao_frames = [
    pygame.transform.scale(explosao_img, (32, 32)),
    pygame.transform.scale(explosao_img, (64, 64)),
    pygame.transform.scale(explosao_img, (120, 120)),
    pygame.transform.scale(explosao_img, (64, 64)),
    pygame.transform.scale(explosao_img, (32, 32)),
]


class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = explosao_frames
        self.frame = 0
        self.image = self.frames[self.frame]

        self.center = (x, y)
        self.rect = self.image.get_rect(center=self.center)
        self.velocidade_anim = 0.4

    def update(self):
        self.frame += self.velocidade_anim

        if int(self.frame) >= len(self.frames):
            self.kill()
            return

        self.image = self.frames[int(self.frame)]
        self.rect = self.image.get_rect(center=self.center)


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)

        self.sprites: List[pygame.Surface] = []

        jogador1 = pygame.image.load("assets/Astronaut.png").convert_alpha()
        jogador2 = pygame.image.load("assets/Astronaut1.png").convert_alpha()

        jogador1 = pygame.transform.scale(jogador1, (80, 80))
        jogador2 = pygame.transform.scale(jogador2, (80, 80))

        self.sprites.append(jogador1)
        self.sprites.append(jogador2)

        self.frame = 0
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(center=(x, y))

        self.vida = 5

    def update(self):
        self.frame += 0.03
        if self.frame >= len(self.sprites):
            self.frame = 0

        self.image = self.sprites[int(self.frame)]

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.mover(0, -self.velocidade)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.mover(0, self.velocidade)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.mover(-self.velocidade, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.mover(self.velocidade, 0)

        self.rect.x = max(0, min(self.rect.x, LARGURA - self.image.get_width()))
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.image.get_height()))


# TIRO
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        tiro1 = pygame.image.load("assets/ataque.png").convert_alpha()
        tiro1 = pygame.transform.rotate(tiro1, -135)
        tiro1 = pygame.transform.scale(tiro1, (100, 100))
        self.image = tiro1
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))

    def atualizar_posicao(self):
        raise NotImplementedError


# ROBO ZIGUE ZAGUE
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1

        self.original_image = pygame.image.load("assets/furacao.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (52, 52))

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.angulo = 0  

    def atualizar_posicao(self):
        self.rect.y += self.velocidade

        self.rect.x += self.direcao * random.randint(3, 8)

        if self.rect.centerx <= 0 or self.rect.centerx >= LARGURA - self.image.get_width():
            self.direcao *= -1

        self.angulo = (self.angulo + 15) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angulo)

        centro = self.rect.center
        self.rect = self.image.get_rect(center=centro)

        if self.rect.y > ALTURA:
            self.kill()

    def update(self):
        self.atualizar_posicao()


# ROBO RÁPIDO
class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=12)

        img = pygame.image.load("assets/estrelacadente.png").convert_alpha()
        img = pygame.transform.rotate(img, -50)
        img = pygame.transform.scale(img, (80, 80))

        self.image = img
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_posicao(self):
        self.rect.y += self.velocidade

        if self.rect.y > ALTURA:
            self.kill()

    def update(self):
        self.atualizar_posicao()


# ROBO LENTO
class RoboLento(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1)

        self.image = pygame.image.load("assets/satelite.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_posicao(self):
        self.rect.y += self.velocidade

        if self.rect.y > ALTURA:
            self.kill()

    def update(self):
        self.atualizar_posicao()


# ROBO CÍCLICO
class RoboCiclico(Robo):
    def __init__(self, x, y):

        super().__init__(x, y, velocidade=2)

        self.image = pygame.image.load("assets/UfoBlue.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

        self.base_x = max(40, min(x, LARGURA - 40))
        self.base_y = y

        self.raio = 60
        self.vel_giro = 0.3

        self.tabela_x = [0, 1, 2, 3, 2, 1, 0, -1, -2, -3, -2, -1]
        self.tabela_y = [-3, -2, -1, 0, 1, 2, 3, 2, 1, 0, -1, -2]

        self.indice = 0
        self.descida = 1

    def atualizar_posicao(self):
        self.base_y += self.descida

        self.indice = (self.indice + self.vel_giro) % len(self.tabela_x)
        i = int(self.indice)

        cx = self.tabela_x[i] * self.raio / 3
        cy = self.tabela_y[i] * self.raio / 3

        self.rect.centerx = int(self.base_x + cx)
        self.rect.centery = int(self.base_y + cy)

        if self.rect.top > ALTURA:
            self.kill()

    def update(self):
        self.atualizar_posicao()


# ROBO CAÇADOR
class RoboCacador(Robo):
    def __init__(self, x, y, jogador):
        super().__init__(x, y, velocidade=5)

        self.jogador = jogador
        self.image = pygame.image.load("assets/nave.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, 180)
        self.image = pygame.transform.scale(self.image, (65, 65))
        self.rect = self.image.get_rect(center=(x, y))

    def atualizar_posicao(self):
        dx = self.jogador.rect.centerx - self.rect.centerx
        dy = self.jogador.rect.centery - self.rect.centery

        distancia = max(1, (dx**2 + dy**2) ** 0.5)

        self.rect.x += (dx / distancia) * self.velocidade
        self.rect.y += (dy / distancia) * self.velocidade
        
        if self.rect.y > ALTURA + 40:
            self.kill()

    def update(self):
        self.atualizar_posicao()


# ROBO SALTADOR — PARABÓLICO
class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=4)

        # sprite
        self.image_original = pygame.image.load("assets/RedPlanet.png").convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (60, 60))
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(x, y))

        # salto parabólico
        self.altura_salto = random.randint(60, 120)
        self.tempo_total = random.randint(50, 90)
        self.tempo_atual = 0

        self.dx = random.choice([-1, 1]) * random.randint(2, 4)

    def atualizar_posicao(self):
        self.tempo_atual += 1

        self.rect.x += self.dx

        if self.rect.x < 0 or self.rect.x > LARGURA - self.image.get_width():
            self.dx *= -1

        self.rect.y += 4

        t = self.tempo_atual / self.tempo_total
        altura = -4 * self.altura_salto * (t - 0.5) ** 2 + self.altura_salto

        self.rect.y += int(-altura / 10) + 3

        if self.tempo_atual >= self.tempo_total:
            self.tempo_atual = 0
            self.altura_salto = random.randint(60, 120)
            self.tempo_total = random.randint(50, 90)

        if self.rect.y > ALTURA:
            self.kill()

    def update(self):
        self.atualizar_posicao()


# BOSS (AINDA VAZIO)
class Boss(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
