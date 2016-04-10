import subprocess

bashCommand="arecord -c 1 -r 44100 -N -d 5 test.wav"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output = process.communicate()[0]