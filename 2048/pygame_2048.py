import pygame as pg
import time
import os
import random
import numpy as np
from PIL import Image, ImageGrab
import cv2
import concurrent.futures

# my modules
from ft_pg.ft_pg_init import *
from ft_pg.ft_pg_gui import *
from env_2048 import *
from utils import *
from ft_pg.ft_pg_music_player import *
from ddqn_agent import DDQNAgent


BG = (40, 40, 40)
BLACK_TXT = (3, 3, 3)
WHITE_TXT = (200, 200, 200)


class Pygame2048(object):

	def __init__(self):

		self.screen, self.clock, self.fonts = ft_pg_init()
		self.param = {"fps": 60}
		self.running = True

		self.ft_gui = FtPgGui(self.screen)
		self.music_player = MusicPlayer(volume=0)

		self._init_variables()
		self._load_scene(0)

	def _init_variables(self, img_path="img"):
		self.scene = None
		self.env_2048 = Env2048()
		self.background_scene_exec = {2 : [], 3: []}
		self.param["interface_sep"] = 20
		self.surface = {"fire_effect": [pg.image.load(f"{img_path}/{x}") for x  in os.listdir(img_path) if ".png" in x and "fire_effect" in x],
						"water_effect": [pg.image.load(f"{img_path}/{x}") for x  in os.listdir(img_path) if ".png" in x and "water_effect" in x],
						"meme_img": [pg.image.load(f"{img_path}/{x}") for x  in os.listdir(img_path) if ".png" in x and "meme_img" in x],
						"game_over": [pg.image.load(f"{img_path}/{x}") for x  in os.listdir(img_path) if ".png" in x and "game_over" in x]}

	def quit(self):
		self.background_scene_exec = {2 : [], 3: []}
		self.running = False

# SCENES_LIST: [menu_principal : 0, game: 1, bot_show: 2, bot_train: 3]

# _______________________________________________________________________________________________________________________________
# FUNCS call scene funcs with num
	def _load_scene(self, num):
		funcs = [self._load_scene_0, self._load_scene_1, self._load_scene_2, self._load_scene_3]
		funcs[num]()

	def _event_scene(self, num, event):
		funcs = [self._event_scene_0, self._event_scene_1, self._event_scene_2, self._event_scene_3]
		funcs[num](event)

	def _display_scene(self, num):
		funcs = [self._display_scene_0, self._display_scene_1, self._display_scene_2, self._display_scene_3]
		funcs[num]()
# -------------------------------------------------------------------------------------------------------------------------------

