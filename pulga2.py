import pygame
import random

#---------------------------------------------------------------
# Clases:
#			Pulga 		(No sprite)
#			Plataforma 	(Sprite)
#			FlappyBird	(Sprite)
#			Bicho 		(Sprite)
#			Textos		(Sprite)
#			Decorativos (Sprite)
#--------------------------------------------------------------					
class Pulga():
	def __init__(self, game, x, y, TX, TY, escala):
		self.game = game 

		self.lista_imagenes = []

		for i in range(3):
			nombrePng = 'pulga{}.png'.format(i + 1)
			image_rect = self.game.obtenerGrafico(nombrePng, escala)
			self.lista_imagenes.append(image_rect[0])

		self.image = self.lista_imagenes[2]
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

		self.PlataformaMETA = -999

		self.acelX = 0.0
		self.velX = 7
		self.velY = -20
		self.flip = False


	def actualiza(self):
		if not self.game.enJuego:
			return 0

		if self.velY < 0:
			self.image = self.lista_imagenes[1]
		else:
			self.image = self.lista_imagenes[0]

		# --------------------------------------
		# 	RESETS (scroll, dx, dy)
		# --------------------------------------
		scroll = 0
		dx = 0
		dy = 0

		dx = self.leerTeclado(dx)

		self.velY += self.game.GRAVEDAD
		dy += self.velY

		dx = self.checkLimitesHor(dx)
		dy = self.checkColisionPlataformas(dy)
		dy = self.checkCaerAlVacio(dy)
		self.checkColisionPlataformaMETA()
		scroll = self.checkScrollThresh(scroll, dy)

		self.rect.x += dx
		self.rect.y += dy + scroll 

		if self.acelX > 0:
			self.acelX -= 1

		return scroll 


	def dibuja(self, pantalla):
		if self.game.presentacion:
			movim = self.game.TY + self.rect.height
			pantalla.blit(self.image, (self.rect.x, self.game.RESOLUCION[1] - movim))

		else:
			pantalla.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x, self.rect.y))


	def checkScrollThresh(self, scroll, dy):
		if self.rect.top <= self.game.SCROLL_THRESH:
			if self.velY < 0:
				scroll = -dy 

		return scroll


	def checkColisionPlataformas(self, dy):
		for plataf in self.game.lista_plataformas:
			if plataf.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
				if self.rect.bottom < plataf.rect.centery:
					if self.velY > 0:
						self.rect.bottom = plataf.rect.top
						dy = 0
						self.velY = -20
						self.game.sonido_salto.play()

		return dy 


	def checkCaerAlVacio(self, dy):
		if self.rect.bottom + dy > self.game.RESOLUCION[1] * 1.5:
			dy = 0
			self.game.gameOver = True
			self.game.enJuego = False
			self.game.sonido_gameOver.play()

		return dy


	def checkLimitesHor(self, dx):
		if self.rect.left + dx < 0:
			dx = -self.rect.left 

		if self.rect.right + dx > self.game.RESOLUCION[0]:
			dx = self.game.RESOLUCION[0] - self.rect.right 

		return dx


	def checkColisionPlataformaMETA(self):
		if self.rect.bottom <= self.PlataformaMETA and not self.game.nivelSuperado:
			self.game.nivelSuperado = True
			self.game.sonido_pacIntermision.play()
			print('nivel superado!')


	def leerTeclado(self, dx):
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
		super().__init__()
		self.game = game 

		self.lista_imagenes = []

		for i in range(6):
			nombrePng = 'tile{}.png'.format(i + 1)
			image_rect = self.game.obtenerGrafico(nombrePng, escala)
			self.lista_imagenes.append(image_rect[0])

		escalaX = escala[0]
		escalaY = escala[1]

		self.image = pygame.Surface((ancho * escalaX, escalaY))
		self.image.set_colorkey((0, 0, 0))

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

		self.rect = self.image.get_rect()
		self.rect.topleft = (x * TX, y * TY)

		self.ancho = ancho
		self.velX = velX_rnd


	def update(self):
		self.rect.y += self.game.scroll
		self.rect.x += self.velX

		if (self.rect.right > self.game.RESOLUCION[0] and self.velX > 0) or (self.rect.x < 0 and self.velX < 0):
			self.velX = -self.velX

		# if self.ancho == self.game.COLUMNAS:
		# 	self.game.pulga.plataformaMETA = self.rect.y 

		if self.rect.top > self.game.RESOLUCION[1]:
			self.kill()







