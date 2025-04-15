import pygame
import sys

# Inicialização
pygame.init()
size = width, height = 800, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("LEED com Imagem de Ponto")
clock = pygame.time.Clock()

# Cores
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Carrega a imagem do ponto
ponto_img = pygame.image.load("ponto.png").convert_alpha()
ponto_rect = ponto_img.get_rect()
img_w, img_h = ponto_rect.width, ponto_rect.height

# Lista de pontos
pontos = []
ponto_selecionado = None
arrastando = False

def ponto_mais_proximo(pos):
    for i, (x, y) in enumerate(pontos):
        if (x - pos[0]) ** 2 + (y - pos[1]) ** 2 < 20**2:
            return i
    return None

# Loop principal
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            i = ponto_mais_proximo(pos)
            if i is not None:
                ponto_selecionado = i
                arrastando = True
            else:
                pontos.append(pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            arrastando = False
            ponto_selecionado = None

    if arrastando and ponto_selecionado is not None:
        pontos[ponto_selecionado] = pygame.mouse.get_pos()

    # Desenha os pontos com a imagem
    for x, y in pontos:
        screen.blit(ponto_img, (x - img_w // 2, y - img_h // 2))

    # Destaca ponto selecionado (círculo vermelho)
    if ponto_selecionado is not None:
        x, y = pontos[ponto_selecionado]
        pygame.draw.circle(screen, RED, (x, y), 15, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
