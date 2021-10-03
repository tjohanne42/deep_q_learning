from PIL import ImageGrab
import pyautogui
import keyboard
import random
import time

#usage with https://framagames.org/2048originel/index.html
#board of the game must be fully open

class ColorsValues:
	whitepage = (250, 248, 239)
	border = (187, 173, 160)
	border_min = (187, 173, 150)
	border_max = (200, 180, 162)
	empty = (205, 193, 180)
	two = (238, 228, 218)
	four = (237, 224, 200)
	eight = (242, 177, 121)
	sixteen = (245, 149, 99)
	thirtytwo = (246, 124, 95)
	sixtyfour = (246, 94, 59)
	onehundredtwentyeightt = (237, 207, 114)
	twohundredfiftysix = (237, 204, 97)
	fivehundredtwelve = (237, 200, 80)
	onethousandtwentyfour = (237, 197, 63)
	twothousandfortyeight = (237, 194, 46)

def pixel_is_border(pixel):
	if pixel == ColorsValues.border:
		return True
	r, g, b = pixel
	nr, ng, nb = ColorsValues.border_max
	mr, mg, mb = ColorsValues.border_min
	if r >= mr and r <= nr and g >= mg and g <= ng and b >= mb and b <= nb:
		return True
	else:
		return False

def change_value_with_pixel(grid, y, x, pixel):
	if pixel == ColorsValues.empty:
		grid[y][x] = 0
	elif pixel == ColorsValues.two:
		grid[y][x] = 2
	elif pixel == ColorsValues.four:
		grid[y][x] = 4
	elif pixel == ColorsValues.eight:
		grid[y][x] = 8
	elif pixel == ColorsValues.sixteen:
		grid[y][x] = 16
	elif pixel == ColorsValues.thirtytwo:
		grid[y][x] = 32
	elif pixel == ColorsValues.sixtyfour:
		grid[y][x] = 64
	elif pixel == ColorsValues.onehundredtwentyeightt:
		grid[y][x] = 128
	elif pixel == ColorsValues.twohundredfiftysix:
		grid[y][x] = 256
	elif pixel == ColorsValues.fivehundredtwelve:
		grid[y][x] = 512
	elif pixel == ColorsValues.onethousandtwentyfour:
		grid[y][x] = 1024
	elif pixel == ColorsValues.twothousandfortyeight:
		grid[y][x] = 2048
	else:
		print("no color match pixel =", pixel)

def GetGrid(x, y, grid):
	image = ImageGrab.grab()
	nb_x = 0
	pixel = image.getpixel((x, y))
	while nb_x < 4:
		change_value_with_pixel(grid, 0, nb_x, pixel)
		count = 0
		nb_y = 1
		while nb_y < 4:
			count = count + 1
			pixel = image.getpixel((x, y + count))
			while pixel_is_border(pixel) == False:
				count = count + 1
				pixel = image.getpixel((x, y + count))
			count = count + 1
			pixel = image.getpixel((x, y + count))
			while pixel_is_border(pixel) == True:
				count = count + 1
				pixel = image.getpixel((x, y + count))
			pixel = image.getpixel((x, y + count + 2))
			change_value_with_pixel(grid, nb_y, nb_x, pixel)
			nb_y = nb_y + 1
		pixel = image.getpixel((x, y))
		while pixel_is_border(pixel) == False:
			x = x + 1
			pixel = image.getpixel((x, y))
		while pixel_is_border(pixel) == True:
			x = x + 1
			pixel = image.getpixel((x, y))
		x = x + 1
		pixel = image.getpixel((x, y))
		nb_x = nb_x + 1

def GetGridPos():
	image = ImageGrab.grab()
	sizex, sizey = image.size
	done1 = False
	x = 0
	while done1 == False and x < sizex:
		done = False
		while x < sizex and done == False:
			y = 0
			while y < sizey and done == False:
				pixel = image.getpixel((x, y))
				if pixel_is_border(pixel) == True:
					done = True
				else:
					y = y + 1
			if done == False:
				x = x + 1
		if done != False:
			tmp = 1
			while pixel_is_border(pixel) == True and x + tmp < sizex:
				pixel = image.getpixel((x + tmp, y))
				tmp = tmp + 1
			tmp1 = 1
			pixel = image.getpixel((x, y))
			while pixel_is_border(pixel) == True and y + tmp1 < sizey:
				pixel = image.getpixel((x, y + tmp1))
				tmp1 = tmp1 + 1
			print(tmp, tmp1)
			if tmp >= 281 and tmp1 >= 269:
				done1 = True
			else:
				x = x + 1
	if done1 == False:
		print("no game on screen")
		return (-1, -1)
	x = x + 1
	y = y + 1
	pixel = image.getpixel((x, y))
	while pixel == ColorsValues.border:
		pixel = image.getpixel((x, y))
		x = x + 1
		y = y + 1
	return (x, y)

def show_grid(grid):
	for each in grid:
			print(" ", end = "")
			for i in each:
				print("| {} ".format(i), end = "")
			print("|")

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

def take_action(grid):
	action = random.randint(0, 3)
	if action == UP:
		pyautogui.keyDown('up')
	elif action == RIGHT:
		pyautogui.keyDown('right')
	elif action == DOWN:
		pyautogui.keyDown('down')
	elif action == LEFT:
		pyautogui.keyDown('left')

grid = [[0, 0, 0, 0],
		[0, 0, 0, 0],
		[0, 0, 0, 0],
		[0, 0, 0, 0]]
noboard = False
while True:
	if keyboard.is_pressed('q'):
		posx, posy = GetGridPos()
		if posx == -1:
			noboard = True
		else:
			GetGrid(posx, posy, grid)
		break
if noboard == False:
	show_grid(grid)
	while True:
		if keyboard.is_pressed('q'):
			break
		take_action(grid)
		time.sleep(0.5)
		GetGrid(posx, posy, grid)
		show_grid(grid)
		print()
