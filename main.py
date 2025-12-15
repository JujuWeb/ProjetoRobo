import pygame
import random
import math
import os
from entidades import *

pygame.init()
pygame.mixer.init()

som_tiro = pygame.mixer.Sound("assets/som_tiro.mp3")
som_estouro = pygame.mixer.Sound("assets/estouro.mp3")
som_colisao_jogador = pygame.mixer.Sound("assets/som_colisao.mp3")
som_boss_hit = pygame.mixer.Sound("assets/som_colisao.mp3")  # Usando som existente para hits no boss
som_boss_morto = pygame.mixer.Sound("assets/estouro.mp3")  # Usando explosão para boss morto

som_tiro.set_volume(1.0)
som_estouro.set_volume(4.0)
som_colisao_jogador.set_volume(1.0)
som_boss_hit.set_volume(0.7)
som_boss_morto.set_volume(5.0)

pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
pygame.mixer.music.play(-1)

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Astro Combat")

FPS = 60
clock = pygame.time.Clock()

fundo_img = pygame.image.load("assets/space.png").convert()
fundo_img = pygame.transform.scale(fundo_img, (900, 500))
logo_img = pygame.image.load("assets/logo.png").convert_alpha()
logo_img = pygame.transform.scale(logo_img, (800, 350))

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
tiros_boss = pygame.sprite.Group()
powerups = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

pontos = 0
recorde = 0
spawn_timer = 0

tempo_logo = 0
tempo_texto = 0
texto_visivel = True

DURACAO_POWERUP_MS = 10000

tela = "menu"
rodando = True

fundo_atual = 1
transicao = False
alpha = 0
escurecendo = True
transicao_feita = False

# Variáveis para o boss
boss_ativo = False
boss = None
boss_spawned = False
boss_derrotado = False
tempo_boss_morto = 0

