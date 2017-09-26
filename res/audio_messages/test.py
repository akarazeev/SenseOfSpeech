bashCommand = "ffmpeg -i hello.ogg test_hello_from_ogg.wav"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
