from typing import List
import pygame
import random
import os
import math

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

        self.vel_base = 5          # velocidade normal
        self.tempo_vel = 0         # tempo que o power-up dura

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
        # animação
        self.frame += 0.03
        if self.frame >= len(self.sprites):
            self.frame = 0
        self.image = self.sprites[int(self.frame)]

        #  VOLTAR À VELOCIDADE NORMAL QUANDO O TEMPO ACABAR
        if pygame.time.get_ticks() > self.tempo_vel:
            self.velocidade = self.vel_base

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.mover(0, -self.velocidade)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.mover(0, self.velocidade)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.mover(-self.velocidade, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.mover(self.velocidade, 0)

        # limites
        self.rect.x = max(0, min(self.rect.x, LARGURA - self.image.get_width()))
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.image.get_height()))

# TIRO
class Tiro(Entidade):
    def __init__(self, x, y, vel_x=0, vel_y=-1):
        super().__init__(x, y, 10)
        tiro1 = pygame.image.load("assets/ataque.png").convert_alpha()
        tiro1 = pygame.transform.rotate(tiro1, -135)
        tiro1 = pygame.transform.scale(tiro1, (100, 100))
        self.image = tiro1
        self.rect = self.image.get_rect(center=(x, y))

        self.vel_x = vel_x * self.velocidade
        self.vel_y = vel_y * self.velocidade

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > LARGURA:
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

        larg = self.original_image.get_width()

        if self.rect.centerx <= larg/2 or self.rect.centerx >= LARGURA - larg/2:
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

        self.image = pygame.image.load("assets/UfoGrey.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
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


# ROBO SALTADOR
class RoboSaltador(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=4)

        # sprite
        self.image_original = pygame.image.load("assets/Satelite2.png").convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (80, 80))
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


# BOSS
class Boss(Robo):
    def __init__(self, x, y, fase = 1):
        super().__init__(x, y, velocidade=1.5)

        try:
            self.image_original = pygame.image.load("assets/boss-Photoroom.png").convert_alpha()
            self.image_original = pygame.transform.scale(self.image_original, (120, 160))
            self.image = self.image_original.copy()
        except:
            pass

        self.rect = self.image.get_rect(center=(x, y))

        # Vida
        self.vida = 100
        self.vida_max = 100

        # Movimento
        self.angulo = 0
        self.vel_giro = 0.6

        # Centro FIXO (isso evita travar nas bordas)
        self.centro_x = x
        self.centro_y = y

        # Amplitudes
        self.raio = 140
        self.amp_x = 250
        self.amp_y = 80

        # Padrões
        self.padrao_movimento = 0
        self.proximo_padrao = 0
        self.tempo_padrao = 0

        # Transição
        self.em_transicao = False
        self.t = 0.0
        self.vel_transicao = 0.03

        # Ataques (inalterados)
        self.tempo_tiro = 0
        self.ataque_atual = 1
        self.contador_ataques = 0

        self.max_ataque1 = 4
        self.max_ataque2 = 3

        self.intervalo_ataque1 = 90

        self.ataque_circulo_rapido = False
        self.angulo_circulo = 0
        self.velocidade_circulo = 20
        self.tempo_entre_tiros_circulo = 10
        self.intervalo_ataque2 = 120

    def _pos_padrao(self, padrao):
        ang = math.radians(self.angulo)

        if padrao == 0:  # circular
            return (
                self.centro_x + math.cos(ang) * self.raio,
                self.centro_y + math.sin(ang) * self.raio
            )
        elif padrao == 1:  # horizontal
            return (
                self.centro_x + math.cos(ang) * self.amp_x,
                self.centro_y
            )
        else:  # vertical
            return (
                self.centro_x,
                self.centro_y + math.sin(ang) * self.amp_y + 45
            )

    def atualizar_posicao(self):
        self.angulo += self.vel_giro
        self.tempo_padrao += 1

        # Inicia transição
        if self.tempo_padrao > 300 and not self.em_transicao:
            self.tempo_padrao = 0
            self.em_transicao = True
            self.t = 0.0
            self.proximo_padrao = (self.padrao_movimento + 1) % 3

        if self.em_transicao:
            self.t += self.vel_transicao
            if self.t >= 1:
                self.t = 1
                self.em_transicao = False
                self.padrao_movimento = self.proximo_padrao

            x1, y1 = self._pos_padrao(self.padrao_movimento)
            x2, y2 = self._pos_padrao(self.proximo_padrao)

            x = x1 + (x2 - x1) * self.t
            y = y1 + (y2 - y1) * self.t
        else:
            x, y = self._pos_padrao(self.padrao_movimento)

        self.rect.center = (int(x), int(y))
        
        limite_topo = 40
        if self.rect.top < limite_topo:
            excesso = limite_topo - self.rect.top
            self.centro_y += excesso * 0.15
            

    def atirar(self, grupo_tiros, grupo_sprites):
        self.tempo_tiro += 1

        if self.ataque_atual == 1:
            if self.tempo_tiro >= self.intervalo_ataque1:
                self.tempo_tiro = 0
                self.contador_ataques += 1

                for i in range(8):
                    tiro = TiroBoss(self.rect.centerx, self.rect.centery, i * 45)
                    grupo_tiros.add(tiro)
                    grupo_sprites.add(tiro)

                if self.contador_ataques >= self.max_ataque1:
                    self.ataque_atual = 2
                    self.contador_ataques = 0
                    self.ataque_circulo_rapido = False
                    self.angulo_circulo = 0
        else:
            if not self.ataque_circulo_rapido:
                if self.tempo_tiro >= self.intervalo_ataque2:
                    self.tempo_tiro = 0
                    self.ataque_circulo_rapido = True
                    self.angulo_circulo = 0
            else:
                if self.tempo_tiro >= self.tempo_entre_tiros_circulo:
                    self.tempo_tiro = 0

                    tiro = TiroBoss(self.rect.centerx, self.rect.centery, self.angulo_circulo)
                    grupo_tiros.add(tiro)
                    grupo_sprites.add(tiro)

                    self.angulo_circulo += self.velocidade_circulo

                    if self.angulo_circulo >= 360:
                        self.ataque_circulo_rapido = False
                        self.contador_ataques += 1

                        if self.contador_ataques >= self.max_ataque2:
                            self.ataque_atual = 1
                            self.contador_ataques = 0

    def atualizar_fase(self):
        vida_pct = self.vida / self.vida_max

        if vida_pct <= 0.3:
            self.fase = 3
        elif vida_pct <= 0.7:
            self.fase = 2
        else:
            self.fase = 1

        # Ajustes por fase
        if self.fase == 1:
            self.vel_giro = 0.6
            self.intervalo_ataque1 = 90
            self.intervalo_ataque2 = 120
            self.tempo_entre_tiros_circulo = 10
            self.velocidade_circulo = 20
            self.max_ataque1 = 4
            self.max_ataque2 = 3

        elif self.fase == 2:
            self.vel_giro = 0.9
            self.intervalo_ataque1 = 70
            self.intervalo_ataque2 = 100
            self.tempo_entre_tiros_circulo = 8
            self.velocidade_circulo = 26
            self.max_ataque1 = 5
            self.max_ataque2 = 4

        else:  # FASE 3
            self.vel_giro = 1.2
            self.intervalo_ataque1 = 55
            self.intervalo_ataque2 = 80
            self.tempo_entre_tiros_circulo = 6
            self.velocidade_circulo = 32
            self.max_ataque1 = 6
            self.max_ataque2 = 5
        
    def update(self):
        self.atualizar_fase()
        self.atualizar_posicao()

