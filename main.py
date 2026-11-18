import asyncio
import random
import pygame

pygame.init()

# Setup tela e fps

largura, altura = 500, 500
# SCALED = o pygame estica o jogo pra caber na tela (celular em pé ou deitado)
# sem deformar, e converte sozinho a posição do toque/mouse
tela = pygame.display.set_mode((largura, altura), pygame.SCALED)
pygame.display.set_caption("Sarah's world")

relogio = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)
fonte_grande = pygame.font.Font(None, 72)

# cores (R,G,B)

ROSA = 255, 20, 147
BRANCO = 255, 255, 255
VERMELHO = 255, 60, 60

# ---------- Configurações do cronômetro (mude à vontade) ----------

TEMPO_INICIAL = 10    # segundos de cada partida
BONUS_PANDA = 1       # segundos ganhos a cada panda coletado
TEMPO_MAXIMO = None   # limite de tempo em segundos (None = sem limite)

# ---------- Imagens ----------
# IMPORTANTE: o convert_alpha() só funciona depois do set_mode, por isso
# o carregamento fica aqui embaixo da criação da tela.

ESCALA_PLAYER = 3  # aumenta o sprite do player (mude se ficar pequeno/grande)
ESCALA_PANDA = 2    # aumenta o sprite do panda

# ---------- Configurações do título do menu ----------
QTD_FRAMES_TITULO = 2     # quantos "desenhos" tem na imagem (se for uma só, coloque 1)
LARGURA_TITULO = 460      # largura final do título na tela (mude se ficar grande/pequeno)


def carregar_frames(caminho, qtd_frames, escala):
    """Carrega uma sprite sheet horizontal e devolve uma lista de frames."""
    folha = pygame.image.load(caminho).convert_alpha()
    largura_frame = folha.get_width() // qtd_frames
    altura_frame = folha.get_height()

    frames = []
    for i in range(qtd_frames):
        # recorta o pedaço i da imagem
        frame = folha.subsurface((i * largura_frame, 0, largura_frame, altura_frame))
        # aumenta (scale mantém os pixels nítidos, sem borrar)
        frame = pygame.transform.scale(
            frame, (largura_frame * escala, altura_frame * escala)
        )
        frames.append(frame)
    return frames


def carregar_titulo(caminho, qtd_frames, largura_desejada):
    """Carrega o título e ajusta o tamanho pra caber na tela, sem deformar."""
    frames = carregar_frames(caminho, qtd_frames, 1)   # escala 1 = só recorta
    proporcao = largura_desejada / frames[0].get_width()
    altura_nova = int(frames[0].get_height() * proporcao)

    frames_ajustados = []
    for frame in frames:
        frames_ajustados.append(
            pygame.transform.scale(frame, (largura_desejada, altura_nova))
        )
    return frames_ajustados


# ---------- Duração de cada frame do player no menu (em milissegundos) ----------
# Vem do arquivo player_menu.ase: frame 1 = 2000, frame 2 = 2500, frame 3 = 2000, frame 4 = 2500
DURACOES_PLAYER_MENU = [2000, 2500, 2000, 2500]


def frame_por_duracao(frames, duracoes, tempo):
    """Escolhe o frame certo quando cada frame dura um tempo diferente."""
    tempo = tempo % sum(duracoes)   # volta pro começo quando termina (loop)
    for frame, duracao in zip(frames, duracoes):
        if tempo < duracao:
            return frame
        tempo -= duracao
    return frames[-1]


frames_player = carregar_frames("assets/imagens/player.png", 4, ESCALA_PLAYER)
frames_panda = carregar_frames("assets/imagens/panda_colectable.png", 2, ESCALA_PANDA)
frames_titulo = carregar_titulo("assets/imagens/titulomenu.png", QTD_FRAMES_TITULO, LARGURA_TITULO)
frames_player_sprite_menu = carregar_frames("assets/imagens/player_sprite_menu.png", 4, ESCALA_PLAYER)

# ---------- Sons ----------
som_coleta = pygame.mixer.Sound("assets/sons/collect_sound.ogg")
som_coleta.set_volume(0.7)   # 0.0 a 1.0

