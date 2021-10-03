import pygame as pg

# my modules
from .ft_pg_input_textbar import *
from .ft_pg_button import *
from .ft_pg_video_player import *

class FtPgGui(object):

	def __init__(self, screen):
		self.screen = screen
		pg.key.set_repeat(400, 35)
		self._init_var()


	def _init_var(self):
		self.buttons = {}
		self.input_textbar = {}
		self.video_player = {}


	def clear(self):
		self._init_var()


	def add_button(self, id_, **kwargs):
		self.buttons[id_] = FtPgButton(self.screen, **kwargs)
		return self.buttons[id_]


	def add_input_textbar(self, id_, **kwargs):
		self.input_textbar[id_] = FtPgInputTextbar(self.screen, **kwargs)
		return self.input_textbar[id_]


	def add_video_player(self, id_, **kwargs):
		self.video_player[id_] = FtPgVideoPlayer(self.screen, **kwargs)
		if self.video_player[id_] == None:
			return None
		return self.video_player[id_]


	def event(self, event):
		my_ret = {"input_textbar": {}, "button": {}, "video_player": {}}

		for k, textbar in self.input_textbar.items():
			ret = textbar.event(event)
			my_ret["input_textbar"][textbar.id_] = ret

		for k, button in self.buttons.items():
			ret = button.event(event)
			my_ret["button"][button.id_] = ret

		for k, video in self.video_player.items():
			ret = video.event(event)
			my_ret["video_player"][video.id] = ret

		return my_ret


	def display(self):
		for k, textbar in self.input_textbar.items():
			textbar.display()

		for k, button in self.buttons.items():
			button.display()

		for k, video in self.video_player.items():
			video.display()