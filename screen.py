import curses, traceback

class screen(object):
    def __init__(self):
        try:
            #initialize curses
            self.stdscr = curses.initscr()
            curses.start_color()
            curses.init_pair(1, 136, 235)
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

    def showInterface(self, unreadCount):
        #header
        title = "cursesRSS 0.1 - {0} unread".format(unreadCount);
        self.stdscr.addstr(0,0, title+(" "*(curses.COLS - len(title))), curses.color_pair(1));
        #footer
        bottom = "{0} x {1}".format(curses.COLS,curses.LINES)
        self.stdscr.addstr(curses.LINES-3,0, bottom+(" "*(curses.COLS - len(bottom))), curses.color_pair(1));
        self.stdscr.refresh()
        return

    def showList(self, items, padY = 0, selectedItem = 0):
        nrItems = len(items);
        #feed list
        pad = curses.newpad(nrItems+1,curses.COLS)
        pad.keypad(1)
        for i in range(0,nrItems):
            pad.addstr(i, 0, " {0}{1}".format(items[i], " "*(curses.COLS - len(items[i]))))

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
                    pad.chgat(selectedItem,0,-1,curses.A_NORMAL);
                    selectedItem+=1;
                    pad.chgat(selectedItem,0,-1,curses.A_REVERSE);
                    #scroll down when we reach the end
                    if (selectedItem >= curses.LINES - 4):
                        padY = selectedItem - (curses.LINES - 4) + 1
            elif c == ord('k') or c == curses.KEY_UP:
                if (selectedItem > 0):
                    pad.chgat(selectedItem,0,-1,curses.A_NORMAL);
                    selectedItem-=1;
                    pad.chgat(selectedItem,0,-1,curses.A_REVERSE);
                    #scroll up when we want a item that isnt showing
                    if (selectedItem < padY):
                        padY -= 1
            elif c == ord('q') or c == curses.KEY_LEFT or c == ord('h'):
                return ('q',);
            elif c == 10 or c == curses.KEY_RIGHT or c == ord('l'): #enter
                return 'return',padY, selectedItem;
            elif c == ord('r'):#update this feed
                return 'r',padY,selectedItem;
            elif c == ord('R'):
                return 'R',padY,selectedItem

            pad.refresh(padY,0,1,0,curses.LINES-4,curses.COLS)

    def showArticle(self, content):
        #split content in lines
        content = self.fitContent(content, curses.COLS)
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

    def fitContent(self,content,cols):
        content = ''.join(content) #convert to string
        resultContent = []
        line = ""
        for i in range(0,len(content)):
           line = line + content[i]
           if len(line) == cols or content[i] == "\n":
               resultContent.append(line)
               line = "";

        if len(line)>0:
            resultContent.append(line)
        return resultContent

    def setStatus(self, message):
        self.stdscr.addstr(curses.LINES-2,0, str(message));
        self.stdscr.refresh()
        return