# _______________________________________________________________________________________________________________________________
# # LOAD surface 2048 board
	def _get_surface_2048(self, state, surface_size, border_radius=6, border_width=2, font_size=29, background_color=(245,245,220), board_size_percent=90, fusion=[], game_done=False):
		"""
		Args:
			state -> state of the 2048 game in 1D array
			surface_size -> size of the generated surface in tuple (width, height)
			background_color -> color of the background
			board_size_percent -> size of the board on the surface
		Return:
			surface (pygame.Surface): surface to blit on pygame screen
		"""
		ret_surface = pg.Surface(surface_size)
		ret_surface.fill(background_color)
		rounded_surface = pg.Surface(surface_size, pg.SRCALPHA)
		pg.draw.rect(rounded_surface, background_color, (0, 0, surface_size[0], surface_size[1]), border_radius=border_radius)
		ret_surface = ret_surface.convert_alpha()
		ret_surface.blit(rounded_surface, (0, 0), None, pg.BLEND_RGBA_MIN)
		surface_size = (board_size_percent * surface_size[0] / 100, board_size_percent * surface_size[1] / 100)


		game_size = isqrt(len(state))
		tuile_size = (int(surface_size[0] / game_size), int(surface_size[1] / game_size))
		marge_for_centered = (max(0, int(surface_size[0] - tuile_size[0] * game_size)), max(0, int(surface_size[1] - tuile_size[1] * game_size)))
		x_pos, y_pos = 0, 0

		surface = pg.Surface(surface_size)
		surface.fill(background_color)
		rounded_surface = pg.Surface(surface_size, pg.SRCALPHA)
		pg.draw.rect(rounded_surface, background_color, (0, 0, surface_size[0], surface_size[1]), border_radius=border_radius)
		surface = surface.convert_alpha()
		surface.blit(rounded_surface, (0, 0), None, pg.BLEND_RGBA_MIN)

		for y in range(game_size):
			y_pos = y * tuile_size[1] + marge_for_centered[1]
			for x in range(game_size):
				x_pos = x * tuile_size[0] + marge_for_centered[0]
				game_ctn = game_size * y + x

				tuile_surface = pg.Surface(tuile_size)
				color = ((state[game_ctn] * 50 + 200) % 256, (state[game_ctn] * 80 + 200) % 256, (state[game_ctn] * 60 + 200) % 256)
				tuile_surface.fill(color)
				rounded_surface = pg.Surface(tuile_size, pg.SRCALPHA)
				pg.draw.rect(rounded_surface, background_color, (0, 0, tuile_size[0], tuile_size[1]), border_radius=border_radius)
				tuile_surface = tuile_surface.convert_alpha()
				tuile_surface.blit(rounded_surface, (0, 0), None, pg.BLEND_RGBA_MIN)

				pg.draw.rect(tuile_surface, (3, 3, 3), pg.Rect(0, 0, tuile_surface.get_size()[0], tuile_surface.get_size()[1]),
														width=border_width, border_radius=border_radius)

				if state[game_ctn] != 0:
					color = WHITE_TXT if color[0] < 40 & color[1] < 40 & color[2] < 40 else BLACK_TXT
					text_surface = self.fonts[29].render(str(state[game_ctn]), True, color)
					tuile_surface.blit(text_surface,
						(tuile_size[0] / 2 - text_surface.get_size()[0] / 2, tuile_size[1] / 2 - text_surface.get_size()[1] / 2))
				

				surface.blit(tuile_surface, (x_pos, y_pos))

		for y in range(game_size):
			y_pos = y * tuile_size[1] + marge_for_centered[1]
			for x in range(game_size):
				x_pos = x * tuile_size[0] + marge_for_centered[0]
				game_ctn = game_size * y + x
				if game_ctn in fusion and random.randint(0, 0) == 0 and state[game_ctn] == max(state):
					element_effect = random.choice(["fire_effect", "water_effect"])
					for effect_surface in [random.choice(self.surface[element_effect])] * random.randint(1, 2):
						# size_percent = 50
						size_percent = random.randint(50, 60)
						effect_surface = pg.transform.scale(effect_surface, (int(tuile_size[0] - tuile_size[0] * (100 - size_percent) / 100),
																			int(tuile_size[1] - tuile_size[1] * (100 - size_percent) / 100)))
						try:
							# tmp_pos_x = random.randint(0, tuile_size[0] - effect_surface.get_width())
							tmp_pos_x = random.randint(x_pos + effect_surface.get_width() * -1 / 2, x_pos + tuile_size[0] - effect_surface.get_width() / 2)
						except ValueError:
							tmp_pos_x = x_pos + tuile_size[0] / 2 - effect_surface.get_width() / 2
						try:
							tmp_pos_y = random.randint(y_pos + effect_surface.get_height() * -1 / 2, y_pos + tuile_size[1] - effect_surface.get_height() / 2)
						except ValueError:
							tmp_pos_y = y_pos + tuile_size[1] / 2 - effect_surface.get_height() / 2
						surface.blit(effect_surface, (tmp_pos_x, tmp_pos_y))

		ret_surface.blit(surface, (ret_surface.get_width() / 2 - surface.get_width() / 2, ret_surface.get_height() / 2 - surface.get_height() / 2))
		if game_done:
			game_over_surface = random.choice(self.surface["game_over"])
			# game_over_surface = pg.transform.scale(game_over_surface, (width, height))
			ret_surface.blit(game_over_surface,
							(ret_surface.get_width() / 2 - game_over_surface.get_width() / 2,
							 ret_surface.get_height() / 2 - game_over_surface.get_height() / 2))
		return ret_surface

