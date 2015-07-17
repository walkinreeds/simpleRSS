import curses, traceback
import sys, os

PAIR_TOPBAR = 1
PAIR_BOTTOMBAR = 2
PAIR_NORMAL_UNSELECTED = 3
PAIR_NORMAL_SELECTED = 5
PAIR_UNREAD_UNSELECTED = 4
PAIR_UNREAD_SELECTED = 6

class screen(object):
    def __init__(self, config = None):
        self.stdscr = None
        try:
            #initialize curses
            self.stdscr = curses.initscr()
            curses.start_color()
            if curses.has_colors():
                self.processColors(config)
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            self.stdscr.keypad(1)
            #these need to go global because we will handle window resize in this module
            self.topMsg = ""
            self.bottomMsg = ""
        except Exception as e:
            #error ocurred, restore terminal
            self.close()
            print(e)
            traceback.print_exc() #print the exception
        return

    def close(self):
        if (self.stdscr != None):
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

        topMsg = self.fitContent(topMsg,curses.COLS)[0]
        bottomMsg = self.fitContent(bottomMsg,curses.COLS)[0]
        if curses.has_colors():
            self.stdscr.addstr(0,0, topMsg+(" "*(curses.COLS - len(topMsg))), curses.color_pair(PAIR_TOPBAR));
            self.stdscr.addstr(curses.LINES-2,0, bottomMsg+(" "*(curses.COLS - len(bottomMsg))), curses.color_pair(PAIR_BOTTOMBAR));
            self.setStatus(""); #make status bar match normal_unselected color
        else:
            self.stdscr.addstr(0,0, topMsg+(" "*(curses.COLS - len(topMsg))) );
            self.stdscr.addstr(curses.LINES-2,0, bottomMsg+(" "*(curses.COLS - len(bottomMsg))) );
        self.stdscr.refresh()
        return

    def showList(self, items = [], padY = 0, selectedItem = 0, readItems = [], keysMoveUp = [curses.KEY_UP, ord('k')], keysMoveDown = [curses.KEY_DOWN, ord('j')], returnKeys = []):
        nrItems = len(items);
        #feed list
        pad = curses.newpad(nrItems + 1,curses.COLS)
        pad.keypad(1)
        for i in range(0,nrItems):
            fill = " "*(curses.COLS - len(items[i]))
            pad.addstr(i, 0, " {0}{1}".format(items[i], fill),curses.color_pair(PAIR_NORMAL_UNSELECTED))
            if (len(readItems) == nrItems) and (nrItems > 0):
                if readItems[i] == 0:
                    pad.chgat(i,0,-1,curses.A_BOLD | curses.color_pair(PAIR_UNREAD_UNSELECTED))

        #fill blank lines to overwrite old content
        if curses.has_colors():
            pad.chgat(nrItems, 0, -1, curses.color_pair(PAIR_NORMAL_UNSELECTED))
        if(nrItems < curses.LINES - 2):
            for z in range(nrItems - 1, curses.LINES-2):
                if curses.has_colors():
                    self.stdscr.addstr(z, 0, " "*curses.COLS, curses.color_pair(PAIR_NORMAL_UNSELECTED))
                else:
                    self.stdscr.addstr(z, 0, " "*curses.COLS);
        
        #fix, select current item when redraw window
        if (selectedItem >= curses.LINES - 3):
            padY = selectedItem - (curses.LINES - 3) + 1


        currentAttr = curses.A_NORMAL
        if (len(readItems) == nrItems) and (nrItems > 0):
            if readItems[selectedItem] == 0:
                currentAttr = curses.A_BOLD

        #selected item - 0
        if (curses.has_colors()):
            if (currentAttr == curses.A_BOLD): #is unread
                pad.chgat(selectedItem,0,-1, currentAttr | curses.color_pair(PAIR_UNREAD_SELECTED));
            else:
                pad.chgat(selectedItem,0,-1, currentAttr | curses.color_pair(PAIR_NORMAL_SELECTED));
        else:
            pad.chgat(selectedItem,0,-1,curses.A_REVERSE | currentAttr);

        self.stdscr.refresh()
        pad.refresh(padY,0,1,0,curses.LINES-3,curses.COLS)
        while (1):
            c = pad.getch()
            
            if c in keysMoveDown: #moveDown
                if (selectedItem < nrItems-1):
                    lastAttr = curses.A_NORMAL
                    lastColor = curses.color_pair(PAIR_NORMAL_UNSELECTED);
                    currentAttr = curses.A_NORMAL
                    currentColor = curses.color_pair(PAIR_NORMAL_SELECTED);
                    if (len(readItems) == nrItems) and (nrItems > 0):
                        if readItems[selectedItem] == 0:
                            lastAttr = curses.A_BOLD
                            lastColor = curses.color_pair(PAIR_UNREAD_UNSELECTED) 
                        if readItems[selectedItem + 1] == 0:
                            currentAttr = curses.A_BOLD
                            currentColor = curses.color_pair(PAIR_UNREAD_SELECTED)
                    if (curses.has_colors()):
                        pad.chgat(selectedItem+1,0,-1, currentAttr | currentColor);
                        pad.chgat(selectedItem,0,-1, lastAttr | lastColor)
                    else:
                        pad.chgat(selectedItem,0,-1,lastAttr)
                        pad.chgat(selectedItem+1,0,-1,curses.A_REVERSE | currentAttr);
                    selectedItem+=1
                    #scroll down when we reach the end of the page
                    if (selectedItem >= curses.LINES - 3):
                        padY = selectedItem - (curses.LINES - 3) + 1

            elif c in keysMoveUp:#moveUp
                if (selectedItem > 0):
                    lastAttr = curses.A_NORMAL
                    lastColor = curses.color_pair(PAIR_NORMAL_UNSELECTED);
                    currentAttr = curses.A_NORMAL
                    currentColor = curses.color_pair(PAIR_NORMAL_SELECTED);
                    if readItems != 0:
                        if readItems[selectedItem] == 0:
                            lastAttr = curses.A_BOLD
                            lastColor = curses.color_pair(PAIR_UNREAD_UNSELECTED) 
                        if readItems[selectedItem - 1] == 0:
                            currentAttr = curses.A_BOLD
                            currentColor = curses.color_pair(PAIR_UNREAD_SELECTED)
                    if (curses.has_colors()):
                        pad.chgat(selectedItem-1,0,-1, currentAttr | currentColor);
                        pad.chgat(selectedItem,0,-1, lastAttr | lastColor)
                    else:
                        pad.chgat(selectedItem,0,-1,lastAttr)
                        pad.chgat(selectedItem-1,0,-1,curses.A_REVERSE | currentAttr);
                    selectedItem-=1;
                    #scroll up when we want a item that isnt showing
                    if (selectedItem < padY):
                        padY -= 1

            elif c in returnKeys: #return
                return c, padY, selectedItem

            elif c == curses.KEY_RESIZE: #terminal resized
                self.resizeWindow()
                return '0',padY,selectedItem
 
            pad.refresh(padY,0,1,0,curses.LINES-3,curses.COLS)

    def resizeWindow(self):
        y, x = self.stdscr.getmaxyx()
        curses.resizeterm(y,x)
        self.stdscr.clear()
        self.showInterface()
        return

    def fitContent(self,content,cols):
        content = ''.join(content) #convert to string
        resultContent = []
        line = ""

        for i in range(0,len(content)):
           line = line + content[i]
           if len(line) == cols or content[i] == "\n" or (content[i] == " " and len(line) > cols - 5):
               resultContent.append(line)
               line = "";

        if len(line)>0:
            resultContent.append(line)
        return resultContent

    def showArticle(self, content, padY = 0, moveUpKeys = [curses.KEY_UP,ord('k')], moveDownKeys = [curses.KEY_DOWN,ord('j')], returnKeys = []):
        content = self.fitContent(content, curses.COLS - 1)
        pad = curses.newpad(len(content)+1,curses.COLS)
        pad.keypad(1)

        boldStatus = False #is bold attribute active?
        prevChar = 0
        for y in range(0,len(content)):
            posX = 0;
            for x in range(0, len(content[y])):
                try:
                    #Bold - Text in bold are surrounded by **
                    if (content[y][x] == "*"):
                        if (prevChar == "*"):
                            boldStatus = not boldStatus #toggle bold status
                            if (boldStatus == True):
                                pad.attron(curses.A_BOLD);
                            else:
                                pad.attroff(curses.A_BOLD);
                            posX = posX - 1; #go one position back to delete the **
                            continue;
                    #End Bold

                    prevChar = content[y][x]
                    pad.addch(y,posX,content[y][x])
                    posX += 1
                except Exception as e:
                    pad.addstr(y,x,'-')
            #end line
            if curses.has_colors():
                pad.chgat(y,0,-1,curses.color_pair(PAIR_NORMAL_UNSELECTED))

        #fill blank lines to overwrite old content
        if(len(content) < curses.LINES - 3):
            for z in range(len(content) + 1, curses.LINES-2):
                if curses.has_colors():
                    self.stdscr.addstr(z, 0, " "*curses.COLS, curses.color_pair(PAIR_NORMAL_UNSELECTED));
                else:
                    self.stdscr.addstr(z, 0, " "*curses.COLS);

        #fix when window get resized
        if padY >= len(content) - curses.LINES + 2:
            padY = len(content) - curses.LINES + 2
        if len(content) <= curses.LINES - 3: #if the content fits the window goto top 
            padY = 0
        #end fix

        pad.refresh(padY,0,1,0,curses.LINES-3,curses.COLS)
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

            pad.refresh(padY,0,1,0,curses.LINES-3,curses.COLS)
                
    def getDimensions(self):
        return curses.LINES, curses.COLS

    def setStatus(self, message):
        self.stdscr.insstr(curses.LINES-1,0, ' '*curses.COLS, curses.color_pair(PAIR_NORMAL_UNSELECTED))
        self.stdscr.insstr(curses.LINES-1,0, str(message), curses.color_pair(PAIR_NORMAL_UNSELECTED));
        self.stdscr.refresh()
        return

    def setWindowTitle(self, title):
        compatibleTerminals = ['xterm', 'rxvt-unicode-256color', 'rxvt-unicode']
        if os.getenv("TERM") in compatibleTerminals:
            print("\x1B]0;%s\x07" % title) 
        return

    def processColors(self, colors):
        if colors == None:
            colors = {"":""}
        #index - foreground - background
        if "color_topbar" in colors.keys():
            fg,bg = colors['color_topbar'].split(',');
            curses.init_pair(PAIR_TOPBAR, int(fg), int(bg));
        else:
            curses.init_pair(PAIR_TOPBAR, 0, 7);

        if "color_bottombar" in colors.keys():
            fg,bg = colors['color_bottombar'].split(',');
            curses.init_pair(PAIR_BOTTOMBAR, int(fg), int(bg));
        else:
            curses.init_pair(PAIR_BOTTOMBAR, 0, 7)

        if "color_listitem" in colors.keys():
            fg,bg = colors['color_listitem'].split(',');
            curses.init_pair(PAIR_NORMAL_UNSELECTED, int(fg), int(bg));
        else:
            curses.init_pair(PAIR_NORMAL_UNSELECTED, 7, 0)

        if "color_listitem_selected" in colors.keys():
            fg,bg = colors['color_listitem_selected'].split(',');
            curses.init_pair(PAIR_NORMAL_SELECTED, int(fg), int(bg));
        else:
            curses.init_pair(PAIR_NORMAL_SELECTED, 0, 7)

        if "color_listitem_unread" in colors.keys():
            fg,bg = colors['color_listitem_unread'].split(',');
            curses.init_pair(PAIR_UNREAD_UNSELECTED, int(fg), int(bg));
        else:
            curses.init_pair(PAIR_UNREAD_UNSELECTED, 1, 0)

        if "color_listitem_unread_selected" in colors.keys():
            fg,bg = colors['color_listitem_unread_selected'].split(',');
            curses.init_pair(PAIR_UNREAD_SELECTED, int(fg), int(bg));
        else:
            curses.init_pair(PAIR_UNREAD_SELECTED, 1, 7)
