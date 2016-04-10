import sublime, sublime_plugin, os, subprocess, urllib, urllib2, time, json

GOOGLE_DEFAULT_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw" #i think this is some random guys key... oh well
GOOGLE_SPEECH_URL = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-us&key=" + GOOGLE_DEFAULT_KEY

audio_filename='output.wav'

class VoiceCommand(sublime_plugin.TextCommand):
	def record(self, edit):
		bashCommand="arecord -c 1 -r 44100 -N -d 5 output.wav"
		process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
		time.sleep(5)

		print "begin sending to google"
		self.send_to_google()


	def send_to_google(self):
		#convert to file to flac before sending to google
		os.system('flac -f ' + audio_filename)
		filename = audio_filename.split('.')[0] + '.flac'

		print "converted to flac"

		f = open(filename)
		content = f.read()
		f.close()

		headers = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7", 
		   'Content-type': 'audio/x-flac; rate=44100'}

		request = urllib2.Request(GOOGLE_SPEECH_URL, data=content, headers=headers)
		print("Sending audio to Google Speech API at url: " + GOOGLE_SPEECH_URL)

		try:
			stream = urllib2.urlopen(request)
			response = stream.read()
			print "full response: " + response
			
			result = json.loads(response.split("\n")[1])
			res = result['result'][0]['alternative'][0]['transcript']
			print "parsed response: " + res

		except:
			print("error connecting to google speech api")
			res = None
			raise

		os.remove(filename) #remove flac file so we dont litter with files

		return res

	def run(self, edit):
		thread = threading.Thread(name='record', target=self.record, kwargs={'edit':edit})
		thread.setDaemon(True)
		thread.start()
		print "daemon started"