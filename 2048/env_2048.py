import random
import numpy as np
import copy

from utils import *

class Env2048(object):
	def __init__(self):
		pass

	def start_game(self, size):
		state = [0] * (size * size)
		state = self._add_random_tuile(state, 2)
		return state


	def _add_random_tuile(self, state, nb):
		# lst_free_idx : [0, 1, 2, 3] -> signifie qu'il n'y a que la ligne du haut qui a des cases libres
		lst_free_idx = [i for i in range(len(state)) if state[i] == 0]

		# nb tuile libre
		if len(lst_free_idx) < nb:
			nb = len(lst_free_idx)

		for i in range(nb):
			rand = random.randint(0, len(lst_free_idx) - 1)
			state[lst_free_idx[rand]] = random.choice([2, 4, 2, 2])
			lst_free_idx = [i for i in range(len(state)) if state[i] == 0]
		return state


	def step(self, original_state, action, nb_random_tuile=1, verbose=False, ret_fusion=False):
		state = copy.deepcopy(original_state)
		size = isqrt(len(state))
		# 0up, 1right, 2down, 3left
		value = [-1 * size, 1, size, -1]
		value = value[action]

		# select order to move tuile
		if action == 0:
			if verbose: print("move:\t0:\tup")
			tuile_list = list(range(0, len(state)))
		elif action == 1:
			if verbose: print("move:\t1:\tright")
			tuile_list = []
			for col in range(size):
				for row in range(size):
					tuile_list.append(size - 1 - col + row * size)
		elif action == 2:
			if verbose: print("move:\t2:\tdown") 
			tuile_list = list(range(len(state)-1, -1, -1))
			tuile_list.reverse
		elif action == 3:
			if verbose: print("move:\t:\tleft")
			tuile_list = []
			for ret in range(size + 1):
				tuile_list += [x for x in range(len(state)) if x % size == ret]


		if verbose: print(f"action: '{action}'\nvalue: '{value}'\ntuile_list: '{tuile_list}'")

		# move tuiles
		unfusionable = []
		tmp_state = copy.deepcopy(state)
		for tuile_nb in tuile_list:
			if state[tuile_nb] != 0:
				for move in range(size - 1):

					if tuile_nb + value < 0 or tuile_nb + value >= len(state):
						break
					if value in [-1, 1] and (int(tuile_nb / size) != int((tuile_nb + value) / size)):
						break
					elif value in [-1 * size, size] and tuile_nb % size != (tuile_nb + value) % size:
						break

					if state[tuile_nb + value] == 0:
						# si la case est libre -> déplacement
						if verbose: print(f"move {tuile_nb} in {tuile_nb + value}")
						state[tuile_nb + value] = state[tuile_nb]
						state[tuile_nb] = 0
						tuile_nb += value
					elif state[tuile_nb + value] == state[tuile_nb] and tuile_nb + value not in unfusionable:
						# si collision avec meme tuile -> fusion
						if verbose: print(f"fusion {tuile_nb} in {tuile_nb + value}")
						state[tuile_nb + value] *= 2
						# state[tuile_nb + value] += 1
						state[tuile_nb] = 0
						unfusionable.append(tuile_nb + value)
						break
					else:
						break

		if tmp_state != state and nb_random_tuile > 0:
			self._add_random_tuile(state, nb_random_tuile)
		
		done = False
		if len([i for i in range(len(state)) if state[i] == 0]) == 0:
			done = True
			for i in range(len(state)):
				if (i > 0 and i % size != 0 and state[i] == state[i - 1]) or\
					(i < len(state) - 1 and i % size != size - 1 and state[i] == state[i + 1]) or\
					(i >= size and int(i / size) != 0 and state[i] == state[i - size]) or\
					(i < len(state) - size and int(i / size) != size - 1 and state[i] == state[i + size]):
					done = False
					break
		if ret_fusion:
			return state, done, unfusionable
		return state, done



	def terminal_print(self, state):
		size = isqrt(len(state))
		start = 0
		for i in range(size):
			# print([int(2 ** s) if s > 0 else 0 for s in state[start:start+size]])
			print(state[start:start+size])
			start += size


if __name__ == "__main__":
	size = 4
	env = Env2048()

	state = env.start_game(size)
	env.terminal_print(state)
	done = False


	def human_action():
		action = None
		while action is None:
			tmp = input("")
			if tmp == "exit":
				exit()
			try:
				action = int(tmp)
			except:
				print("0, 1, 2 or 3 for up, right, down, left -- exit to leave")

	def rand_action():
		return random.randint(0, 3)
	
	get_action = rand_action

	while not done:

		action = get_action()

		print("action:", action)

		state, done = env.step(state, action, nb_random_tuile=1, verbose=False)
		env.terminal_print(state)
		print(f"done: '{done}'")

	score = sum(state)
	print("score final:", score)