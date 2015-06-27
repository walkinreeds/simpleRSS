import curses, traceback

class screen(object):
    def __init__(self):
        try:
            #initialize curses
            self.stdscr = curses.initscr()
            curses.start_color()
            if curses.has_colors():
                curses.init_pair(1,0,7)
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            self.stdscr.keypad(1)
        except:
            #error ocurred, restore terminal
            self.stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            traceback.print_exc() #print the exception

    def close(self):
        self.stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def showInterface(self, top_msg = "simpleRSS", bottom_msg = ""):
        if curses.has_colors():
            self.stdscr.addstr(0,0, top_msg+(" "*(curses.COLS - len(top_msg))), curses.color_pair(1));
            self.stdscr.addstr(curses.LINES-3,0, bottom_msg+(" "*(curses.COLS - len(bottom_msg))), curses.color_pair(1));
        else:
            self.stdscr.addstr(0,0, top_msg+(" "*(curses.COLS - len(top_msg))) );
            self.stdscr.addstr(curses.LINES-3,0, bottom_msg+(" "*(curses.COLS - len(bottom_msg))) );
        self.stdscr.refresh()
        return

    def showList(self, items, padY = 0, selectedItem = 0, boldItems = 0):
        nrItems = len(items);
        #feed list
        pad = curses.newpad(nrItems+1,curses.COLS)
        pad.keypad(1)
        for i in range(0,nrItems):
            pad.addstr(i, 0, " {0}{1}".format(items[i], " "*(curses.COLS - len(items[i]))))
            if boldItems != 0:
                if boldItems[i] == 0:
                    pad.chgat(i,0,-1,curses.A_BOLD)

        #fill blank lines to overwrite old content
        if(nrItems < curses.LINES - 3):
            for z in range(nrItems + 1, curses.LINES-3):
                self.stdscr.addstr(z, 0, " "*curses.COLS);

        pad.chgat(selectedItem,0,-1,curses.A_REVERSE);
        pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)
        self.stdscr.refresh()

        while (1):
            c = pad.getch()
            if c == ord('j') or c == curses.KEY_DOWN:
                if (selectedItem < nrItems - 1):
                    lastAttr = curses.A_NORMAL
                    if boldItems != 0:
                        if boldItems[selectedItem] == 0:
                            lastAttr = curses.A_BOLD
                    pad.chgat(selectedItem,0,-1,lastAttr)
                    selectedItem+=1;
                    pad.chgat(selectedItem,0,-1,curses.A_REVERSE);
                    #scroll down when we reach the end
                    if (selectedItem >= curses.LINES - 4):
                        padY = selectedItem - (curses.LINES - 4) + 1
            elif c == ord('k') or c == curses.KEY_UP:
                if (selectedItem > 0):
                    lastAttr = curses.A_NORMAL
                    if boldItems != 0:
                        if boldItems[selectedItem] == 0:
                            lastAttr = curses.A_BOLD
                    pad.chgat(selectedItem,0,-1,lastAttr)
                    selectedItem-=1;
                    pad.chgat(selectedItem,0,-1,curses.A_REVERSE);
                    #scroll up when we want a item that isnt showing
                    if (selectedItem < padY):
                        padY -= 1
            elif c == ord('q') or c == curses.KEY_LEFT or c == ord('h'):
                return 'q',padY,selectedItem;
            elif c == 10 or c == curses.KEY_RIGHT or c == ord('l'): #enter
                return 'return',padY, selectedItem;
            elif c == ord('r'):#update this feed
                return 'r',padY,selectedItem;
            elif c == ord('R'):
                return 'R',padY,selectedItem
            elif c == ord('A'):
                return 'A',padY,selectedItem
            elif c == ord('a'):
                return 'a',padY,selectedItem
            elif c == ord('o'):
                return 'o',padY,selectedITem

            pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)

    def showArticle(self, content):
        #split content in lines
        content = content.split('\n')
        pad = curses.newpad(len(content)+1,curses.COLS)
        pad.keypad(1)
        padY = 0;
        for i in range(0,len(content)):
            pad.addstr(i,0,content[i])
        #fill blank lines to overwrite old content
        if(len(content) < curses.LINES - 3):
            for z in range(len(content) + 1, curses.LINES-3):
                self.stdscr.addstr(z, 0, " "*curses.COLS);


        pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)
        self.stdscr.refresh()
        while(1):
            c = pad.getch()
            if c == ord('j') or c == curses.KEY_DOWN:
                if padY < len(content) and len(content) > curses.LINES - 4:
                    padY += 1;
            elif c == ord('k') or c == curses.KEY_UP:
                if (padY > 0):
                    padY -= 1
            elif c == ord('q') or c == curses.KEY_LEFT or c == ord('h'):
                return ('q',)
            elif c == 10 or c == curses.KEY_RIGHT or c == ord('l'): #enter
                pass
            pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)

    def getDimensions(self):
        return curses.LINES, curses.COLS

    def setStatus(self, message):
        self.stdscr.addstr(curses.LINES-2,0, ' '*curses.COLS)
        self.stdscr.addstr(curses.LINES-2,0, str(message));
        self.stdscr.refresh()
        return
