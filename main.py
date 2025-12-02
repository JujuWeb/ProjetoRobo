import pygame
import random
import math
from entidades import *

pygame.init()

musica = pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
pygame.mixer.music.play(-1)

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                tela = "jogo"

        # JOGO
        elif tela == "jogo":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
                    todos_sprites.add(tiro)
                    tiros.add(tiro)

                if event.key == pygame.K_p:
                    tela = "pause"

        # PAUSE
        elif tela == "pause":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                tela = "jogo"

        # GAME OVER
        elif tela == "gameover":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                tela = "jogo"
                jogador.vida = 5
                pontos = 0

                inimigos.empty()
                tiros.empty()
                todos_sprites.empty()
                todos_sprites.add(jogador)

                jogador.rect.centerx = LARGURA // 2
                jogador.rect.centery = ALTURA - 60
                pygame.mixer.music.rewind()

    # Piscar o texto no menu
    tempo_texto += 1
    if tempo_texto > 20:
        texto_visivel = not texto_visivel
        tempo_texto = 0

    # -------------------------------------
    # LÓGICA DO JOGO
    # -------------------------------------
    if tela == "jogo":

        # SPWAN DOS ROBÔS
        spawn_timer += 1
        if spawn_timer > 40:

            tipo = random.choice(["lento", "zigue"])

            if tipo == "lento":
                robo = RoboLento(random.randint(40, LARGURA - 40), -40)
            else:
                robo = RoboZigueZague(random.randint(40, LARGURA - 40), -40)

            inimigos.add(robo)
            todos_sprites.add(robo)
            spawn_timer = 0

        # Colisão tiro vs inimigo
        colisao = pygame.sprite.groupcollide(inimigos, tiros, True, True)
        pontos += len(colisao)

        # Colisão jogador x robô
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            jogador.vida -= 1
            if jogador.vida <= 0:
                tela = "gameover"

        todos_sprites.update()

    # -------------------------------------
    # DESENHO DA TELA
    # -------------------------------------
    TELA.blit(fundo_img, (0, 0))

    if tela == "jogo":
        todos_sprites.draw(TELA)
        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)
        texto = font.render(f"Vida: {jogador.vida} | Pontos: {pontos}",
                            True, (255, 255, 255))
        TELA.blit(texto, (10, 10))

    elif tela == "menu":
        tempo_logo += 0.05
        logo_y = 40 + math.sin(tempo_logo) * 10
        logo_x = 40 + math.cos(tempo_logo * 0.8) * 10
        TELA.blit(logo_img, (logo_x, logo_y))

        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 30)
        texto = font.render("Pressione ENTER para começar!",
                            True, (255, 255, 255))
        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, 350))

    elif tela == "pause":
        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 40)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 25)
        texto = font1.render("JOGO PAUSADO", True, (255, 255, 255))
        texto2 = font2.render("Pressione P para continuar",
                              True, (255, 255, 255))

        TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 40))
        TELA.blit(texto2, (LARGURA//2 - texto2.get_width()//2, ALTURA//2 + 10))

    elif tela == "gameover":
        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 40)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 25)

        texto = font1.render("GAME OVER", True, (255, 50, 50))
        texto2 = font2.render("Pressione ENTER para reiniciar",
                              True, (255, 255, 255))

        TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 40))
        TELA.blit(texto2, (LARGURA//2 - texto2.get_width()//2, ALTURA//2 + 10))

    pygame.display.flip()
