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

# Carrega imagens dos pontos
ponto_imgs = {
    1: pygame.image.load("LEEDintense1.png").convert_alpha(),
    2: pygame.image.load("LEEDintense2.png").convert_alpha(),
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
mostrar_linhas = True
modo_manual = 1  # 1 para desenhar manualmente, 0 para gerar automaticamente
modo_angulo = False
pontos_angulo = []
angulo_resultado = None
pos_angulo = None

# Modo de medição de distância
modo_distancia = False
pontos_distancia = []
medicoes_distancia = []  # Armazena linhas de medição permanentes

# Histórico para desfazer
historico = []

# Edição de distância
editando_distancia = None
input_distancia = ""

# Edição de ângulo
editando_angulo = False


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
    cos_theta = produto_escalar(ab, cb) / (modulo(ab) * modulo(cb))
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
                        pontos_angulo.append(pontos[i])
                        if len(pontos_angulo) == 3:
                            angulo_resultado = calcular_angulo(*[(x, y) for x, y, _ in pontos_angulo])
                            pos_angulo = pontos_angulo[1][:2]
                            print(f"Ângulo: {angulo_resultado:.2f}°")
                            pontos_angulo = []
                    else:
                        pontos_angulo = []
                        angulo_resultado = None
                        pos_angulo = None
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

        elif event.type == pygame.KEYDOWN:
            if editando_distancia is not None:
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
                    mostrar_linhas = not mostrar_linhas
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    desfazer()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    tipo_ponto_atual = int(event.unicode)
                    print(f"Selecionado tipo de ponto: {tipo_ponto_atual}")
                elif event.key == pygame.K_4:
                    modo_angulo = not modo_angulo
                    pontos_angulo = []
                    angulo_resultado = None
                    pos_angulo = None
                    print("Modo ângulo:", "Ativo" if modo_angulo else "Desativado")
                elif event.key == pygame.K_d:
                    modo_distancia = not modo_distancia
                    pontos_distancia = []
                    print("Modo distância:", "Ativo" if modo_distancia else "Desativado")
                elif event.key == pygame.K_c:
                    medicoes_distancia = []  # Limpa todas as medições

    if arrastando and ponto_selecionado is not None:
        x, y, t = pontos[ponto_selecionado]
        pontos[ponto_selecionado] = (*pygame.mouse.get_pos(), t)

    # Conecta os pontos com linhas e mostra distâncias
    if mostrar_linhas and len(pontos) > 1:
        coords = [(x, y) for x, y, _ in pontos]
        pygame.draw.lines(screen, LINE_COLOR, False, coords, 1)

        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            dist = math.hypot(x2 - x1, y2 - y1)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            dist_text = font.render(f"{dist:.1f}", True, TEXT_COLOR)
            rect = dist_text.get_rect(center=(cx, cy))
            screen.blit(dist_text, rect)
            if pygame.mouse.get_pressed()[0] and rect.collidepoint(pygame.mouse.get_pos()):
                editando_distancia = (i, i + 1)
                input_distancia = ""

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

    # Destaca ponto selecionado
    if ponto_selecionado is not None:
        x, y, _ = pontos[ponto_selecionado]
        pygame.draw.circle(screen, RED, (x, y), 15, 2)

    # Mostra o ângulo na tela
    if angulo_resultado and pos_angulo:
        texto_angulo = font.render(f"{angulo_resultado:.2f}°", True, GREEN)
        screen.blit(texto_angulo, (pos_angulo[0] + 10, pos_angulo[1] - 10))

    # Desenha linhas temporárias de medição de ângulo
    if modo_angulo and len(pontos_angulo) > 0:
        pygame.draw.circle(screen, GREEN, pontos_angulo[0][:2], 6)
        if len(pontos_angulo) > 1:
            pygame.draw.line(screen, GREEN, pontos_angulo[0][:2], pontos_angulo[1][:2], 1)
            pygame.draw.circle(screen, GREEN, pontos_angulo[1][:2], 6)
        if len(pontos_angulo) == 3:
            pygame.draw.line(screen, GREEN, pontos_angulo[1][:2], pontos_angulo[2][:2], 1)
            pygame.draw.circle(screen, GREEN, pontos_angulo[2][:2], 6)

    # Mostra valor sendo digitado para distância
    if editando_distancia is not None:
        cx, cy = pygame.mouse.get_pos()
        texto_input = font.render(f"{input_distancia}", True, TEXT_COLOR)
        screen.blit(texto_input, (cx + 10, cy - 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
