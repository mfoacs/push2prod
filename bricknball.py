# To change this template, choose Tools | Templates
# and open the template in the editor.
#!/usr/bin/env python
#
# Brick & Ball in Python
# by Jerry Fleming <>
#
# This is a small game adapted from that in Motorola Mobile C289, and my first game in python :)
#
# This progrma is best run under linux. Since Windows port of Python has poor curses support,
# play it under Windows is not recommended. If you have no linux box available, try Cygwin,
# though it too has poor curses support.
#
# As I am a newbie to python, please tell me if you have a better implementation or any suggestions.
#
# TODO:
# re-implemente it with wxPython, so one does not have to rely on the ugly curses.
# session support.
# pausing, especially when confirming
# resize terminal at run time
#
# HISTORY
# 2006-04-19: first version
#
#

import curses
import _curses
import thread
import time
import string
import random

# parameters: adjust them to fit you terminal
brick_width = 7
brick_gap_x = 1
brick_gap_y = 1
speed = 0.05 # sleep time to control moving speed of the ball
pause = 1 # time to pause

# terminal initialization
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
stdscr.keypad(1)
screen_height, screen_width = stdscr.getmaxyx()
screen_height = screen_height - 1
screen_width = screen_width - 1
brick_rows = screen_height / 4
if brick_rows > 7: brick_rows = 7
brick_cols = (screen_width + brick_gap_x) / (brick_width + brick_gap_x)
brick_margin = (screen_width - brick_cols * (brick_width + brick_gap_x) + brick_gap_x)/2
pad_position = randint(0, screen_width - brick_width)
ball_position = [screen_height - 3, randint(0, screen_width - brick_width)]
ball_direction = [-1, 1] # abs(tan(a)) must be 1
char = ''
bricks = []
game_score = 0
ScreenSizeError = 'ScreenSizeError'

tStart = '''
  ______        _       _         ___      ______        _ _     _ 
     ______             _
(____  \      (_)     | |       / _ \    (____  \      | | |   (_) 
   (_____ \        _  | |
  ____)  ) ____ _  ____| |  _   ( (_) )    ____)  )_____| | |    _ ____ 
     _____) )   _ _| |_| |__   ___  ____
|  __  ( / ___) |/ ___) |_/ )   ) _ (    |  __  ((____ | | |   | |  _ \ 
   |  ____/ | | (_   _)  _ \ / _ \|  _ \
| |__)  ) |   | ( (___|  _ (   ( (/  \   | |__)  ) ___ | | |   | | | | | 
  | |    | |_| | | |_| | | | |_| | | | |
|______/|_|   |_|\____)_| \_)   \__/\_)  |______/\_____|\_)_)  |_|_| |_| 
  |_|     \__  |  \__)_| |_|\___/|_| |_|
 
           (____/


                                by Jerry Fleming <>


                                           GAME STARTING ...

                        (this assumes that your terminal be larger that 
130x40)
'''

tExit = '''
                                                88888 
       88888
88888888888             88       ad88888ba     88 8b        d8      d8 
         88
88                      ""   ,d d8"     "8b    88  Y8,    ,8P     ,8P' 
         88
88                           88 ""      a8P    88   Y8,  ,8P     d8" 
         88
88aaaaa     8b,     ,d8 88 MM88MMM   ,a8P"     88    "8aa8"    ,8P' 
8b,dPPYba,  88
88"""""      `Y8, ,8P'  88   88     d8"        88     `88'    d8"   88P' 
   `"8a 88
88             )888(    88   88     ""         88      88   ,8P'    88 
      88 88
88           ,d8" "8b,  88   88,    aa         88      88  d8"      88 
      88 88
88888888888 8P'     `Y8 88   "Y888  88         88      88 8P'       88 
      88 88
                                                88888 
       88888
'''

tOver = '''
   ,ad8888ba, 
                                  88
  d8"'    `"8b 
                                  88
d8' 
                                 88
88            ,adPPYYba, 88,dPYba,,adPYba,   ,adPPYba,     ,adPPYba,  8b 
       d8  ,adPPYba, 8b,dPPYba, 88
88      88888 ""     `Y8 88P'   "88"    "8a a8P_____88    a8"     "8a 
`8b     d8' a8P_____88 88P'   "Y8 88
Y8,        88 ,adPPPPP88 88      88      88 8PP"""""""    8b       d8 
`8b   d8'  8PP""""""" 88         ""
  Y8a.    .a88 88,    ,88 88      88      88 "8b,   ,aa    "8a,   ,a8" 
  `8b,d8'   "8b,   ,aa 88         aa
   `"Y88888P"  `"8bbdP"Y8 88      88      88  `"Ybbd8"'     `"YbbdP"' 
    "8"      `"Ybbd8"' 88         88
'''

