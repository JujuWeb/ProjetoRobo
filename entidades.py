from typing import List
import pygame
import random

LARGURA = 900
ALTURA = 500

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)

        self.sprites: List[pygame.Surface] = []

        jogador1 = pygame.image.load("assets/Astronaut.png").convert_alpha()
        jogador2 = pygame.image.load("assets/Astronaut1.png").convert_alpha()

        # Aumenta o tamanho 
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


# TIRO DO JOGADOR
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        tiro1 = pygame.image.load("assets/ataque.png").convert_alpha()
        # Rotaciona a imagem
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
        self.image.fill((255, 0, 0))  # vermelho

    def atualizar_posicao(self):
        raise NotImplementedError


# ROBO ZigueZague
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1

        self.original_image = pygame.image.load("assets/furacao.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (60, 60))

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # ângulo de rotação
        self.angulo = 0  

    def atualizar_posicao(self):
        # Movimento para baixo
        self.rect.y += self.velocidade

        # Zigue-zague forte e aleatório
        self.rect.x += self.direcao * random.randint(3, 8)

        # Bate na parede
        if self.rect.centerx <= 0 or self.rect.centerx >= LARGURA - self.image.get_width():
            self.direcao *= -1

        # Rotação do furacão
        self.angulo = (self.angulo + 10) % 360   # quanto maior → gira mais rápido
        self.image = pygame.transform.rotate(self.original_image, self.angulo)

        centro = self.rect.center
        self.rect = self.image.get_rect(center=centro)

        if self.rect.y > ALTURA:
            self.kill()

    def update(self):
        self.atualizar_posicao()

# ROBO RAPIDO
class RoboRapido(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=10)

        self.image = pygame.image.load("assets/estrelacadente.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
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



# ROBO CAÇADOR 
class RoboCacador(Robo):
    def __init__(self, x, y, jogador):
        super().__init__(x, y, velocidade=2)

        self.jogador = jogador
        self.image = pygame.image.load("assets/Nave_caçador.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
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