MUSICA_MENU = "assets/sons/menu_inicial.ogg"
MUSICA_JOGO = "assets/sons/game_loop.ogg"
MUSICA_GAME_OVER = "assets/sons/game_over.ogg"


def tocar_musica(caminho, repetir=-1):
    """Troca a música de fundo. repetir=-1 fica em loop, repetir=0 toca uma vez só."""
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(repetir)


def desenhar_texto_quebrado(texto, fonte, cor, centro_x, y_inicial, largura_max, espaco_linha=30):
    """Escreve o texto quebrando em várias linhas pra caber na largura máxima."""
    palavras = texto.split(" ")
    linhas = []
    linha = ""
    for palavra in palavras:
        teste = (linha + " " + palavra).strip()
        # fonte.size() mede a largura do texto sem precisar desenhar
        if fonte.size(teste)[0] <= largura_max:
            linha = teste
        else:
            linhas.append(linha)
            linha = palavra
    linhas.append(linha)

    for i, parte in enumerate(linhas):
        imagem = fonte.render(parte, True, cor)
        tela.blit(imagem, imagem.get_rect(center=(centro_x, y_inicial + i * espaco_linha)))


# Posição inicial e velocidade do player

x = largura // 2
y = altura // 2
velocidade = 7

# O "raio" agora vem do tamanho do sprite (usado na colisão)
raio = frames_player[0].get_width() // 2
raio_orb = frames_panda[0].get_width() // 2