# -------------------------------------------------------------------------------------------------------------------------------

# _______________________________________________________________________________________________________________________________
# SCENE 0 menu_principal
	def _load_scene_0(self):
		# menu principal
		print("menu_principal scene :D")
		self.scene = 0
		self.ft_gui.clear()

		self.button_size = (200, 75)
		self.ft_gui.add_button(id_="play", pos=(int(self.screen.get_width() / 4 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Play", function=self._load_scene_1)
		self.ft_gui.add_button(id_="bot_show", pos=(int(self.screen.get_width() / 4 * 2 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Bot show", function=self._load_scene_2)
		self.ft_gui.add_button(id_="bot_train", pos=(int(self.screen.get_width() / 4 * 3 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Bot train", function=self._load_scene_3)


	def _event_scene_0(self, event):
		if event.type == pg.VIDEORESIZE:
			self.ft_gui.buttons["play"].rect.x = self.screen.get_width() / 2 - self.button_size[0] / 2
			self.ft_gui.buttons["play"].rect.y = 150
			self.ft_gui.buttons["bot_show"].rect.x = self.screen.get_width() / 2 - self.button_size[0] / 2
			self.ft_gui.buttons["bot_show"].rect.y = self.button_size[1] + self.param["interface_sep"] + 150
			

	def _display_scene_0(self):
		pass
# -------------------------------------------------------------------------------------------------------------------------------

# _______________________________________________________________________________________________________________________________
# SCENE 1 play
	def _load_scene_1(self):
		# interface to play
		print("1play scene :D")
		self.scene = 1
		self.ft_gui.clear()
		self.game_state = self.env_2048.start_game(4)
		self.game_done = False
		self.fusion = []

	def _event_scene_1(self, event):
		if not self.game_done and event.type == pg.KEYUP:
			if event.key in [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT]:
				if event.key == pg.K_UP:
					action = 0
				elif event.key == pg.K_RIGHT:
					action = 1
				elif event.key == pg.K_DOWN:
					action = 2
				elif event.key == pg.K_LEFT:
					action = 3
				tmp_game_state, score, self.game_done, self.fusion = self.env_2048.step(self.game_state, action, ret_fusion=True)
				if self.game_state != tmp_game_state:
					self.game_state = tmp_game_state
				if self.game_done:
					print("self.game_done")

	def _display_scene_1(self):
		self.game_surface = self._get_surface_2048(self.game_state,
												  (min(self.screen.get_width(), self.screen.get_height()) / 3 * 2, min(self.screen.get_width(), self.screen.get_height()) / 3 * 2),
												  font_size=20,
												  fusion=self.fusion,
												  game_done=self.game_done)
		self.screen.blit(self.game_surface,
			(self.screen.get_width() / 2 - self.game_surface.get_width() / 2,
				(self.screen.get_height() - 150) / 2 - self.game_surface.get_height() / 2 + 150))
# -------------------------------------------------------------------------------------------------------------------------------

# _______________________________________________________________________________________________________________________________
# SCENE 2 bot_show
	def _pause_auto_bot_scene_2(self):
		if self.auto:
			self.auto = False
			self.ft_gui.buttons["auto"].display_on = True
			self.ft_gui.buttons["pause"].display_on = False
		else:
			self.auto = True
			self.ft_gui.buttons["auto"].display_on = False
			self.ft_gui.buttons["pause"].display_on = True

	def _background_task_scene_2(self):
		id_ = time.time()
		try:
			self.background_scene_exec[2].append(id_)
		except:
			self.background_scene_exec[2] = id_
		while id_ in self.background_scene_exec[2] and self.running:
			if self.auto:
				action = random.choice([0, 1, 2, 3])
				tmp_game_state, self.game_done, self.fusion = self.env_2048.step(self.game_state, action, ret_fusion=True)
				if self.game_state != tmp_game_state:
					self.game_state = tmp_game_state
				if self.game_done:
					print("self.game_done")
					self.background_scene_exec[2].pop(id_)
					exit()
				time.sleep(self.bot_speed)
			else:
				time.sleep(0)
		exit()

	def _one_step_scene_2(self):
		if not self.game_done:
			action = random.choice([0, 1, 2, 3])
			tmp_game_state, self.game_done, self.fusion = self.env_2048.step(self.game_state, action, ret_fusion=True)
			if self.game_state != tmp_game_state:
				self.game_state = tmp_game_state
			if self.game_done:
				print("self.game_done")
				self.background_scene_exec[2].pop(id_)

	def _retry_game_scene_2(self):
		self.background_scene_exec[2] = []
		self.game_state = self.env_2048.start_game(4)
		self.game_done = False
		self.fusion = []
		concurrent.futures.ThreadPoolExecutor().submit(self._background_task_scene_2)
		

	def _load_scene_2(self):
		# interface bot play
		print("2bot_show scene :D")
		self.scene = 2
		self.button_size = (200, 75)
		self.ft_gui.clear()
		self.ft_gui.add_button(id_="auto", pos=(int(self.screen.get_width() / 4 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Auto", function=self._pause_auto_bot_scene_2)
		self.ft_gui.add_button(id_="pause", pos=(int(self.screen.get_width() / 4 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Pause", function=self._pause_auto_bot_scene_2, display_on=False)
		self.ft_gui.add_button(id_="one_step", pos=(int(self.screen.get_width() / 4 * 2 - self.button_size[0] / 2), 150),
			size=self.button_size, text="One Step", function=self._one_step_scene_2)
		self.ft_gui.add_button(id_="retry", pos=(int(self.screen.get_width() / 4 * 3 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Retry", function=self._retry_game_scene_2)

		self.game_state = self.env_2048.start_game(4)
		self.game_done = False
		self.auto = False
		self.fusion = []
		# self.bot_speed = 0.1
		self.bot_speed = 0.05
		concurrent.futures.ThreadPoolExecutor().submit(self._background_task_scene_2)

	def _event_scene_2(self, event):
		if event.type == pg.VIDEORESIZE:
			self.ft_gui.buttons["auto"].rect.x = int(self.screen.get_width() / 4 - self.button_size[0] / 2)
			self.ft_gui.buttons["auto"].rect.y = 150
			self.ft_gui.buttons["pause"].rect.x = int(self.screen.get_width() / 4 - self.button_size[0] / 2)
			self.ft_gui.buttons["pause"].rect.y = 150
			self.ft_gui.buttons["one_step"].rect.x = int(self.screen.get_width() / 4 * 2 - self.button_size[0] / 2)
			self.ft_gui.buttons["one_step"].rect.y = 150
			self.ft_gui.buttons["retry"].rect.x = int(self.screen.get_width() / 4 * 3 - self.button_size[0] / 2)
			self.ft_gui.buttons["retry"].rect.y = 150
		elif not self.game_done and not self.game_done and event.type == pg.KEYUP:
			if event.key in [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT]:
				if event.key == pg.K_UP:
					action = 0
				elif event.key == pg.K_RIGHT:
					action = 1
				elif event.key == pg.K_DOWN:
					action = 2
				elif event.key == pg.K_LEFT:
					action = 3
				tmp_game_state, self.game_done, self.fusion = self.env_2048.step(self.game_state, action, ret_fusion=True)
				if self.game_state != tmp_game_state:
					self.game_state = tmp_game_state
				if self.game_done:
					print("self.game_done")

	def _display_scene_2(self):
		self.game_surface = self._get_surface_2048(self.game_state,
												  (min(self.screen.get_width(), self.screen.get_height()) / 3 * 2, min(self.screen.get_width(), self.screen.get_height()) / 3 * 2),
												  font_size=20,
												  fusion=self.fusion,
												  game_done=self.game_done)
		self.screen.blit(self.game_surface, (self.screen.get_width()/2 - self.game_surface.get_width()/2,
											 self.screen.get_height() - self.game_surface.get_height() - self.param["interface_sep"]))
		text_surface = self.fonts[20].render("Score: " + str(sum(self.game_state)), True, WHITE_TXT)
		self.screen.blit(text_surface, (self.screen.get_width()/2 - text_surface.get_width()/2,
										self.screen.get_height() - self.game_surface.get_height() - text_surface.get_height() - self.param["interface_sep"]*2))
# -------------------------------------------------------------------------------------------------------------------------------

# _______________________________________________________________________________________________________________________________
# SCENE 3 bot_train
	def _background_task_scene_3(self):
		id_ = time.time()
		try:
			self.background_scene_exec[3].append(id_)
		except:
			self.background_scene_exec[3] = [id_]
		while id_ in self.background_scene_exec[3] and self.running:
			if self.auto:
				timer = time.time()

				action = self.agent.choose_action(self.game_state)

				tmp_game_state, self.game_done, self.fusion = self.env_2048.step(self.game_state, action, ret_fusion=True)

				
				if self.game_state != tmp_game_state:
					# reward = self.game_state.count(0) - tmp_game_state.count(0) + 1
					# reward = max(self.game_state)
					# reward = len(self.fusion)
					if self.game_done:
						reward = -1
					else:
						reward = self.game_state.count(0) - tmp_game_state.count(0) + 1
						# reward = sum(self.game_state)
					self.game_state = tmp_game_state
					if self.n_game % 5 == 0:
						self.game_surface = self._get_surface_2048(self.game_state,
												  (min(self.screen.get_width(), self.screen.get_height()) / 3 * 2, min(self.screen.get_width(), self.screen.get_height()) / 3 * 2),
												  font_size=20,
												  fusion=self.fusion,
												  game_done=self.game_done)
					self.score += reward
					self.agent.remember(self.game_state, action, reward, tmp_game_state, int(self.game_done))

					self.agent.learn()
				else:
					reward = -1

				if self.game_done:
					self.eps_history.append(self.agent.epsilon)
					self.ddqn_scores.append(self.score)
					self.agent.save_model()
					self.n_game += 1
					self.game_state = self.env_2048.start_game(4)
					self.game_done = False
					self.score = 0
					print("epsilon:", self.eps_history)
					print("scores:", self.ddqn_scores)

				# time.sleep(max(0, time.time() - timer() - self.bot_speed))
			else:
				time.sleep(0)
		exit()

	def _pause_auto_bot_scene_3(self):
		if self.auto:
			self.auto = False
			self.ft_gui.buttons["auto"].display_on = True
			self.ft_gui.buttons["pause"].display_on = False
		else:
			self.auto = True
			self.ft_gui.buttons["auto"].display_on = False
			self.ft_gui.buttons["pause"].display_on = True

	def _one_step_scene_3(self):
		if not self.game_done:

			action = random.choice([0, 1, 2, 3])

			tmp_game_state, self.game_done, self.fusion = self.env_2048.step(self.game_state, action, ret_fusion=True)
			if self.game_state != tmp_game_state:
				self.game_state = tmp_game_state
			if self.game_done:
				print("self.game_done")
				self.background_scene_exec[2].pop(id_)

	def _show_graph_scene_3(self):
		pass

	def _load_scene_3(self):
		# interface bot train
		print("3bot_train scene :D")
		self.scene = 3
		self.button_size = (200, 75)
		self.ft_gui.clear()
		self.ft_gui.add_button(id_="auto", pos=(int(self.screen.get_width() / 4 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Auto", function=self._pause_auto_bot_scene_3)
		self.ft_gui.add_button(id_="pause", pos=(int(self.screen.get_width() / 4 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Pause", function=self._pause_auto_bot_scene_3, display_on=False)
		self.ft_gui.add_button(id_="one_step", pos=(int(self.screen.get_width() / 4 * 2 - self.button_size[0] / 2), 150),
			size=self.button_size, text="One Step", function=self._one_step_scene_3)
		self.ft_gui.add_button(id_="graph", pos=(int(self.screen.get_width() / 4 * 3 - self.button_size[0] / 2), 150),
			size=self.button_size, text="Graph", function=self._show_graph_scene_3)

		""" load existant model """
		fname = "model/new_model.h5"
		self.agent = DDQNAgent(alpha=0.0005, gamma=0.99, n_actions=4, epsilon=1.0,
							batch_size=64, input_dims=16, fname=fname)
		try:
			self.agent.load_model()
			print(f"model {fname} loaded")
		except:
			print("create new model")

		self.auto = False
		self.fusion = []
		self.bot_speed = 0.05
		self.show_graph = False

		self.n_game = 0
		self.ddqn_scores = []
		self.eps_history = []

		self.game_state = self.env_2048.start_game(4)
		self.game_done = False
		self.game_surface = self._get_surface_2048(self.game_state,
												  (min(self.screen.get_width(), self.screen.get_height()) / 3 * 2, min(self.screen.get_width(), self.screen.get_height()) / 3 * 2),
												  font_size=20,
												  fusion=self.fusion,
												  game_done=self.game_done)
		self.score = 0
		
		concurrent.futures.ThreadPoolExecutor().submit(self._background_task_scene_3)


	def _event_scene_3(self, event):
		pass

	def _display_scene_3(self):
		self.screen.blit(self.game_surface, (self.screen.get_width()/2 - self.game_surface.get_width()/2,
											 self.screen.get_height() - self.game_surface.get_height() - self.param["interface_sep"]))
		text_surface = self.fonts[20].render("Score: " + str(sum(self.game_state)), True, WHITE_TXT)
		self.screen.blit(text_surface, (self.screen.get_width()/3 - text_surface.get_width()/2,
										self.screen.get_height() - self.game_surface.get_height() - text_surface.get_height() - self.param["interface_sep"]*2))
		text_surface = self.fonts[20].render("n_game: " + str(self.n_game), True, WHITE_TXT)
		self.screen.blit(text_surface, (self.screen.get_width()/3*2 - text_surface.get_width()/2,
										self.screen.get_height() - self.game_surface.get_height() - text_surface.get_height() - self.param["interface_sep"]*2))
# -------------------------------------------------------------------------------------------------------------------------------

	def event(self, event):
		if event.type == pg.VIDEORESIZE:
			self.screen = pg.display.set_mode((event.w, event.h), pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE)
		self.music_player.event(event)
		ret = self.ft_gui.event(event)
		
		self._event_scene(self.scene, event)


	def display(self, fps=False):
		self.screen.fill(BG)
		
		# display fps
		if not fps:
			fps_real_time_surface = self.fonts[15].render("FPS : -", True, WHITE_TXT)
		else:
			fps_real_time_surface = self.fonts[15].render("FPS : " + str(fps), True, WHITE_TXT)
		self.screen.blit(fps_real_time_surface, (20, 20))
		
		mp_width, mp_height  = self.music_player.music_player.get_width(), self.music_player.music_player.get_height()
		self._display_scene(self.scene)
		self.ft_gui.display()
		# self.music_player.display(self.screen, self.screen.get_width() / 2 - mp_width / 2, min(self.screen.get_height() - mp_height, self.screen.get_height() / 6 * 4))
		self.music_player.display(self.screen, self.screen.get_width() / 2 - mp_width / 2, 20)
		# refresh the display
		pg.display.flip()


if __name__ == "__main__":

	app = Pygame2048()
	
	timer = time.time()
	fps_timers = []
	last_count_fps = False
	
	while app.running:
	
		for event in pg.event.get():
			if event.type == pg.QUIT:
				app.running = False
			else:
				app.event(event)
	
		if len(fps_timers) > 0:
			app.display(round(1 / np.mean(fps_timers), 2))
		else:
			app.display()

		app.clock.tick(app.param["fps"])
		tmp = time.time()
		fps_timers += [tmp - timer]
		timer = tmp
		fps_timers = fps_timers[max(0, len(fps_timers) - app.param["fps"]):]
	
	app.quit()