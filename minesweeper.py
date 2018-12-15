import Tkinter as tk
import tkMessageBox
import random as rand
import time

'''
GridCell class objects are structures that hold the necessary data for each grid square in the game's grid.
These fields include the x and y coordinates of the grid cell, the length of the square the area encloses, and
whether or not it was clicked on yet by the user. It also has boolean values for whether or not the user
placed a flag on that cell, and whether the cell has a mine in it. It also keeps track of the number
of mines in the surrounding 8 adjacent squares of the grid cell. 
'''
class GridCell(object):
	def __init__(self, x, y, length):
		self.x = x # x location of grid cell
		self.y = y # y location of grid cell
		self.length = length # length of the grid cell
		self.clicked = False # whether or not the user has clicked the cell yet 
			# (default is false, so the cell should be concealed)
		self.hasFlag = False # whether or not the cell has a flag on it (default false)
		self.hasMine = False # whether or not the cell will have a mine in it (default false)
		self.surroundingValue = 0 # the number of mines in the 8 adjacent squares around cell (default 0)

	'''
	checkClick runs each time the user clicks on a GridCell. It determines if the click was valid
	by checking if the click coordinates were within the grid cell
	'''
	def checkClick(self, ev): 
		coords = self.getCoordinates()
		if (ev.x > coords[0]) & (ev.y > coords[1]) & (ev.x < coords[2]) & (ev.y < coords[3]):
			if self.clicked:
				return False
			return True
		return False
        	
	'''
	getCoordinates returns a 4-length tuple where the first 2 indices contain the x and y coordinates of the grid cell
	followed by the next set of x y coordinates to define the opposing vertex of the grid cell.
	'''
	def getCoordinates(self):
		return (self.x, self.y, self.x + self.length, self.y + self.length)


