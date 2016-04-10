import sublime, sublime_plugin, sys, os, functools, pyaudio, urllib, urllib2, math
import audioop, wave, json, threading, time
from recorder import Recorder
from collections import deque

GOOGLE_DEFAULT_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw" #i think this is some random guys key... oh well
GOOGLE_SPEECH_URL = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-us&key=" + GOOGLE_DEFAULT_KEY

CHUNK   = 1024				#bytes to record and recognize audio 'snippet'
FORMAT = pyaudio.paInt16 	#audio stuff, dw about it
CHANNELS = 1        		#audio channel
RATE = 44100        		#audio bitrate, make sure to send the same bitrate to google
THRESHOLD=2500      		#energy threshold before something is considered not silence
RECORD_SECONDS=5    		#seconds to record (duh)

audio_filename='output.wav'

class VoiceCommand(sublime_plugin.TextCommand):
	def record(self, edit):
		print "started recording"
		rec = Recorder(channels=1)
		with rec.open(audio_filename, 'wb') as f:
			f.start_recording()
			time.sleep(5)
			f.stop_recording()

		self.send_to_google()


	def send_to_google(self):
		#convert to file to flac before sending to google
		os.system('flac -f ' + audio_filename)
		filename = audio_filename.split('.')[0] + '.flac'

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

		os.remove(filename) #remove flac file so we dont litter with files

		return res

	def run(self, edit):
		thread = threading.Thread(name='record', target=self.record, kwargs={'edit':edit})
		thread.setDaemon(True)
		thread.start()
		print "daemon started"