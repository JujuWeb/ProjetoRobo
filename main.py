import pygame
import random
import math
from entidades import *

pygame.init()
pygame.mixer.init()  

som_tiro = pygame.mixer.Sound("assets/som_tiro.mp3")           # som ao disparar
som_estouro = pygame.mixer.Sound("assets/estouro.mp3")         # som quando tiro acerta robo
som_colisao_jogador = pygame.mixer.Sound("assets/som_colisao.mp3")  # som quando jogador leva dano

som_tiro.set_volume(1.0)
som_estouro.set_volume(4.0)
som_colisao_jogador.set_volume(1.0)

pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
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

        # Menu
        if tela == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    tela = "jogo"

        # Tela do jogo
        elif tela == "jogo":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    som_tiro.play()  
                    tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
                    todos_sprites.add(tiro)
                    tiros.add(tiro)

                if event.key == pygame.K_p:
                    tela = "pause"

        # Tela de pausa
        elif tela == "pause":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    tela = "jogo"

        # Tela de game over
        elif tela == "gameover":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:

                    # música volta ao normal
                    pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
                    pygame.mixer.music.play(-1)

                    tela = "jogo"
                    jogador.vida = 5
                    pontos = 0
                    inimigos.empty()
                    tiros.empty()
                    todos_sprites.empty()
                    todos_sprites.add(jogador)

                    jogador.rect.centerx = LARGURA // 2
                    jogador.rect.centery = ALTURA - 60

    # Piscar o texto no menu
    tempo_texto += 1
    if tempo_texto > 20:
        texto_visivel = not texto_visivel
        tempo_texto = 0

    # Lógica do jogo
    if tela == "jogo":

        spawn_timer += 1
        if spawn_timer > 40:
            tipo = random.choice(["lento", "zigue", "cacador", "rapido", "ciclico"])

            if tipo == "lento":
                robo = RoboLento(random.randint(40, LARGURA - 40), -40)
            elif tipo == "rapido":
                robo = RoboRapido(random.randint(40, LARGURA - 40), -40)
            elif tipo == "zigue":
                robo = RoboZigueZague(random.randint(40, LARGURA - 40), -40)
            elif tipo == "ciclico":
                robo = RoboCiclico(random.randint(40, LARGURA - 40), -40)
            elif tipo == "cacador":
                robo = RoboCacador(random.randint(40, LARGURA - 40), -40, jogador)

            inimigos.add(robo)
            todos_sprites.add(robo)
            spawn_timer = 0

        # colisão tiro x inimigo
        colisoes = pygame.sprite.groupcollide(inimigos, tiros, True, True)

        for inimigo in colisoes:
            som_estouro.play()  
            explosao = Explosao(inimigo.rect.centerx, inimigo.rect.centery)
            todos_sprites.add(explosao)

        pontos += len(colisoes)

        # colisão jogador x inimigo
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            som_colisao_jogador.play()  
            jogador.vida -= 1
            if jogador.vida <= 0:
                tela = "gameover"

                # música de game over
                pygame.mixer.music.load("assets/gameovereal.mp3")
                pygame.mixer.music.play()

        todos_sprites.update()

    # Desenho da tela
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
        logo_x = 35 + math.cos(tempo_logo * 0.8) * 10
        TELA.blit(logo_img, (logo_x, logo_y))

        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 30)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 16)

        texto = font1.render("Pressione ENTER para começar!", True, (255, 255, 255))
        texto2 = font2.render("(Use as teclas WASD/setas para mover e Espaço para atirar)", True, (255, 255, 255))
  
        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, 350))
        TELA.blit(texto2, (160, 400))     

    elif tela == "pause":
        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 50)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)

        texto = font1.render("JOGO PAUSADO", True, (255, 255, 255))
        texto2 = font2.render("Pressione P para continuar!", True, (255, 255, 255))
        
        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 40))
        TELA.blit(texto2, (LARGURA//2 - texto2.get_width()//2, ALTURA//2 + 30))

    elif tela == "gameover":
        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 50)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)

        texto = font1.render("GAME OVER", True, (255, 50, 50))
        texto2 = font2.render("Pressione ENTER para reiniciar!", True, (255, 255, 255))

        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 40))
        TELA.blit(texto2, (LARGURA//2 - texto2.get_width()//2, ALTURA//2 + 30))

    pygame.display.flip()