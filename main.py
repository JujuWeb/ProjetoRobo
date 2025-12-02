import pygame
import random
import math
from entidades import *

pygame.init()

musica = pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
pygame.mixer_music.play(-1)

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")

FPS = 60
clock = pygame.time.Clock()

fundo_img = pygame.image.load("assets/space.png").convert()
fundo_img = pygame.transform.scale(fundo_img, (900, 500))
logo_img = pygame.image.load("assets/logo.png").convert_alpha()
logo_img = pygame.transform.scale(logo_img, (800, 350))

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

pontos = 0
spawn_timer = 0

tempo_logo = 0  
tempo_texto = 0
texto_visivel = True

tela = "menu"
rodando = True 

while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        # MENU
        if tela == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    tela = "jogo"

        # GAME
        elif tela == "jogo":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
                    todos_sprites.add(tiro)
                    tiros.add(tiro) 

    tempo_texto += 1
    if tempo_texto > 20:   # velocidade de piscar
        texto_visivel = not texto_visivel
        tempo_texto = 0

    # Lógica só quando estiver no jogo
    if tela == "jogo":

        # Timer dos inimigos
        spawn_timer += 1
        if spawn_timer > 40:
            robo = RoboZigueZague(random.randint(40, LARGURA - 40), -40)
            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0

        # Colisão tiro x robô
        colisao = pygame.sprite.groupcollide(inimigos, tiros, True, True)
        pontos += len(colisao)

        # Colisão robô x jogador
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            jogador.vida -= 1
            if jogador.vida <= 0:
                tela = "menu"
                jogador.vida = 5
                pontos = 0
                inimigos.empty()
                tiros.empty()
                jogador.rect.centerx = LARGURA // 2
                jogador.rect.centery = ALTURA - 60
                pygame.mixer.music.rewind()

        # Atualizar
        todos_sprites.update()

    # DESENHAR TUDO
    TELA.blit(fundo_img, (0, 0))

    if tela == "jogo":
        todos_sprites.draw(TELA)

        # Painel
        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)
        texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
        TELA.blit(texto, (10, 10))

    elif tela == "menu":
        tempo_logo += 0.05  
    # movimento vertical senoidal
        logo_y = 40 + math.sin(tempo_logo) * 10

    # movimento horizontal senoidal
        logo_x = 40 + math.cos(tempo_logo * 0.8) * 10   

        TELA.blit(logo_img, (logo_x, logo_y))
        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 30)
        texto = font.render("Pressione ENTER para começar!", True, (255, 255, 255))
        if texto_visivel:   # só desenha quando está "ligado"
            TELA.blit(texto, (205, 350))

    pygame.display.flip()