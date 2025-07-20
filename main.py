from flask import Flask, render_template, redirect, url_for, request
from gtts import gTTS
import os
import pygame
import threading
from time import sleep
from colorama import Fore, Back, Style

os.chdir(os.path.dirname(os.path.abspath(__file__))) #change to the current dir because python in cmd line is fucking stupid

# 1) go into command prompt
# 2) type "ipconfig" and hit enter
# 3) change HOST to your IPv4 address
HOST = "192.168.1.98"
PORT = 8001
# fyi: to go to the locally hosted server, it will be under (http://HOST:PORT)


gttsDomains = {
    "British": ["en", "co.uk"],
    "American": ["en", "us"],
    "Indian": ["en", "co.in"],
    "Nigerian": ["en", "com.ng"],
    "French": ["fr", "fr"],
    "Chinese": ["zh-CN", "us"],
    "Mexican": ["es", "es"]
}


class audioQueue():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.is_playing = False
        self.queue = []
        self.stopQueued = False

    def startPlaying(self):
        if self.is_playing:
            print(Fore.RED + "Player already playing" + Fore.RESET)
            return
        
        print(Fore.YELLOW + "Audio player started" + Fore.RESET)

        while self.stopQueued == False:
            audioList = os.listdir("audioFiles")

            if not self.queue: #Queue is empty
                sleep(1)
                continue

            file = self.queue[0] 
            if file in audioList: #make sure first queued audiofile is actually in the audioFiles dir
                self.is_playing = True
                self.queue.pop(0)

                pygame.mixer.music.load(str("audioFiles/" + file))
                pygame.mixer.music.play()
                print(Fore.MAGENTA + "Playing Audio:  " + file + Fore.RESET)

                while pygame.mixer.music.get_busy() == True:
                    continue

                pygame.mixer.music.unload()
                os.remove("audioFiles/" + file)
            else:
                self.queue.pop(0)
                print(Fore.RED + f"Could not find '{file}' in audio dir")
        
        print(Fore.YELLOW + "Audio player stopped" + Fore.RESET)
        self.is_playing = False
        self.stopQueued = False

    def stopPlaying(self):
        self.stopQueued = True


def queueNewTTS(text, accent):
    tts = gTTS(text, lang=gttsDomains[accent][0], tld=gttsDomains[accent][1])
    tts.save(f"audioFiles/{text[:20]}.mp3")
    player.queue.append(text[:20] + ".mp3")
    print(Fore.GREEN + f"Text added to queue ({accent}): " + Fore.CYAN + text + Fore.RESET)


app = Flask(__name__, template_folder='templates', static_folder='static')

player = audioQueue()
playerThread = threading.Thread(target=player.startPlaying)
playerThread.daemon = True
playerThread.start()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.form["textinput"] != "":

        textinput = request.form["textinput"]
        accentInput = request.form["accentinput"]
        queueNewTTS(textinput, accentInput)

        return render_template("index.html")
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
    print("Webserver closed")