async def main():
    global x, y

    score = 0
    high_score = 0
    tempo_de_vida_orb = 2000   # quanto tempo o panda fica na tela (em milissegundos)

    tempo_restante = TEMPO_INICIAL * 1000   # cronômetro em milissegundos

    # Estados do jogo: "inicio", "jogando" ou "game_over"
    estado = "inicio"

    # O panda começa num lugar sorteado
    orb_x = random.randint(raio_orb, largura - raio_orb)
    orb_y = random.randint(raio_orb, altura - raio_orb)
    momento_do_respawn = pygame.time.get_ticks()   # anota a hora do respawn

    tocar_musica(MUSICA_MENU)

    rodando = True
    while rodando:

        # dt = quanto tempo passou desde o frame anterior (em milissegundos)
        dt = relogio.tick(60)

        clicou = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicou = True

        tick_atual = pygame.time.get_ticks()   # hora de agora

        if estado == "jogando":
            # ---------- Cronômetro ----------
            tempo_restante -= dt
            if tempo_restante <= 0:
                tempo_restante = 0
                estado = "game_over"
                if score > high_score:
                    high_score = score
                tocar_musica(MUSICA_GAME_OVER, 0)   # toca uma vez só
            # ---------- Mover o player ----------
            teclas = pygame.key.get_pressed()

            # pra onde o teclado está empurrando (-1, 0 ou 1)
            dir_x = 0
            dir_y = 0
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                dir_x -= 1
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                dir_x += 1
            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                dir_y -= 1
            if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                dir_y += 1

            if dir_x != 0 or dir_y != 0:
                # Teclado
                movendo = True
                # na diagonal, reduz a velocidade pra não ficar mais rápido
                fator = 0.7071 if (dir_x != 0 and dir_y != 0) else 1
                x += dir_x * velocidade * fator
                y += dir_y * velocidade * fator
            elif pygame.mouse.get_pressed()[0]:
                # Mouse / toque
                movendo = True
                alvo_x, alvo_y = pygame.mouse.get_pos()
                if x < alvo_x:
                    x += velocidade
                if x > alvo_x:
                    x -= velocidade
                if y < alvo_y:
                    y += velocidade
                if y > alvo_y:
                    y -= velocidade
            else:
                movendo = False

            # não deixa o player sair da tela
            x = max(0, min(largura, x))
            y = max(0, min(altura, y))

            respawnar = False   # por padrão, não respawna

            # Colisão: se pegou o panda, ganha score, ganha tempo e ele respawna
            distancia_quadrada = (x - orb_x) ** 2 + (y - orb_y) ** 2
            if distancia_quadrada <= (raio + raio_orb) ** 2:
                score += 1
                som_coleta.play()
                tempo_restante += BONUS_PANDA * 1000
                if TEMPO_MAXIMO is not None:
                    tempo_restante = min(tempo_restante, TEMPO_MAXIMO * 1000)
                respawnar = True

            # Se o tempo de vida acabou, o panda também respawna (sem score)
            if tick_atual - momento_do_respawn >= tempo_de_vida_orb:
                respawnar = True

            # Respawn: novo lugar e o cronômetro do panda reinicia
            if respawnar:
                orb_x = random.randint(raio_orb, largura - raio_orb)
                orb_y = random.randint(raio_orb, altura - raio_orb)
                momento_do_respawn = tick_atual

            # Escolher o frame de cada sprite
            if movendo:
                frame_player = frames_player[(tick_atual // 120) % len(frames_player)]
            else:
                frame_player = frames_player[0]   # parado

            frame_panda = frames_panda[(tick_atual // 300) % len(frames_panda)]

            # Desenhar o jogo
            tela.fill(ROSA)
            tela.blit(frame_panda, frame_panda.get_rect(center=(orb_x, orb_y)))
            tela.blit(frame_player, frame_player.get_rect(center=(x, y)))

            texto = fonte.render(f"Score: {score}", True, BRANCO)
            tela.blit(texto, (10, 10))

            texto = fonte.render(f"High score: {high_score}", True, BRANCO)
            tela.blit(texto, (10, 40))

            segundos = tempo_restante / 1000
            cor_tempo = VERMELHO if segundos <= 3 else BRANCO   # fica vermelho no final
            texto = fonte.render(f"Tempo: {segundos:.1f}s", True, cor_tempo)
            tela.blit(texto, (largura - texto.get_width() - 10, 10))

        else:
            # ---------- Telas de início e de game over ----------
            tela.fill(ROSA)

            if estado == "inicio":
                # título (imagem) alternando entre os frames
                frame_titulo = frames_titulo[(tick_atual // 500) % len(frames_titulo)]
                tela.blit(frame_titulo, frame_titulo.get_rect(center=(largura // 2, altura // 2 - 100)))

                # enfeite: player e panda lado a lado
                frame_panda = frames_panda[(tick_atual // 300) % len(frames_panda)]
                frame_player_menu = frame_por_duracao(frames_player_sprite_menu, DURACOES_PLAYER_MENU, tick_atual)
                tela.blit(frame_player_menu, frame_player_menu.get_rect(center=(largura // 2 - 50, altura // 2 - 20)))
                tela.blit(frame_panda, frame_panda.get_rect(center=(largura // 2 + 50, altura // 2 - 20)))

                # texto quebrado em duas linhas pra caber na tela (margem de 20px de cada lado)
                desenhar_texto_quebrado("Pegue o máximo de pandas antes que o tempo acabe!", fonte, BRANCO, largura // 2, altura // 2 + 50, 460)

                texto = fonte.render("Clique para começar", True, BRANCO)
                tela.blit(texto, texto.get_rect(center=(largura // 2, altura // 2 + 120)))

            else:  # estado == "game_over"
                texto = fonte_grande.render("Fim de jogo", True, BRANCO)
                tela.blit(texto, texto.get_rect(center=(largura // 2, altura // 2 - 80)))

                texto = fonte.render(f"Seu score: {score}", True, BRANCO)
                tela.blit(texto, texto.get_rect(center=(largura // 2, altura // 2 - 10)))

                texto = fonte.render(f"High score: {high_score}", True, BRANCO)
                tela.blit(texto, texto.get_rect(center=(largura // 2, altura // 2 + 30)))

                texto = fonte.render("Clique para jogar de novo", True, BRANCO)
                tela.blit(texto, texto.get_rect(center=(largura // 2, altura // 2 + 90)))

            # Clicou? Começa uma partida nova (serve pro início e pro game over)
            if clicou:
                score = 0
                tempo_restante = TEMPO_INICIAL * 1000
                estado = "jogando"
                tocar_musica(MUSICA_JOGO)
                x = largura // 2
                y = altura // 2
                orb_x = random.randint(raio_orb, largura - raio_orb)
                orb_y = random.randint(raio_orb, altura - raio_orb)
                momento_do_respawn = pygame.time.get_ticks()

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
