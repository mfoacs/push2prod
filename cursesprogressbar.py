#!/usr/bin/python
# -*- coding: utf-8 -*-

import curses
import time

class PB2:
    "progress bar v2"
    
    if __name__ == "__main__": 
        stdscr=curses.initscr() 
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_RED,curses.COLOR_WHITE)
        curses.init_pair(3,curses.COLOR_BLUE,curses.COLOR_WHITE)
        curses.init_pair(4,curses.COLOR_WHITE,curses.COLOR_WHITE)
        curses.init_pair(5,curses.COLOR_BLUE,curses.COLOR_BLUE)
        curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_WHITE)
        s=curses.newwin(48,156,0,0)
        s.bkgd(ord(' '),curses.color_pair(1))
        s.box()
        s.refresh()
        s=stdscr.subwin(3,52,26,41)
        s.bkgd(ord(' ' ), curses.color_pair(3))
        s.box()

        s.refresh()

        s=stdscr.subwin(12,68,20,32)
        s.bkgd(ord(' ' ), curses.color_pair(6))
        s.addstr(1, 27, "PROGRESS",curses.color_pair(2))

        # s.bkgdset(ord(' '), curses.color_pair(4)) s.box()

        s.refresh()

        diff=42
        s=stdscr.subwin(1,50,27,42)
        s.bkgd(ord(' ' ), curses.color_pair(4))
        #s.bkgdset(ord(' '),curses.color_pair(5))
        s.box()
        s.refresh()
        for x in range(26):
            s = stdscr.subwin(1, 2,27, diff)
            diff=diff+2
            s.bkgd (ord(' '), curses.color_pair(5))
        #limit = 10000
        #prog = progressBar(0, limit, 13)
        #oldprog =str(prog)
        #for i in xrange(limit+1):
        #     prog.updateAmount(i)

        #     print prog, "\r",
            time.sleep(0.20)
        s.refresh()
        curses.endwin()
        
test = PB2()
print test