'''
MainScreen class is the main viewing window of the minesweeper game that houses most of the logic to display
the game using the tk inter module.
'''
class MainScreen(tk.Frame):
	def __init__(self, parent, n):
		# set up the canvas and actions for click:
		tk.Frame.__init__(self, parent)
		self.pack()
		self.parent = parent
		self.canvas_width = 1000 # width of canvas (1000 pixels)
		self.canvas_height = 800 # height of canvas (800 pixels)
		self.canvas = tk.Canvas(parent, width=self.canvas_width, height=self.canvas_height)
		self.canvas.pack()
		self.canvas.bind("<Button-1>", self.clickCellAction) # bind left mouse click to our clickCellAction() method
		self.canvas.bind("<Button-2>", self.clickFlagAction) # bind right mouse click to our clickFlagAction() method

		# initialize the game
		self.initGame(n)

		# draw the grid
		self.drawGrid(n)
		self.drawFlags()

	'''
	initGame takes in the length of the nxn game grid, n, and initializes other parameters the game needs to know
	about. In particular, it sets the pixel length of each grid square, initializes an empty game board and sets
	the default values for all the other fields we need to keep track of like the number of flags at start.
	'''
	def initGame(self, n):
		# initialize the values we need:
		self.n = n # length of grid (smallest is 10x10 grid), and also the number of mines the grid will have.
		self.padding = 5 # shift the grid from (0px, 0px) over by 5px so we can see whole grid in screen
		self.length = (self.canvas_height - self.padding) / n # length of each grid cell, resized to fit canvas height & padding
		self.grid = [[] for _ in range(n)] # initialize the our 2D grid with n empty arrays
		self.mines = {} # dict to hold (r,c) tuples for the locations of the mines. Will hold exactly n of these.
		self.flags = n # number of flags we have left to place (same as number of mines).
		self.gameover = False # boolean state to determine if the game is over yet.
		self.sec = 0 # the number of seconds the user has spent playing game so far. Increments every second.

		# initialize/fill in the grid
		self.initGrid(n)

		# draw the time text
		self.drawTime()

		# self.printGrid() # for debugging purposes only. Not part of game to viewer.

	'''
	upon the start of the game, we need to set up all the grid cell objects in our grid variable,
	and also randomly decide which grid cells will have mines (by filling in the mines dict).
	'''
	def initGrid(self, n):
		# randomly generate the unique locations of all n mines and store into the dict
		for _ in range(n):
			r = rand.randint(0, n-1)
			c = rand.randint(0, n-1)
			while (r,c) in self.mines:
				r = rand.randint(0, n-1)
				c = rand.randint(0, n-1)
			self.mines[(r,c)] = True

		# fill the 2D grid with GridCell objects
		for y in range(n):
			for x in range(n):
				coords = (x*self.length+self.padding, y*self.length+self.padding)
				cell = GridCell(coords[0], coords[1], self.length)
				if (y,x) in self.mines: # set the hasMine field in cell if its coordinates match one of mines' dict 
					cell.hasMine = True
				self.grid[y].append(cell)

		# for all grid cells that dont contain mines, count the number of surrounding mines
		for i in range(n):
			for j in range(n):
				cell = self.grid[i][j]
				if cell.hasMine == False:
					cell.surroundingValue = self.countMines(n, i, j)

	'''
	isInGrid takes in the length of the grid, n, and a row and column coordinate.
	It determines if the coordinate is within the zero-indexed 2D array boundaries to
	prevent array index out of bounds errors.
	'''
	def isInGrid(self, n, row, col):
		if row < 0 or col < 0 or row >= n or col >= n:
			return False
		return True

	'''
	countMines takes in the length of the grid, n, and a row and column coordinate.
	It determines how many mines are in the surrounding 8 squares of the cell at coordinate
	'''
	def countMines(self, n, row, col):
		# list containing coordinates of squares adjacent to current cell at (row, col)
		adjSquares = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
		count = 0 # count of the number of adjacent mines
		for i, j in adjSquares:
			r = row + i
			c = col + j
			if self.isInGrid(n, r, c) and self.grid[r][c].hasMine:
				count += 1
		return count

	'''
	drawGrid draws the actual display of the grid. we look at the grid 2D array and determine what we should
	draw at each cell's location on screen, such as the square's color, if we should print a number there, and
	if we should draw a circle for the mine there.
	'''
	def drawGrid(self, n):
		for y in range(n):
			for x in range(n):
				cell = self.grid[y][x]
				coords = cell.getCoordinates()
				clickColor = 'gray'  # the color of the square we will fill in. default is gray for unclicked
				clickText = '' # the text of square we will fill in. default is empty
				if cell.clicked and cell.hasMine == False: # if we clicked a non-mine square:
					clickColor = 'light gray' # set color to be light gray
					clickText = str(cell.surroundingValue) # set the text to be the cell's number of adjacent mines
				if cell.hasMine and self.gameover: # if the cell has a mine AND the game is over (normally we hide mines)
					clickColor = 'red' # set the color to be red
				if cell.hasFlag: # if the cell has a flag, set the color to orange
					clickColor = 'orange'
				self.canvas.create_rectangle(coords, fill=clickColor) # draw the grid cell square on screen with set color
				if cell.hasMine and self.gameover: # if the cell had a mine and game is over:
					self.canvas.create_oval(coords, fill="black") # draw a circle over that square to indicatae mine 
				# draw the text we set at the square, if any (centered by the square's opposing coordinates)
				self.canvas.create_text(((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2), text=clickText)

	'''
	drawTime draws the text on screen outside the grid to indicate the time the user has spent so far playing the game.
	'''
	def drawTime(self):
		timeText = "Time:\n%d" %(self.sec) # get the time text
		length = 100
		offset = self.padding*6
		coords = (self.length*(self.n+1), length) # set the coordinates of the text
		# draw a white rectangle over the previous iteration's time text to hide the unused pixels
		self.canvas.create_rectangle((coords[0]-offset, coords[1]-offset, coords[0]+offset, coords[1]+offset), fill='white', outline="black")
		# draw the new time text over white rectangle
		self.canvas.create_text(coords, text=timeText)
		# do not increment seconds if the game is over so the time is static upon end
		if self.gameover:
			return
		self.sec += 1 # increment time's seconds by 1
		self.parent.after(1000, self.drawTime) # after 1000 ms, run the drawTime function again to increment time.

	'''
	drawFlags will draw the text on screen outside the grid to indicate the number of flags the user has left to 
	place.
	'''
	def drawFlags(self):
		flagText = "Flags:\n" + str(self.flags) # get flag text
		offset = self.padding*6
		length = 100
		coords = (self.length*(self.n+1), length*2) # set the coordinates of text
		# draw a white rectangle over the previous iteration's flag text to hide the unused pixels
		self.canvas.create_rectangle((coords[0]-offset, coords[1]-offset, coords[0]+offset, coords[1]+offset), fill='white', outline="black")
		# draw the new flag text over white rectangle
		self.canvas.create_text(coords, text=flagText)


	# run every time we left click a cell. Checks if we clicked in a valid square before updating the grid cell
	# and redrawing grid and checking what we clicked on and if we won the game.
	def clickCellAction(self, ev):
		if self.gameover: # do not continue if game is over
			return
		n = self.n
		redrawGrid = False # boolean to determine if we need to redraw the grid
		for y in range(n):
			for x in range(n):
				cell = self.grid[y][x]
				if cell.checkClick(ev): # if the click falls inside a cell:
					if cell.hasFlag: # if the cell has a flag, return
						return
					elif cell.hasMine: # lose the game if the cell has a mine
						self.loseGame()
						return;
					# if cell has a surrounding mines value of 0, clear out all adjacent 0 cells
					elif cell.surroundingValue == 0: 
						self.clearEmptyCells(n, y, x)
					cell.clicked = True # set current cell to be clicked
					self.checkWinGame() # check if we won the game
					redrawGrid = True # we need to redraw the grid
		if redrawGrid:
			self.drawGrid(n) # redraw the grid

	# run every time we right click a cell to place a flag. Checks if we clicked a valid square before updating the
	# grid cell with flag, and then redrawing grid
	def clickFlagAction(self, ev):
		if self.gameover:
			return
		n = self.n
		redrawGrid = False
		for y in range(n):
			for x in range(n):
				cell = self.grid[y][x]
				if cell.checkClick(ev): # if valid cell click:
					if cell.hasFlag == False and self.flags > 0: # only place flag if we have flags left
						cell.hasFlag = True
						self.flags -= 1
						self.checkWinGame() # check if we won the game
					elif cell.hasFlag: # if we right click on cell with flag, it removes the flag and we get one back
						cell.hasFlag = False
						self.flags += 1
					redrawGrid = True
		if redrawGrid:
			self.drawGrid(n) # update the grid and redraw
			self.drawFlags() # update the flag text and redraw

	'''
	clearEmptyCells will recursively clear out the squares adjacent to (row, col) square that have
	0 mines adjacent to itself.
	'''
	def clearEmptyCells(self, n, row, col):
		if self.isInGrid(n, row, col) == False: # break if row and col aren't in grid
			return
		cell = self.grid[row][col]
		# if cell is already clicked, or cell has mine, or cell's surrounding mine value is not 0, break
		if cell.surroundingValue != 0 or cell.hasMine or cell.clicked: 
			return
		if cell.hasFlag: # remove flags placed on 0 mine squares we want to reveal.
			cell.hasFlag = False
			self.flags += 1
		
		# set cell as clicked
		cell.clicked = True

		# list containing coordinates of squares adjacent to current cell at (row, col)
		adjSquares = [(-1, 0), (0, -1), (0, 1), (1, 0)]
		count = 0 # count of the number of adjacent mines
		# go through the adjacent squares to current square and recursively clear out empty cells
		for i, j in adjSquares: 
			r = row + i
			c = col + j
			self.clearEmptyCells(n, r, c)

	# loseGame will end the game when the user loses (clicks on mine). It sets gameover to be True,
	# redraws the grid with all mines revealed (with red background), 
	# and shows a message dialog that tells user they lost.
	def loseGame(self):
		self.gameover = True
		self.drawGrid(self.n)
		self.showMessageBox("Game Over!", "You Lose!")

	''' 
	winGame will end the game when the user wins. It sets gameover to be True, 
	redraws the grid with all mines revealed (on top of flags), and then shows a message box that tells
	user they won and how long they spent to finish the game.
	'''
	def winGame(self):
		self.gameover = True
		self.drawGrid(self.n)
		self.showMessageBox("Game Over!", "You Win! You finished in " + str(self.sec) + " seconds")
		
	# showMessageBox displays a tkMessageBox info box with the input title and body text.
	def showMessageBox(self, title, body):
		tkMessageBox.showinfo(title, body)

	# checkWinGame scans the grid to check if the user won (if the user has placed a flag on all mines)
	def checkWinGame(self):
		for r,c in self.mines.keys():
			cell = self.grid[r][c]
			if cell.hasFlag == False:
				return
		self.winGame()

	# for debugging purposes only, not part of the game implementation
	def printGrid(self):
		n = self.n
		for i in range(n):
			for j in range(n):
				cell = self.grid[i][j]
				if cell.hasMine:
					print "*",
				else:
					print cell.surroundingValue,
			print ""

def main():
	root = tk.Tk()
	n = 10
	app = MainScreen(root, n)
	root.mainloop()

if __name__ == "__main__":
    main()