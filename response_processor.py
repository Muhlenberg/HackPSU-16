class ResponseProcessor():
	def __init__(self, response):
		self.response = response

	def processResponse(self):
		if self.isCreateClass():
			statement = "class"
		elif self.isCreateConstructor():
			statement = "constructor"
		elif self.isCreateMethod():
			statement = "method"
		elif self.isCreateIfStatement():
			statement = "if-statement"
		elif self.isCreateWhileLoop():
			statement = "while-loop"
		elif self.isOpenUrl():
			statement = "open-url" 
		elif self.isCreateForLoop():
			statement = "for-loop"
		# elif self.isGoToNext():
		# 	statement = "goToNext"
		# elif isCopyCurrentLine():No matching voice command found
		# 	statement = "copyCurrentLine"
		# elif insertBelowLine():
			 # statement = "insertBelowLine"
		else:
			statement = "error"
		return statement

	def isCreateClass(self):
		dictionary = ["define", "create", "class", "add", "default"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2:
			return True
		else:
			return False

	def isCreateConstructor(self):
		dictionary = ["insert", "define", "create", "add", "constructor", "named", "called"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2:
			return True
		else:
			return False
	def isCreateMethod(self):
		dictionary = ["insert", "define", "create", "add", "method", "function", "named", "called"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2:
			return True
		else:
			return False
	def isCreateIfStatement(self):
		dictionary = ["insert", "define", "create", "add", "if", "statement", "condition"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2 and "if" in self.response:
			return True
		else:
			return False
	def isCreateWhileLoop(self):
		dictionary = ["insert", "define", "create", "add", "while", "loop", "condition"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2 and "while" in self.response:
			return True
		else:
			return False
	def isCreateForLoop(self):
		dictionary = ["insert", "define", "create", "add", "for", "loop", "condition"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2 and "for" in self.response:
			return True
		else:
			return False
	def isGoToNext(self):
		dictionary = ["go", "next", "move", "to"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 1 and "next" in self.response or "move" in self.response:
			return True
		else:
			return False

	def isOpenUrl(self):
		dictionary = ["search", "for", "google"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 1 and "search" in self.response:
			return True
		else:
			return False