import pygame
import sys
import math

# Inicialização
pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption("LEED com Imagem de Ponto")
clock = pygame.time.Clock()

# Cores
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRID_COLOR = (40, 40, 40)
LINE_COLOR = (100, 100, 255)
TEXT_COLOR = (200, 200, 200)
BLUE = (0, 0, 255)

# Carrega imagens dos pontos
ponto_imgs = {
    2: pygame.image.load("LEEDintense1.png").convert_alpha(),
    1: pygame.image.load("LEEDintense2.png").convert_alpha(),
    3: pygame.image.load("LEEDintense3.png").convert_alpha()
}

# Assume que todas as imagens têm o mesmo tamanho
img_w, img_h = ponto_imgs[1].get_rect().size

# Lista de pontos: (x, y, tipo)
pontos = []
ponto_selecionado = None
arrastando = False
tipo_ponto_atual = 3  # Padrão inicial: tipo 3

# Controles
mostrar_grade = True
mostrar_linhas = True  # Esta variável agora controlará se TODAS as conexões são mostradas
modo_manual = 1  # 1 para desenhar manualmente, 0 para gerar automaticamente
modo_angulo = False
pontos_angulo_info = [] # Usar info para guardar índice original
angulo_resultado = None
pos_angulo = None
arrastando_angulo = False  # Inicializa a variável aqui
ponto_selecionado_angulo = None # Inicializa a variável aqui

# Modo de medição de distância
modo_distancia = False
pontos_distancia = []
medicoes_distancia = []  # Armazena linhas de medição permanentes

# Histórico para desfazer
historico = []

# Edição de distância
editando_distancia = None
input_distancia = ""

# Fonte para texto
font = pygame.font.SysFont(None, 20)

def salvar_estado():
    historico.append(pontos[:])

def desfazer():
    if historico:
        global pontos
        pontos = historico.pop()

def espelhar_pontos(eixo='vertical'):
    novos_pontos = []
    for (x, y, tipo) in pontos:
        if eixo == 'vertical':
            novos_pontos.append((width - x, y, tipo))
        elif eixo == 'horizontal':
            novos_pontos.append((x, height - y, tipo))
        elif eixo == 'centro':
            novos_pontos.append((width - x, height - y, tipo))
    salvar_estado()
    pontos.extend(novos_pontos)

def desenha_grade(screen, espacamento=50):
    for x in range(0, width, espacamento):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, height))
    for y in range(0, height, espacamento):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (width, y))

def ponto_mais_proximo(pos):
    for i, (x, y, _) in enumerate(pontos):
        if (x - pos[0]) ** 2 + (y - pos[1]) ** 2 < 20**2:
            return i
    return None

def calcular_angulo(a, b, c):
    def vetor(u, v):
        return (v[0] - u[0], v[1] - u[1])

    def produto_escalar(u, v):
        return u[0]*v[0] + u[1]*v[1]

    def modulo(v):
        return math.hypot(v[0], v[1])

    ab = vetor(b, a)
    cb = vetor(b, c)
    modulo_ab = modulo(ab)
    modulo_cb = modulo(cb)
    if modulo_ab == 0 or modulo_cb == 0:
        return 0  # Evita divisão por zero se os pontos forem coincidentes
    cos_theta = produto_escalar(ab, cb) / (modulo_ab * modulo_cb)
    angulo = math.degrees(math.acos(max(min(cos_theta, 1), -1)))
    return angulo

# Se modo automático, adiciona pontos aqui
if not modo_manual:
    pontos = [
        (200, 200, 1), (300, 200, 2), (400, 200, 3),
        (200, 300, 1), (300, 300, 2), (400, 300, 3)
    ]

# Fonte para texto
font = pygame.font.SysFont(None, 20)

