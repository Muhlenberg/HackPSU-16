class ResponseProcessor():
	def __init__(self, response):
		self.response = response

	def processResponse(self):
		if self.isCreateClass():
			statement = "class"
		elif self.isCreateNamedConstructor():
			statement = "named-constructor"
		elif self.isCreateUnamedConstructor():
			statement = "unamed-constructor"
		elif self.isCreateNamedMethod():
			statement = "named-method"
		elif self.isCreatedUnamedMethod():
			statement = "unamed-method"
		elif self.isCreateIfStatement():
			statement = "if-statement"
		elif self.isCreateWhileLoop():
			statement = "while-loop"
		elif self.isCreateForLoop():
			statement = "for-loop"
		elif self.isGoToNext():
			statement = "goToNext"
		# elif isCopyCurrentLine():
		# 	statement = "copyCurrentLine"
		# elif insertBelowLine():
			statement = "insertBelowLine"
		else:
			statement = "error"
		return statement;

	def isCreateClass(self):
		dictionary = ["define", "create", "class", "add", "default"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2:
			return True;
		else:
			return False;
	def isCreateNamedConstructor(self):
		dictionary = ["define", "create", "add", "constructor", "named", "called"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 3:
			return True;
		else:
			return False;
	def isCreateUnamedConstructor(self):
		dictionary = ["define", "create", "add", "constructor"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2:
			return True;
		else:
			return False;
	def isCreateNamedMethod(self):
		dictionary = ["define", "create", "add", "method", "function", "named", "called"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 3:
			return True;
		else:
			return False;
	def isCreatedUnamedMethod(self):
		dictionary = ["define", "create", "add", "method", "function"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2:
			return True;
		else:
			return False;
	def isCreateIfStatement(self):
		dictionary = ["define", "create", "add", "if", "statement", "condition"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2 and "if" in self.response:
			return True;
		else:
			return False;
	def isCreateWhileLoop(self):
		dictionary = ["define", "create", "add", "while", "loop", "condition"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2 and "while" in self.response:
			return True;
		else:
			return False;
	def isCreateForLoop(self):
		dictionary = ["define", "create", "add", "for", "loop", "condition"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 2 and "for" in self.response:
			return True;
		else:
			return False;
	def isGoToNext(self):
		dictionary = ["go", "next", "move", "to"]
		count = 0
		for w in dictionary:
			if w in self.response:
				count+=1
		if count >= 1 and "next" in self.response or "move" in self.response:
			return True;
		else:
			return False;
