import pygame
import random

class Pulga():
    def __init__(self, game, x, y, TX, TY, escala):
        # Inicialización de la clase Pulga
        self.game = game 

        # Lista para almacenar las imágenes de la pulga
        self.lista_imagenes = []

        # Carga las imágenes de la pulga
        for i in range(3):
            nombrePng = 'pulga{}.png'.format(i + 1)
            image_rect = self.game.obtenerGrafico(nombrePng, escala)
            self.lista_imagenes.append(image_rect[0])

        # Configura la imagen inicial y su posición
        self.image = self.lista_imagenes[2]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Inicializa variables de movimiento
        self.acelX = 0.0
        self.velX = 7
        self.velY = -20
        self.flip = False

    def actualiza(self):
        # Actualiza la posición y estado de la pulga
        if not self.game.enJuego:
            return 0

        # Cambia la imagen según el movimiento vertical
        if self.velY < 0:
            self.image = self.lista_imagenes[1]
        else:
            self.image = self.lista_imagenes[0]

        scroll = 0
        dx = 0
        dy = 0

        # Lee el teclado para movimiento horizontal
        dx = self.leerTeclado(dx)

        # Aplica gravedad
        self.velY += self.game.GRAVEDAD
        dy += self.velY

        # Comprueba límites y colisiones
        dx = self.checkLimitesHor(dx)
        dy = self.checkColisionPlataformas(dy)
        dy = self.checkCaerAlVacio(dy)
        scroll = self.checkScrollThresh(scroll, dy)

        # Actualiza la posición
        self.rect.x += dx
        self.rect.y += dy + scroll 

        # Reduce la aceleración horizontal
        if self.acelX > 0:
            self.acelX -= 1

        return scroll 

    def dibuja(self, pantalla):
        # Dibuja la pulga en la pantalla
        if self.game.presentacion:
            movim = self.game.TY + self.rect.height
            pantalla.blit(self.image, (self.rect.x, self.game.RESOLUCION[1] - movim))
        else:
            pantalla.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x, self.rect.y))

    def checkScrollThresh(self, scroll, dy):
        # Comprueba si la pulga ha alcanzado el umbral de desplazamiento
        if self.rect.top <= self.game.SCROLL_THRESH:
            if self.velY < 0:
                scroll = -dy 
        return scroll

    def checkColisionPlataformas(self, dy):
        # Comprueba colisiones con plataformas
        for plataf in self.game.lista_plataformas:
            if plataf.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.rect.bottom < plataf.rect.centery:
                    if self.velY > 0:
                        self.rect.bottom = plataf.rect.top
                        dy = 0
                        self.velY = -20
                        self.game.sonido_salto.play()
                        self.game.plataformasSaltadas += 1
        return dy 

    def checkCaerAlVacio(self, dy):
        # Comprueba si la pulga ha caído al vacío
        if self.rect.top > self.game.RESOLUCION[1]:
            dy = 0
            self.game.gameOver = True
            self.game.enJuego = False
            self.game.sonido_gameOver.play()
        return dy

    def checkLimitesHor(self, dx):
        # Comprueba los límites horizontales de la pantalla
        if self.rect.left + dx < 0:
            dx = -self.rect.left 
        if self.rect.right + dx > self.game.RESOLUCION[0]:
            dx = self.game.RESOLUCION[0] - self.rect.right 
        return dx

    def leerTeclado(self, dx):
        # Lee las teclas para el movimiento horizontal
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_LEFT]:
            self.acelX += 2 
            dx = -(self.velX + self.acelX)
            self.flip = True
        elif tecla[pygame.K_RIGHT]:
            self.acelX += 2
            dx = self.velX + self.acelX
            self.flip = False
        return dx 

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, game, x, y, ancho, velX_rnd, TX, TY, escala):
        # Inicialización de la clase Plataforma
        super().__init__()
        self.game = game 

        # Lista para almacenar las imágenes de las plataformas
        self.lista_imagenes = []

        # Carga las imágenes de las plataformas
        for i in range(6):
            nombrePng = 'tile{}.png'.format(i + 1)
            image_rect = self.game.obtenerGrafico(nombrePng, escala)
            self.lista_imagenes.append(image_rect[0])

        escalaX = escala[0]
        escalaY = escala[1]

        # Crea la imagen de la plataforma
        self.image = pygame.Surface((ancho * escalaX, escalaY))
        self.image.set_colorkey((0, 0, 0))

        # Dibuja la plataforma según su tipo (estática o móvil)
        if velX_rnd == 0:
            for i in range(ancho):
                if i == 0 and ancho < self.game.COLUMNAS:
                    self.image.blit(self.lista_imagenes[1], (i * escalaX, 0))
                elif i == ancho - 1 and ancho < self.game.COLUMNAS:
                    self.image.blit(self.lista_imagenes[2], (i * escalaX, 0))
                else:
                    self.image.blit(self.lista_imagenes[0], (i * escalaX, 0))
        else:
            for i in range(ancho):
                self.image.blit(self.lista_imagenes[5], (i * escalaX, 0))

        # Configura la posición de la plataforma
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TX, y * TY)

        self.ancho = ancho
        self.velX = velX_rnd

    def update(self):
        # Actualiza la posición de la plataforma
        self.rect.y += self.game.scroll
        self.rect.x += self.velX

        # Invierte la dirección si alcanza los bordes de la pantalla
        if (self.rect.right > self.game.RESOLUCION[0] and self.velX > 0) or (self.rect.x < 0 and self.velX < 0):
            self.velX = -self.velX

        # Elimina la plataforma si sale de la pantalla por abajo
        if self.rect.top > self.game.RESOLUCION[1]:
            self.kill()