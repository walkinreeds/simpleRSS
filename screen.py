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
            #these need to go global because we will handle window resize in this module
            self.topMsg = ""
            self.bottomMsg = ""
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

    def showInterface(self, topMsg = -1, bottomMsg = -1):
        if topMsg == -1:
            topMsg = self.topMsg
        else:
            self.topMsg = topMsg

        if bottomMsg == -1:
            bottomMsg = self.bottomMsg
        else:
            self.bottomMsg = bottomMsg

        if curses.has_colors():
            self.stdscr.addstr(0,0, topMsg+(" "*(curses.COLS - len(topMsg))), curses.color_pair(1));
            self.stdscr.addstr(curses.LINES-3,0, bottomMsg+(" "*(curses.COLS - len(bottomMsg))), curses.color_pair(1));
        else:
            self.stdscr.addstr(0,0, topMsg+(" "*(curses.COLS - len(topMsg))) );
            self.stdscr.addstr(curses.LINES-3,0, bottomMsg+(" "*(curses.COLS - len(bottomMsg))) );
        self.stdscr.refresh()
        return

    def showList(self, items, padY = 0, selectedItem = 0, boldItems = 0, keysMoveUp = [curses.KEY_UP, ord('k')], keysMoveDown = [curses.KEY_DOWN, ord('j')], returnKeys = []):
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
        
        #fix, select current item when redraw window
        if (selectedItem >= curses.LINES - 4):
            padY = selectedItem - (curses.LINES - 4) + 1


        currentAttr = curses.A_NORMAL
        if boldItems != 0:
            if boldItems[selectedItem] == 0:
                currentAttr = curses.A_BOLD
        pad.chgat(selectedItem,0,-1,curses.A_REVERSE | currentAttr);

        self.stdscr.refresh()
        pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)
        while (1):
            c = pad.getch()
            
            if c in keysMoveDown: #moveDown
                if (selectedItem < nrItems-1):
                    lastAttr = curses.A_NORMAL
                    currentAttr = curses.A_NORMAL
                    if boldItems != 0:
                        if boldItems[selectedItem] == 0:
                            lastAttr = curses.A_BOLD
                        if boldItems[selectedItem + 1] == 0:
                            currentAttr = curses.A_BOLD
                    pad.chgat(selectedItem,0,-1,lastAttr)
                    selectedItem+=1
                    pad.chgat(selectedItem,0,-1,curses.A_REVERSE | currentAttr);
                    #scroll down when we reach the end of the page
                    if (selectedItem >= curses.LINES - 4):
                        padY = selectedItem - (curses.LINES - 4) + 1

            elif c in keysMoveUp:#moveUp
                if (selectedItem > 0):
                    lastAttr = curses.A_NORMAL
                    currentAttr = curses.A_NORMAL
                    if boldItems != 0:
                        if boldItems[selectedItem] == 0:
                            lastAttr = curses.A_BOLD
                        if boldItems[selectedItem - 1] == 0:
                            currentAttr = curses.A_BOLD
                    pad.chgat(selectedItem,0,-1,lastAttr)
                    selectedItem-=1;
                    pad.chgat(selectedItem,0,-1,curses.A_REVERSE | currentAttr);
                    #scroll up when we want a item that isnt showing
                    if (selectedItem < padY):
                        padY -= 1

            elif c in returnKeys: #return
                return c, padY, selectedItem

            elif c == curses.KEY_RESIZE: #terminal resized
                self.resizeWindow()
                return '0',padY,selectedItem
 
            pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)

    def resizeWindow(self):
        y, x = self.stdscr.getmaxyx()
        curses.resizeterm(y,x)
        self.stdscr.clear()
        self.showInterface()
        return

    def showArticle(self, content, padY = 0, moveUpKeys = [curses.KEY_UP,ord('k')], moveDownKeys = [curses.KEY_DOWN,ord('j')], returnKeys = []):
        #split content in lines
        content = content.split('\n')
        pad = curses.newpad(len(content)+1,curses.COLS)
        pad.keypad(1)
        for i in range(0,len(content)):
            pad.addstr(i,0,content[i])
        #fill blank lines to overwrite old content
        if(len(content) < curses.LINES - 3):
            for z in range(len(content) + 1, curses.LINES-3):
                self.stdscr.addstr(z, 0, " "*curses.COLS);

        #fix when window get resized
        if padY >= len(content) - curses.LINES + 2:
            padY = len(content) - curses.LINES + 2
        if len(content) <= curses.LINES - 4: #if the content fits the window show from the beggining
            padY = 0
        #end fix

        pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)
        self.stdscr.refresh()
        while(1):
            c = pad.getch()
            if c in moveUpKeys:
                if (padY > 0):
                    padY -= 1

            elif c in moveDownKeys:
                if padY <= len(content) - curses.LINES + 2:
                    padY += 1;
            
            elif c in returnKeys:
                return c, padY

            elif c == curses.KEY_RESIZE: #terminal resized
                self.resizeWindow()
                return '0',padY

            pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)
                
    def getDimensions(self):
        return curses.LINES, curses.COLS

    def setStatus(self, message):
        self.stdscr.addstr(curses.LINES-2,0, ' '*curses.COLS)
        self.stdscr.addstr(curses.LINES-2,0, str(message));
        self.stdscr.refresh()
        return