while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if tela == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    tela = "jogo"

        elif tela == "jogo":
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    som_tiro.play()

                    # Tiro normal
                    tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
                    todos_sprites.add(tiro)
                    tiros.add(tiro)

                    # Tiro triplo
                    if pygame.time.get_ticks() < getattr(jogador, "tempo_tiro_triplo", 0):
                        tiro_esq = Tiro(jogador.rect.centerx - 20, jogador.rect.top)
                        tiro_dir = Tiro(jogador.rect.centerx + 20, jogador.rect.top)
                        todos_sprites.add(tiro_esq, tiro_dir)
                        tiros.add(tiro_esq, tiro_dir)

                if event.key == pygame.K_p:
                    tela = "pause"

        elif tela == "pause":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    tela = "jogo"

        elif tela == "gameover":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
                    pygame.mixer.music.play(-1)

                    tela = "jogo"
                    jogador.vida = 5
                    pontos = 0
                    inimigos.empty()
                    tiros.empty()
                    tiros_boss.empty()
                    todos_sprites.empty()
                    todos_sprites.add(jogador)

                    jogador.rect.centerx = LARGURA // 2
                    jogador.rect.centery = ALTURA - 60
                    
                    # Resetar boss
                    boss_ativo = False
                    boss = None
                    boss_spawned = False
                    boss_derrotado = False
                    tempo_boss_morto = 0

    tempo_texto += 1
    if tempo_texto > 20:
        texto_visivel = not texto_visivel
        tempo_texto = 0

    if tela == "jogo":
        # SPAWN DE INIMIGOS NORMAIS (apenas se não houver boss ativo)
        if not boss_ativo and not boss_derrotado:
            if pontos < 150:
                tempo_spawn = 40
            elif pontos < 200:
                tempo_spawn = 25
            else:
                tempo_spawn = 18

            spawn_timer += 1
            if spawn_timer > tempo_spawn:
                tipo = random.choice(["lento", "zigue", "cacador", "rapido", "ciclico", "saltador"])

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
                elif tipo == "saltador":
                    robo = RoboSaltador(random.randint(40, LARGURA - 40), -40)

                inimigos.add(robo)
                todos_sprites.add(robo)
                spawn_timer = 0

        # SPAWN DO BOSS
        if pontos >= 200 and not boss_spawned and not boss_derrotado:
            boss = Boss(LARGURA // 2, 80)
            todos_sprites.add(boss)
            inimigos.add(boss)
            boss_ativo = True
            boss_spawned = True
            
            # Parar música normal e tocar música de boss
            pygame.mixer.music.load("assets/gameovereal.mp3")  # Usando música existente, você pode trocar depois
            pygame.mixer.music.play(-1)

        # ATUALIZAR E ATIRAR DO BOSS
        if boss_ativo and boss:
            boss.atirar(tiros_boss, todos_sprites)
            
            # Checar colisão dos tiros do jogador com o boss
            hits_boss = pygame.sprite.spritecollide(boss, tiros, True)
            for hit in hits_boss:
                boss.vida -= 1
                som_boss_hit.play()
                if boss.vida <= 0:
                    boss_ativo = False
                    boss_derrotado = True
                    tempo_boss_morto = pygame.time.get_ticks()
                    
                    # Explosão grande para o boss
                    for i in range(5):
                        explosao = Explosao(boss.rect.centerx + random.randint(-50, 50), 
                                           boss.rect.centery + random.randint(-50, 50))
                        todos_sprites.add(explosao)
                    
                    
                    # Power-ups especiais ao derrotar o boss
                    for i in range(3):
                        tipo = random.choice([PowerUpTiroTriplo, PowerUpVelocidade, PowerUpVidaExtra])
                        powerup = tipo(boss.rect.centerx + random.randint(-100, 100), 
                                      boss.rect.centery + random.randint(-50, 50))
                        todos_sprites.add(powerup)
                        powerups.add(powerup)
                    
                    som_boss_morto.play()
                    boss.kill()
                    
                    # Voltar música normal
                    pygame.mixer.music.load("assets/SkyFire(fundo).mp3")
                    pygame.mixer.music.play(-1)

        # COLISÕES NORMAIS (tiros do jogador vs inimigos normais)
        colisoes = pygame.sprite.groupcollide(inimigos, tiros, True, True)

        for inimigo in colisoes:
            som_estouro.play()
            explosao = Explosao(inimigo.rect.centerx, inimigo.rect.centery)
            todos_sprites.add(explosao)

            if random.random() < 0.035 and not boss_ativo:
                p_tipo = random.choice([PowerUpTiroTriplo, PowerUpVelocidade, PowerUpVidaExtra])
                powerup = p_tipo(inimigo.rect.centerx, inimigo.rect.centery)
                todos_sprites.add(powerup)
                powerups.add(powerup)

        pontos += len(colisoes)

        # COLISÕES: Jogador vs Inimigos (incluindo boss)
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            som_colisao_jogador.play()
            jogador.vida -= 2 if boss_ativo else 1  # Boss causa mais dano
            if jogador.vida <= 0:

                if pontos > recorde:
                    recorde = pontos

                tela = "gameover"

                pygame.mixer.music.load("assets/gameovereal.mp3")
                pygame.mixer.music.play()

        # COLISÕES: Jogador vs Tiros do Boss
        if pygame.sprite.spritecollide(jogador, tiros_boss, True):
            som_colisao_jogador.play()
            jogador.vida -= 1
            if jogador.vida <= 0:
                if pontos > recorde:
                    recorde = pontos
                tela = "gameover"
                pygame.mixer.music.load("assets/gameovereal.mp3")
                pygame.mixer.music.play()

        todos_sprites.update()

        # COLISÕES: Jogador vs Power-ups
        powerup_col = pygame.sprite.spritecollide(jogador, powerups, True)
        for p in powerup_col:
            current_time = pygame.time.get_ticks()

            if isinstance(p, PowerUpVelocidade):
                if not hasattr(jogador, "vel_base"):
                    jogador.vel_base = getattr(jogador, "velocidade", 5)
                jogador.velocidade = 8
                jogador.tempo_vel = current_time + DURACAO_POWERUP_MS

            elif isinstance(p, PowerUpTiroTriplo):
                jogador.tempo_tiro_triplo = current_time + DURACAO_POWERUP_MS
                
            elif isinstance(p, PowerUpVidaExtra):
                jogador.vida += 1
                
        # Transição de fundo (apenas se não tiver boss ativo)
        if pontos >= 200 and not transicao and not transicao_feita and not boss_ativo:
            transicao = True
            escurecendo = True
            alpha = 0

    # DESENHAR TELA
    TELA.blit(fundo_img, (0, 0))

    if tela == "jogo":
        todos_sprites.draw(TELA)
        
        # Mostrar barra de vida do boss na tela se estiver ativo
        if boss_ativo and boss:
            font = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)
            texto_boss = font.render(f"BOSS: {boss.vida}/{boss.vida_max}", True, (255, 0, 0))
            TELA.blit(texto_boss, (LARGURA // 2 - texto_boss.get_width() // 2, 10))
                   
        font = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)
        texto = font.render(f"Vida: {jogador.vida} | Pontos: {pontos}", True, (255, 255, 255))
        TELA.blit(texto, (10, 10))
        
        # Mostrar mensagem de boss derrotado
        if boss_derrotado:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - tempo_boss_morto < 3000:  # Mostrar por 3 segundos
                font_grande = pygame.font.Font("assets/DepartureMono-Regular.otf", 36)
                texto_vitoria = font_grande.render("BOSS DERROTADO! +100 PONTOS", True, (0, 255, 0))
                TELA.blit(texto_vitoria, (LARGURA // 2 - texto_vitoria.get_width() // 2, ALTURA // 2))

    elif tela == "menu":
        tempo_logo += 0.05
        logo_y = 40 + math.sin(tempo_logo) * 10
        logo_x = 25 + math.cos(tempo_logo * 0.8) * 10
        TELA.blit(logo_img, (logo_x, logo_y))

        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 30)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 16)

        texto = font1.render("Pressione ENTER para começar!", True, (255, 255, 255))
        texto2 = font2.render("(Use WASD/setas para mover e Espaço para atirar)", True, (255, 255, 255))

        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, 350))
            TELA.blit(texto2, (LARGURA//1.9 - texto.get_width()//2, 395))

    elif tela == "pause":
        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 50)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)

        texto = font1.render("JOGO PAUSADO", True, (255, 255, 255))
        texto2 = font2.render("Pressione P para continuar!", True, (255, 255, 255))
        texto3 = font2.render(f"Recorde: {recorde}", True, (255, 255, 255))

        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 40))
        TELA.blit(texto2, (LARGURA//2 - texto2.get_width()//2, ALTURA//2 + 30))
        TELA.blit(texto3, (LARGURA//2 - texto3.get_width()//2, ALTURA//2 + 70))

    elif tela == "gameover":
        font1 = pygame.font.Font("assets/DepartureMono-Regular.otf", 50)
        font2 = pygame.font.Font("assets/DepartureMono-Regular.otf", 20)

        texto = font1.render("GAME OVER", True, (255, 50, 50))
        texto2 = font2.render("Pressione ENTER para reiniciar!", True, (255, 255, 255))
        texto3 = font2.render(f"Pontuação: {pontos}", True, (255, 255, 255))
        texto4 = font2.render(f"Recorde: {recorde}", True, (255, 255, 0))

        if texto_visivel:
            TELA.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - 40))
        TELA.blit(texto2, (LARGURA//2 - texto2.get_width()//2, ALTURA//2 + 30))
        TELA.blit(texto3, (LARGURA//2 - texto3.get_width()//2, ALTURA//2 + 60))
        TELA.blit(texto4, (LARGURA//2 - texto4.get_width()//2, ALTURA//2 + 90))

    if transicao:
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 0, 0))

        if escurecendo:
            alpha += 5
            if alpha >= 255:
                alpha = 255
                escurecendo = False

                fundo_atual += 1
                novo_fundo = f"assets/space{fundo_atual}.png"

                if os.path.exists(novo_fundo):
                    fundo_img = pygame.image.load(novo_fundo).convert()
                    fundo_img = pygame.transform.scale(fundo_img, (LARGURA, ALTURA))
                else:
                    fundo_img = pygame.transform.flip(fundo_img, True, False)

        else:
            alpha -= 5
            if alpha <= 0:
                alpha = 0
                transicao = False 
                transicao_feita = True


        overlay.set_alpha(alpha)
        TELA.blit(overlay, (0, 0))

    pygame.display.flip()