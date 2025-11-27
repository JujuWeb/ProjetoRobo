import pygame
import random
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

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

pontos = 0
spawn_timer = 0

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
                if event.key == pygame.K_SPACE:
                    tela = "jogo"

        # GAME
        elif tela == "jogo":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
                    todos_sprites.add(tiro)
                    tiros.add(tiro) 

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
        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 80)
        logo = font.render("Logo", True, (255, 255, 255))
        TELA.blit(logo, (350, 200))
        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 30)
        texto = font.render("Pressione ENTER para começar!", True, (255, 255, 255))
        TELA.blit(texto, (205, 350))

    pygame.display.flip()