class TiroBoss(Tiro):
    def __init__(self, x, y, angulo):
        pygame.sprite.Sprite.__init__(self)
        self.velocidade = 4
        self.angulo = math.radians(angulo)
        
        # Usar EXATAMENTE a mesma sprite do tiro do jogador
        try:
            # Mesma transformação do tiro do jogador
            tiro_img = pygame.image.load("assets/Tiro-Boss.png").convert_alpha()
            
            # Tamanho um pouco menor que o do jogador (ajuste conforme necessário)
            tiro_img = pygame.transform.scale(tiro_img, (50, 90))
            self.image = tiro_img
        except:
            # Fallback: se a imagem não existir
            self.image = pygame.Surface((25, 25))
            self.image.fill((255, 165, 0))  # Laranja
            pygame.draw.circle(self.image, (255, 255, 0), (12, 12), 10)  # Com círculo amarelo
            
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-30, -50)
        
    def update(self):
        # Movimento baseado no ângulo (direções variadas)
        self.rect.x += math.cos(self.angulo) * self.velocidade
        self.rect.y += math.sin(self.angulo) * self.velocidade

        self.hitbox.center = self.rect.center
        
        # Remove se sair da tela (com margem maior)
        if (self.rect.y < -100 or self.rect.y > ALTURA + 100 or 
            self.rect.x < -100 or self.rect.x > LARGURA + 100):
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, cor=(255,255,255), image_path=None):
        super().__init__()
        
        if image_path and os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(img, (30, 30))
        else:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            self.image.fill(cor)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade = 2

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.y > ALTURA:
            self.kill()

class PowerUpVelocidade(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, cor=(255, 255, 0), image_path="assets/robovelocidade.png")

class PowerUpTiroTriplo(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, cor=(128, 0, 128), image_path="assets/robotirotriplo.png")

class PowerUpVidaExtra(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, cor=(0, 255, 0), image_path="assets/robovida.png")