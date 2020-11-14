import pygame
import time
import periscope
import numpy as np

pygame.init()

pygame.mouse.set_visible(False)

display_surface = pygame.display.set_mode((480, 320), pygame.HWSURFACE | pygame.DOUBLEBUF)

color_fg, color_bg = pygame.Color(0xfff32bff), pygame.Color(0x1e2320ff)
display_surface.fill(color_bg)
pygame.display.flip()

width, height = 20, 20
another_surface = pygame.Surface((width, height))
another_surface.fill(color_fg)

display_surface.blit(another_surface, (10, 10))
pygame.display.flip()

font_name, font_size = "inconsolata", 32
font = pygame.font.SysFont(font_name, font_size)
text_surface = font.render("Yo yo yo", True, color_fg, color_bg)
display_surface.blit(text_surface, (240,150))
pygame.display.flip()

x = np.linspace(0.0, 2*np.pi, 100)
line_plot_0 = periscope.LinePlot(120, 80)
line_plot_0.set_content(x, np.sin(x))
display_surface.blit(line_plot_0.surface, (50,50))
pygame.display.flip()

while True:
	time.sleep(1)