# Loop principal
running = True
while running:
    screen.fill(BLACK)

    if mostrar_grade:
        desenha_grade(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and modo_manual:
            pos = pygame.mouse.get_pos()
            i = ponto_mais_proximo(pos)
            if editando_distancia is None:
                if modo_angulo:
                    if i is not None:
                        if not any(p_info[3] == i for p_info in pontos_angulo_info): # Verifica se o ponto já foi selecionado para o ângulo
                            pontos_angulo_info.append((pontos[i][0], pontos[i][1], pontos[i][2], i)) # Guarda o índice original
                            if len(pontos_angulo_info) == 3:
                                print("Selecione um ponto para mover e ajustar o ângulo.")
                        elif len(pontos_angulo_info) == 3:
                            # Se já tem 3 pontos, ao clicar em um deles, prepara para arrastar esse ponto
                            for p_info in pontos_angulo_info:
                                if p_info[3] == i:
                                    ponto_selecionado_angulo = i
                                    arrastando_angulo = True
                                    break
                    else:
                        pontos_angulo_info = []
                elif modo_distancia:
                    if i is not None:
                        pontos_distancia.append(i)
                        if len(pontos_distancia) == 2:
                            editando_distancia = (pontos_distancia[0], pontos_distancia[1])
                            input_distancia = ""
                            pontos_distancia = []
                            modo_distancia = False
                else:
                    if i is not None:
                        ponto_selecionado = i
                        arrastando = True
                    else:
                        salvar_estado()
                        pontos.append((pos[0], pos[1], tipo_ponto_atual))
            else:
                editando_distancia = None

        elif event.type == pygame.MOUSEBUTTONUP:
            arrastando = False
            ponto_selecionado = None
            arrastando_angulo = False
            ponto_selecionado_angulo = None

        elif event.type == pygame.KEYDOWN:
            if editando_distancia is not None:
                # Lógica de edição de distância (igual ao seu código)
                if event.key == pygame.K_RETURN:
                    try:
                        nova_distancia = float(input_distancia)
                        i, j = editando_distancia
                        x1, y1, t1 = pontos[i]
                        x2, y2, t2 = pontos[j]
                        ang = math.atan2(y2 - y1, x2 - x1)
                        x2_novo = x1 + nova_distancia * math.cos(ang)
                        y2_novo = y1 + nova_distancia * math.sin(ang)
                        pontos[j] = (x2_novo, y2_novo, t2)
                    except ValueError:
                        print("Entrada inválida")
                    input_distancia = ""
                    editando_distancia = None
                elif event.key == pygame.K_BACKSPACE:
                    input_distancia = input_distancia[:-1]
                else:
                    input_distancia += event.unicode
            else:
                if event.key == pygame.K_g:
                    mostrar_grade = not mostrar_grade
                elif event.key == pygame.K_l:
                    mostrar_linhas = not mostrar_linhas # Agora controla todas as conexões
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    desfazer()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    tipo_ponto_atual = int(event.unicode)
                    print(f"Selecionado tipo de ponto: {tipo_ponto_atual}")
                elif event.key == pygame.K_4:
                    modo_angulo = not modo_angulo
                    pontos_angulo_info = [] # Reinicia a seleção de pontos para o ângulo
                    angulo_resultado = None
                    pos_angulo = None
                    print("Modo ângulo:", "Ativo" if modo_angulo else "Desativado")
                elif event.key == pygame.K_d:
                    modo_distancia = not modo_distancia
                    pontos_distancia = []
                    print("Modo distância:", "Ativo" if modo_distancia else "Desativado")
                    if modo_distancia and len(pontos_distancia) == 1:
                        i = pontos_distancia[0]
                        x1, y1, _ = pontos[i]
                        x2, y2 = pygame.mouse.get_pos()
                        pygame.draw.line(screen, BLUE, (x1, y1), (x2, y2), 1)
                        dist = math.hypot(x2 - x1, y2 - y1)
                        dist_text = font.render(f"{dist:.1f}", True, BLUE)
                        screen.blit(dist_text, ((x1 + x2) // 2 + 10, (y1 + y2) // 2 - 10))
                elif event.key == pygame.K_c:
                    medicoes_distancia = []  # Limpa todas as medições

    # Movimento normal dos pontos
    if arrastando and ponto_selecionado is not None:
        x, y, t = pontos[ponto_selecionado]
        pontos[ponto_selecionado] = (*pygame.mouse.get_pos(), t)

    # Movimento de pontos no modo de ângulo
    if arrastando_angulo and ponto_selecionado_angulo is not None and modo_angulo and len(pontos_angulo_info) == 3:
        new_x, new_y = pygame.mouse.get_pos()
        # Atualiza as coordenadas do ponto selecionado
        index_para_atualizar = ponto_selecionado_angulo
        tipo_do_ponto = pontos[index_para_atualizar][2]
        pontos[index_para_atualizar] = (new_x, new_y, tipo_do_ponto)

        # Recalcula o ângulo com as novas posições
        coords_angulo = [(pontos[i][0], pontos[i][1]) for _, _, _, i in pontos_angulo_info]
        if len(coords_angulo) == 3:
            angulo_resultado = calcular_angulo(*coords_angulo)
            pos_angulo = coords_angulo[1] # O vértice do ângulo é o segundo ponto na lista

    # Conecta TODOS os pontos entre si e mostra as distâncias
    if mostrar_linhas and len(pontos) > 1:
        for i in range(len(pontos)):
            for j in range(i + 1, len(pontos)):
                p1 = (pontos[i][0], pontos[i][1])
                p2 = (pontos[j][0], pontos[j][1])
                pygame.draw.line(screen, LINE_COLOR, p1, p2, 1)
                dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
                dist_text = font.render(f"{dist:.1f}", True, TEXT_COLOR)
                rect = dist_text.get_rect(center=(cx, cy))
                screen.blit(dist_text, rect)
                # Opcional: Lógica para edição de distância ao clicar na linha (pode ficar complexo com muitas linhas)
                # if pygame.mouse.get_pressed()[0] and rect.collidepoint(pygame.mouse.get_pos()):
                #     editando_distancia = (i, j) # Precisa adaptar a lógica de índice aqui
                #     input_distancia = ""

    # Desenha linhas de medição de distância permanentes
    for (p1, p2, dist) in medicoes_distancia:
        pygame.draw.line(screen, RED, p1, p2, 2)
        cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
        dist_text = font.render(f"{dist:.1f}", True, RED)
        screen.blit(dist_text, (cx + 10, cy - 10))

    # Desenha os pontos
    for x, y, t in pontos:
        img = ponto_imgs.get(t, ponto_imgs[3])
        screen.blit(img, (x - img_w // 2, y - img_h // 2))

    # Destaca ponto selecionado para arrastar normalmente
    if ponto_selecionado is not None and not arrastando_angulo:
        x, y, _ = pontos[ponto_selecionado]
        pygame.draw.circle(screen, RED, (x, y), 15, 2)
    # Destaca ponto selecionado para arrastar no modo de ângulo
    elif ponto_selecionado_angulo is not None and arrastando_angulo and modo_angulo:
        x, y, _ = pontos[ponto_selecionado_angulo]
        pygame.draw.circle(screen, BLUE, (x, y), 15, 2)

    # Mostra o ângulo na tela
    if angulo_resultado is not None and pos_angulo:
        texto_angulo = font.render(f"{angulo_resultado:.2f}°", True, GREEN)
        screen.blit(texto_angulo, (pos_angulo[0] + 10, pos_angulo[1] - 10))

    # Desenha linhas temporárias de medição de ângulo
    if modo_angulo and len(pontos_angulo_info) > 0:
        coords_desenho_angulo = [(p[0], p[1]) for p in pontos_angulo_info]
        for i, coord in enumerate(coords_desenho_angulo):
            pygame.draw.circle(screen, GREEN, coord, 6)
            if i > 0:
                pygame.draw.line(screen, GREEN, coords_desenho_angulo[i-1], coord, 1)

    # Mostra valor sendo digitado para distância
    if editando_distancia is not None:
        cx, cy = pygame.mouse.get_pos()
        texto_input = font.render(f"{input_distancia}", True, TEXT_COLOR)
        screen.blit(texto_input, (cx + 10, cy - 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()