tGoon = '''
                                                                 88888 
                        88888
   ,ad8888ba,                                      ad88888ba     88 8b 
       d8      d8          88
  d8"'    `"8b                                    d8"     "8b    88  Y8, 
    ,8P     ,8P'          88
d8'                                              ""      a8P    88   Y8, 
  ,8P     d8"            88
88             ,adPPYba,      ,adPPYba,  8b,dPPYba,   ,a8P"     88 
"8aa8"    ,8P' 8b,dPPYba,  88
88      88888 a8"     "8a    a8"     "8a 88P'   `"8a d8"        88 
`88'    d8"   88P'   `"8a 88
Y8,        88 8b       d8    8b       d8 88       88 ""         88 
88   ,8P'    88       88 88
  Y8a.    .a88 "8a,   ,a8"    "8a,   ,a8" 88       88 aa         88 
  88  d8"      88       88 88
   `"Y88888P"   `"YbbdP"'      `"YbbdP"'  88       88 88         88 
  88 8P'       88       88 88
                                                                 88888 
                        88888
'''

def init_game():
	'''Game initializing.'''
	global bricks
	# display the bricks
	for row in range(brick_rows):
		y = row * (1 + brick_gap_y)
		for col in range(brick_cols):
			x = col * (brick_gap_x + brick_width) + brick_margin
			stdscr.addstr(y, x, ' ' * brick_width, curses.A_REVERSE)
			bricks.append([y, x])
	# move the pad to center of bottom at starting up
	stdscr.addstr(screen_height - 1, pad_position, ' ' * brick_width, 
curses.A_REVERSE)
	# move the ball to left bottom side at starting up
	stdscr.addstr(ball_position[0], ball_position[1], ' ', curses.A_REVERSE)
	# display score board
	stdscr.addstr(screen_height, 0, ' SCORE: '+ ('%03d' % game_score) + ' '* 4, curses.A_REVERSE)
	stdscr.addstr(screen_height, 15, 'USE q to quit' + ' '* (screen_width -28), curses.A_REVERSE)
	# final step to init display
	stdscr.refresh()

def move_pad(lock):
	'''Move the pad to catch the ball.'''
	global char, pad_position
	char = stdscr.getch()
	if char == ord('q'): quit_game(lock)
	if char == curses.KEY_LEFT: pad_position = pad_position - 1
	if char == curses.KEY_RIGHT: pad_position = pad_position + 1
	if pad_position < 0: pad_position = 0
	if pad_position >= screen_width - brick_width: pad_position = screen_width - brick_width
	stdscr.addstr(screen_height - 1, 0, ' ' * screen_width)
	stdscr.addstr(screen_height - 1, pad_position, ' ' * brick_width, curses.A_REVERSE)
	stdscr.refresh()

def move_ball(lock):
	'''Move the ball to a direction.'''
	global ball_position, ball_direction
	# clear the old position, do not if in pad
	if ball_position[0] != screen_height - 1:
		stdscr.addstr(ball_position[0], ball_position[1], ' ')
	ball_position[0] = ball_position[0] + ball_direction[0]
	ball_position[1] = ball_position[1] + ball_direction[1]
	stdscr.addstr(ball_position[0], ball_position[1], ' ', curses.A_REVERSE)
	detect_collision(lock)
	stdscr.refresh()
	sleep(speed)

