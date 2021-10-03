import pygame as pg
import concurrent.futures
import time
import atexit
import cv2
import numpy as np

BG = (40, 40, 40)

class FtPgVideoPlayer(object):
	def __init__(
				self,
				screen,
				video_path=False,
				audio_path=False,
				id=False,
				pos=(0, 0),
				size=(200, 200),
				display_on=True,
				pause=False,
				max_frames_memory=10				
				):

		self.screen = screen
		self.id = id
		self.rect = pg.Rect(pos[0], pos[1], size[0], size[1])
		self.display_on = display_on
		self.max_frames_memory = max_frames_memory
		self.pause = pause

		self.video_path = video_path
		self.audio_path = audio_path

		if self.video_path == False:
			print("no video path")
			return None
		self.cap = cv2.VideoCapture(self.video_path)
		self.fps = self.cap.get(cv2.CAP_PROP_FPS)
		print("fps =", self.fps)

		if not self.cap.isOpened():
			print("File Cannot be Opened")
			return None

		self.empty_frame = pg.Surface((size))
		self.empty_frame.fill(BG)

		self.last_load = 0
		self.nb_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
		print("nb_frames:", self.nb_frames)
		self.duration_in_seconds = float(self.nb_frames) / float(self.fps)
		print("durationInSeconds: ", self.duration_in_seconds ,"s")

		#self.frames = [False] * (int(self.nb_frames) + 1)
		self.frames = []

		self.actual_frame_index = 0
		self.start = time.time() * 1000
		self.running = True
		self.time_beetween_frames = 1000 / self.fps
		print("time_beetween_frames", self.time_beetween_frames, "ms")

		self.f1 = concurrent.futures.ThreadPoolExecutor().submit(self._load_frames)
		#self._load_frames()
		atexit.register(self.quit)

	def _load_frames(self):
		while self.running:
			start_to_load_timer = time.time() * 1000

			actual_pos_timer = time.time() * 1000 - self.start
			wanted_frame_index = int(actual_pos_timer / self.time_beetween_frames)
			# print("actual_pos_timer", actual_pos_timer)
			# print("wanted_frame_index", wanted_frame_index)
			# print("actual_frame_index", wanted_frame_index)

			# if wanted_frame_index != self.actual_frame_index:
			# 	self.actual_frame_index = wanted_frame_index
			
			#f1 = concurrent.futures.ThreadPoolExecutor().submit(self._load_frame_by_index)
			self._load_frame_by_index(wanted_frame_index)
			self.actual_frame_index = wanted_frame_index

			#self._load_frame_by_index(wanted_frame_index + 1)

			# print("time to load", (time.time() * 1000 - start_to_load_timer) / 1000, "sec")
			#print("time to sleep", max(0, (self.time_beetween_frames  / 2 - (time.time() * 1000 - start_to_load_timer)) / 1000), "sec")
			#time.sleep(max(0, (self.time_beetween_frames  / 2 - (time.time() * 1000 - start_to_load_timer)) / 1000))


			# if self.frames[self.actual_frame_index] == False:
			#   ret, frame = self.cap.read()
			#   if frame is not None:
			#       self.frames[self.actual_frame_index] = self.cv2_to_pygame(frame)
			#       self.frame_count += 1

	def _load_frame_by_index(self, index):
		#test_timer = time.time() * 1000

		if self.frames[index] == False:
			# if the frame isnt already loaded
			# if index != self.last_load + 1:
			# 	self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
			print("start to load", index)
			ret, frame = self.cap.read()

			# resize
			# height, width, channels = img.shape
			# if width > self.rect.rect.width:
			# 	percent_width = 
			dim = (200, 100)
			#
			frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

			if frame is not False:
				self.frames[index] = self.cv2_to_pygame(frame)
		
			self.last_load == index
			print("finish to load", index)

		#print("time to load", index, time.time() * 1000 - test_timer, "ms")


	def cv2_to_pygame(self, cv2_surface):
		pygame_surface = cv2.cvtColor(cv2_surface, cv2.COLOR_BGR2RGB)
		pygame_surface = np.fliplr(pygame_surface)
		pygame_surface = np.rot90(pygame_surface)
		pygame_surface = pg.surfarray.make_surface(pygame_surface)
		return pygame_surface


	def quit(self):
		self.running = False
		self.cap.release()
		cv2.destroyAllWindows()

	def event(self, event):
		return False

	def display(self):
		if self.display_on:
			if self.actual_frame_index > self.nb_frames or self.frames[self.actual_frame_index] == False:
				self.screen.blit(self.empty_frame, (self.rect.x, self.rect.y))
				print("display empty frame for", self.actual_frame_index)
			else:
				self.screen.blit(self.frames[self.actual_frame_index], (self.rect.x, self.rect.y))
				print("display frame for", self.actual_frame_index)
