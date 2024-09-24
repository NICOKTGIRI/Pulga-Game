import pygame
import sys
import random

from pulga2 import *

class Game:
    def __init__(self):
        pygame.init()

        # Definición de colores
        self.rojo = (209, 36, 5)
        self.verde = (50, 205, 54)
        self.amarillo = (240, 130, 14)
        self.azulOsc = (9, 20, 70)
        self.fondoGRIS = (80, 80, 80)
        self.fondoCIELOAzul = (92, 197, 222)
        self.blancoNUBE = (249, 249, 249)

        # Configuración de la pantalla y FPS
        self.RESOLUCION = (800, 700)
        self.FPS = 50

        # Tamaño de las baldosas (tiles)
        self.TX = 50
        self.TY = 50
        self.FILAS = int(self.RESOLUCION[1] / self.TY)
        self.COLUMNAS = int(self.RESOLUCION[0] / self.TX)

        # Configuración del juego
        self.GRAVEDAD = 1
        self.MAX_PLATAFORMAS = 7
        self.contadorPlataformas = 0
        self.plataformasSaltadas = 0
        self.anchoPlataf_nivel = [(2, 7), (2, 6), (2, 5), (2, 5),
                                    (2, 5), (2, 4), (2, 4), (2, 4)]

        # Estados del juego
        self.programaEjecutandose = True
        self.presentacion = True
        self.enJuego = False
        self.gameOver = False

        # Inicialización de Pygame
        self.pantalla = pygame.display.set_mode(self.RESOLUCION)
        self.reloj = pygame.time.Clock()

        # Carga de imágenes de fondo
        self.scrollImg1 = pygame.image.load('./assets/img/scrollBg1.png').convert()
        self.scrollImg2 = pygame.image.load('./assets/img/scrollBg2.png').convert()

        # Configuración del scroll
        self.SCROLL_THRESH = 200
        self.scroll = 0
        self.bgScroll = 0

        # Carga de sonidos
        self.sonido_salto = pygame.mixer.Sound("./assets/sound/jumpbros.ogg")
        self.sonido_salto.set_volume(0.3)
        self.sonido_gameOver = pygame.mixer.Sound('./assets/sound/gameoveretro.ogg')
        self.sonido_gameOver.set_volume(0.7)

        # Música de fondo
        pygame.mixer.music.load("./assets/sound/mario_tuberias.ogg")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(loops=-1)

        # Grupos de sprites
        self.lista_spritesAdibujar = pygame.sprite.Group()
        self.lista_plataformas = pygame.sprite.Group()

        # Fuente para el texto
        self.font = pygame.font.Font(None, 36)

        # Inicialización de instancias
        self.instancias()

    def instancias(self):
        # Reinicia el contador de plataformas saltadas
        self.plataformasSaltadas = 0
        
        # Crea la instancia del jugador (pulga)
        x = self.RESOLUCION[0] // 2
        y = self.RESOLUCION[1] - self.TY * 3 
        self.pulga = Pulga(self, x, y, self.TX, self.TY, (40, 40))

        # Crea la plataforma inicial (suelo)
        y = self.FILAS - 1
        self.plataforma = Plataforma(self, 0, y, self.COLUMNAS, 0, self.TX, self.TY, (self.TX, self.TY))
        self.lista_spritesAdibujar.add(self.plataforma)
        self.lista_plataformas.add(self.plataforma)
        self.contadorPlataformas += 1

    def reInstanciasPlataformas(self):
        # Crea nuevas plataformas si hay menos del máximo permitido
        if len(self.lista_plataformas) < self.MAX_PLATAFORMAS:
            self.contadorPlataformas += 1

            # Genera posición y ancho aleatorios para la nueva plataforma
            x = random.randrange(self.COLUMNAS - 2)
            ancho = random.randrange(2, 7)

            # Calcula la posición vertical de la nueva plataforma
            ultimaPlataforma = min(plataforma.rect.y for plataforma in self.lista_plataformas) // self.TY 
            espacioEntrePlataformas = random.randrange(2) + 2
            y = ultimaPlataforma - espacioEntrePlataformas

            # Asigna velocidad aleatoria a la plataforma
            velX_rnd = random.choice([0, 1, -1])

            # Crea la nueva plataforma y la añade a los grupos de sprites
            self.plataforma = Plataforma(self, x, y, ancho, velX_rnd, self.TX, self.TY, (self.TX, self.TY))
            self.lista_spritesAdibujar.add(self.plataforma)
            self.lista_plataformas.add(self.plataforma)

    def obtenerGrafico(self, nombrePng, escala):
        # Carga y escala una imagen
        img = pygame.image.load('./assets/img/' + nombrePng).convert()
        image = pygame.transform.scale(img, escala)
        image.set_colorkey((255, 255, 255))
        rect = image.get_rect()

        return (image, rect)

    def dibujaScroll(self):
        # Dibuja el fondo con efecto de scroll
        resY = self.RESOLUCION[1]
        self.bgScroll += self.scroll

        if self.bgScroll >= resY * 2:
            self.bgScroll = 0

        self.pantalla.blit(self.scrollImg1, (0, 0 + self.bgScroll))
        self.pantalla.blit(self.scrollImg2, (0, -resY + self.bgScroll))
        self.pantalla.blit(self.scrollImg1, (0, -resY * 2 + self.bgScroll))

    def update(self):
        # Actualiza el juego en cada frame
        pygame.display.set_caption(str(int(self.reloj.get_fps())))

        self.reInstanciasPlataformas()

        self.scroll = self.pulga.actualiza()
        self.dibujaScroll()

        self.lista_spritesAdibujar.update()
        self.lista_spritesAdibujar.draw(self.pantalla)

        self.pulga.dibuja(self.pantalla)

        # Dibuja el contador de plataformas saltadas
        texto_contador = self.font.render(f"Plataformas: {self.plataformasSaltadas}", True, self.rojo)
        self.pantalla.blit(texto_contador, (self.RESOLUCION[0] - 200, 10))

        if self.gameOver:
            self.dibujar_boton_reintentar()
        
        pygame.display.flip()
        self.reloj.tick(self.FPS)

    def dibujar_boton_reintentar(self):
        # Dibuja el botón de reintentar cuando el juego termina
        boton_rect = pygame.Rect(self.RESOLUCION[0] // 2 - 75, self.RESOLUCION[1] // 2 - 25, 150, 50)
        pygame.draw.rect(self.pantalla, self.verde, boton_rect)
        texto_boton = self.font.render("Reintentar", True, self.azulOsc)
        texto_rect = texto_boton.get_rect(center=boton_rect.center)
        self.pantalla.blit(texto_boton, texto_rect)

    def check_event(self):
        # Maneja los eventos de Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_RETURN and self.presentacion:
                    self.presentacion = False
                    self.enJuego = True

            elif event.type == pygame.MOUSEBUTTONDOWN and self.gameOver:
                if pygame.Rect(self.RESOLUCION[0] // 2 - 75, self.RESOLUCION[1] // 2 - 25, 150, 50).collidepoint(event.pos):
                    self.reiniciar_juego()

    def reiniciar_juego(self):
        # Reinicia el juego
        self.gameOver = False
        self.enJuego = True
        self.lista_spritesAdibujar.empty()
        self.lista_plataformas.empty()
        self.instancias()

    def buclePrincipal(self):
        # Bucle principal del juego
        while self.programaEjecutandose:
            self.check_event()
            self.update()

if __name__ == '__main__':
    game = Game()
    game.buclePrincipal()