import sublime, sublime_plugin
from os.path import basename, splitext

class SmartInsertCommand(sublime_plugin.TextCommand):
	statement = ""
	globVoiceCommand = ""

	def run(self, edit, voiceCommand):
		global globVoiceCommand
		global statement

		globVoiceCommand = voiceCommand
		statement = self.getInsertStatement()
		originalCursorPosition = self.view.sel()[0].end()
		
		self.insertStatement(edit, originalCursorPosition)
		self.returnToOriginalCursorPosition(originalCursorPosition)


	def getInsertStatement(self):
		if (globVoiceCommand == "if-statement"):
			statement = "\n\nif ()\n{\n\n}"
		elif (globVoiceCommand == "while-loop"):
			statement = "\n\nwhile ()\n{\n\n}"
		elif (globVoiceCommand == "public-constructor"):
			statement = "public class "+ self.formatFileName(self.view.file_name()) + " \n{\n\n}"
		else:
			statement = "No matching voice command found"
		return statement

	def insertStatement(self, edit, cursorPosition):
		#insert statement; returns length of insert
		statementLength = self.view.insert(edit, cursorPosition, statement)
		#create a region containing new statement
		cursorPosition = self.view.sel()[0].begin()
		region = sublime.Region(cursorPosition, cursorPosition - statementLength)

		#indent new statement
		self.view.sel().clear()
		self.view.sel().add(region)
		self.view.run_command("reindent")

	def returnToOriginalCursorPosition(self, originalCursorPosition):
		(row, col) = self.view.rowcol(originalCursorPosition)
		target = self.view.text_point(row, col)
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(target))
		self.view.show(target)

	def formatFileName(self, fileName):
		formattedFileName = basename(fileName)
		return os.path.splitext(formattedFileName)[0]
