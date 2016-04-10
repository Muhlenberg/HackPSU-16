import sublime, sublime_plugin, os
from os.path import basename, splitext
import urllib, json, subprocess

class SmartInsertCommand(sublime_plugin.TextCommand):
	statement = ""
	globVoiceCommand = ""
	response = ""

	def run(self, edit, voiceCommand, rresponse):
		global globVoiceCommand
		global statement
		global response

		globVoiceCommand = voiceCommand
		response = rresponse
		statement = self.getInsertStatement()
		originalCursorPosition = self.view.sel()[0].end()
		
		self.insertStatement(edit, originalCursorPosition)
		self.returnToOriginalCursorPosition(originalCursorPosition)


	def getInsertStatement(self):
		if (globVoiceCommand == "class"):
			statement = "public class " + self.formatFileName(self.view.file_name()) + " \n{\n\n}"
		elif (globVoiceCommand == "constructor"):
			statement = "public " + self.formatFileName(self.view.file_name()) + " \n{\n\n}"
		elif (globVoiceCommand == "method"):
			statement = "public <ReturnType> <defaultName>(<parameters>)\n{\n\n}"
		elif (globVoiceCommand == "if-statement"):
			statement = "\n\nif ()\n{\n\n}"
		elif (globVoiceCommand == "while-loop"):
			statement = "\n\nwhile ()\n{\n\n}"
		elif (globVoiceCommand == "for-loop"):
			statement = "\n\nfor (int i=0;i<[length];i++)\n{\n\n}"
		elif (globVoiceCommand == "open-url"):
			arg = ''.join(map(str, response.split()[2:]))
			self.openBrowser(arg)
			statement = ""
		else:
			statement = ""
			print "No matching voice command found"
		return statement

	def insertStatement(self, edit, cursorPosition):
		#insert statement; returns length of insert
		statementLength = self.view.insert(edit, cursorPosition, statement)
		#create a region containing new statement
		cursorPosition = self.view.sel()[0].begin()
		region = sublime.Region(cursorPosition, cursorPosition - statementLength)

		#indent new statement
		if statement != "":
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

	def openBrowser(self, query):
		query = urllib.urlencode ( { 'q' : query } )
		response = urllib.urlopen ( 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=3&' + query ).read().decode('unicode-escape')
		resp_json = json.loads ( response, strict=False)
		results = resp_json['responseData']['results']
		for result in results:
			url = result['url']
			subprocess.Popen(['xdg-open', url])