def detect_collision(lock):
	'''Detect whether the ball has hit something, change direction if yes.'''
	global bricks, ball_direction, game_score
	# hit upper wall
	if ball_position[0] == 0 :
		ball_direction = [- ball_direction[0], ball_direction[1]]
	# hit left and right wall
	if ball_position[1] == 0 or ball_position[1] == screen_width:
		ball_direction = [ball_direction[0], - ball_direction[1]]
	# hit brick
	for brick in bricks:
		# hit from bottom or upper direction
		if brick[1] <= ball_position[1] + ball_direction[1] <= brick[1] + brick_width \
		and ball_position[0] + ball_direction[0] == brick[0]:
			ball_direction[0] = - ball_direction[0]
			stdscr.addstr(brick[0], brick[1], ' '* brick_width)
			game_score = game_score + 10
			stdscr.addstr(screen_height, 8, '%03d' % game_score, curses.A_REVERSE)
			bricks.remove(brick)
			# another level to continue the game
			if not len(bricks): another_level()
	# hit body of pad
	if ball_position[0] == screen_height - 2 and pad_position <= ball_position[1] <= pad_position + brick_width:
		ball_direction[0] = - ball_direction[0]
	# hit bottom
	elif ball_position[0] == screen_height - 1:
		ball_direction[0] = - ball_direction[0]
	# hit left side of pad (hit bottom already)
	if ball_position[1] == pad_position and  char == curses.KEY_LEFT and ball_direction[1]:
		ball_direction[1] = - ball_direction[1]
	# hit right side of pad (hit bottom already)
	if ball_position[1] == pad_position + brick_width and  char == curses.KEY_RIGHT and not ball_direction[1]:
		ball_direction[1] = - ball_direction[1]
	# hit bottom wall, game over
	if ball_position[0] == screen_height - 1 and not pad_position <= ball_position[1] <= pad_position + brick_width:
         	line_num = 0
		for line in split(tOver, "\n"):
			stdscr.addstr(screen_height / 2 + line_num, 10, line)
			line_num = line_num + 1
		stdscr.refresh()
		curses.flash()
		sleep(1)
		curses.flash()
		sleep(1)
		lock.release()

def quit_game(lock):
	'''Confirm quit the game.'''
	global char, speed
	if char != ord('q'): return
	speed_old = speed # store the value for resume
	speed = pause # wait for a long time
	line_num = 0
	for line in split(tExit, "\n"):
		stdscr.addstr(screen_height / 2 + line_num, 10, line)
		line_num = line_num + 1
	stdscr.addstr(screen_height, 15, 'USE n to continue, any other key to quit' + ' '* (screen_width - 40), curses.A_REVERSE)
	stdscr.refresh()
	#char = stdscr.getch() ## fix me: why can't we use the global char?
	if char == ord('n'):
		speed = speed_old
		line_num = 0
		for line in split(tExit, "\n"):
			stdscr.addstr(screen_height / 2 + line_num, 10, ' ' * len(line) )
			line_num = line_num + 1
		stdscr.refresh()
	else:
		lock.release()

def another_level():
	'''Confirm another level of the game.'''
	global speed, char
	speed_old = speed # store the value for resume
	speed = pause # wait for a long time
	line_num = 0
	for line in split(tGoon, "\n"):
		stdscr.addstr(screen_height / 2 + line_num, 10, line)
		line_num = line_num + 1
	stdscr.addstr(screen_height, 15, 'USE n to quit, any other key to continue' + ' '* (screen_width - 40), curses.A_REVERSE)
	stdscr.refresh()
	#char = stdscr.getch()
	if char == ord('n'):
		lock.release()
	else:
		stdscr.erase()
		speed = speed / 2
		init_game()

def looper(fun, lock):
	'''Dispatcher to drive th ball and pad.'''
	try:
		while lock.locked(): globals()[fun](lock)
	except _curses.error, diag:
		if lock.locked(): lock.release()
	
# main loop starts here
if __name__ == "__main__":
	try:
		line_num = 0
		for line in split(tStart, "\n"):
			stdscr.addstr(screen_height /4 + line_num, 10, line)
			line_num = line_num + 1
		stdscr.refresh()
		sleep(1)
		stdscr.erase()
		init_game()
		locks = []
		for i in range(2):
			lock = thread.allocate_lock()
			lock.acquire()
			locks.append(lock)
		thread.start_new_thread(looper, ('move_ball', locks[0]))
		thread.start_new_thread(looper, ('move_pad', locks[1]))
		while locks[0].locked() and locks[1].locked: pass # main loop
	except _curses.error, diag:
		msg = 'Your terminal is too small: ' + str(diag)
	except 'dd':
		msg = 'Game exit abnormally.'
	else:
		msg = 'Game stopped.'
	# out of loop means stop
	for i in range(2):
		if locks[i].locked(): locks[i].release()
	height, width = stdscr.getmaxyx()
	if height - 1 < screen_height or width - 1 < screen_width:
		msg = 'Your terminal is shrinked.'
	# out of loop means stop
	curses.curs_set(1)
	stdscr.keypad(0)
	curses.nocbreak()
	curses.echo()
	curses.endwin()
	print msg