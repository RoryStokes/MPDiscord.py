import discord
from mpd import MPDClient
import random
import re
import atexit
import pickle

client = discord.Client()
client.login('email','password');

player = MPDClient();
player.timeout = 10;
player.connect("localhost",6600)

datafile = "data.pkl"

try:
    with open(datafile,"rb") as f:
        data = pickle.load(f)
    beatsCounts = data[0]
    beatsVoted = data[1]
except FileNotFoundError:
    beatsCounts = {}
    beatsVoted = {}

def play(channel,name):
    player.clear()
    player.add(name)
    player.play()
    if name in beatsCounts.keys() and beatsCounts[name] > 0:
        client.send_message(channel, 'What a beat!')

def exit_handler():
    print('Gotta save my shit!')

    data = [beatsCounts,beatsVoted]
    with open(datafile,"wb") as f:
        pickle.dump(data,f)

atexit.register(exit_handler)

@client.event
def on_message(message):
    content = message.content.lower()
    if any(role.name == "BeatsBotBoi" for role in message.author.roles):
        if content.startswith('!play '):
            client.send_message(message.channel, 'Searching for "'+message.content.split(' ',1)[1]+'"')
            results = player.search("any",message.content.split(' ',1)[1])
            if len(results) == 1:
                play(message.channel,results[0]['file'])
                client.send_message(message.channel, 'Playing "'+results[0]['file']+'"')
            elif len(results) == 0:
                client.send_message(message.channel, '404: Beat not found.')
            else:
                client.send_message(message.channel, 'Too many beats to choose from!')
                reply = ""
                for result in results:
                    addition =' - Found "'+result['file']+'"\n'
                    if len(reply) + len(addition) >= 2000:
                        client.send_message(message.channel, reply)
                        reply = ""
                    reply += addition
                client.send_message(message.channel, reply)
        elif content.startswith('!rand'):
            if content == "!random" or content == "!rand":
                client.send_message(message.channel, 'Playing a random song!')
            else:
                client.send_message(message.channel, 'Searching for "'+message.content.split(' ',1)[1]+'"')
            split = message.content.split(' ',1)
            if len(split) > 1:
                results = player.search("any",split[1])
                if len(results) == 0:
                    client.send_message(message.channel, '404: Beat not found.')
                else:
                    client.send_message(message.channel, 'Found '+str(len(results))+' beats')
                    result = random.choice(results)
                    play(message.channel,result['file'])
                    client.send_message(message.channel, 'Playing "'+result['file']+'"')
            else:
                result = random.choice(player.search("any",""))
                play(message.channel,result['file'])
                client.send_message(message.channel, 'Playing "'+result['file']+'"')
        elif content.startswith('!find '):
            client.send_message(message.channel, 'Searching for "'+message.content.split(' ',1)[1]+'"')
            results = player.search("any",message.content.split(' ',1)[1])
            if len(results) == 0:
                client.send_message(message.channel, '404: '+message.content.split(' ',1)[1]+' not found.')
            else:
                client.send_message(message.channel, 'Found some beats!')
                reply = ""
                for result in results:
                    addition =' - Found "'+result['file']+'"\n'
                    if len(reply) + len(addition) >= 2000:
                        client.send_message(message.channel, reply)
                        reply = ""
                    reply += addition
                client.send_message(message.channel, reply)
        elif content.startswith('!stop'):
            player.stop()
        elif content.startswith('!whatabeat') or "what a beat" in content:
            if player.status()['state'] == 'play':
                file = player.currentsong()['file']
                if file in beatsCounts.keys():
                    if message.author.id not in beatsVoted[file]:
                        beatsCounts[file] += 1
                        beatsVoted[file].append(message.author.id)
                        client.send_message(message.channel, file+" now has "+str(beatsCounts[file])+" beatzpointz")
                    else:
                        client.send_message(message.channel, "That cheeky bugger "+message.author.name+" tried to vote twice!")
                else:
                    beatsCounts[file] = 1
                    beatsVoted[file] = [message.author.id]
                    client.send_message(message.channel, file+" now has "+str(beatsCounts[file])+" beatzpointz")
            else:
                client.send_message(message.channel, "Ain't no beat here!")


        elif content == '!beat' or "hit it beatsbot" in content:
            if len(beatsCounts) > 0:
                topSong = max(beatsCounts, key=beatsCounts.get)
                if beatsCounts[topSong] == 0:
                    client.send_message(message.channel, "Used up all me beats!")
                else:
                    client.send_message(message.channel, topSong+" wins with "+str(beatsCounts[topSong])+" beatzpointz!")
                    beatsCounts[topSong] = 0
                    beatsVoted[topSong] = []
                    play(message.channel,topSong)
            else:
                client.send_message(message.channel, "No beats to blast!")
        elif content.startswith("!") and 'point' in content.split(' ',1)[0]:
            sorted_points = sorted(beatsCounts.items(), key=operator.itemgetter(1),reverse=True)
            client.send_message(message.channel, "Current beatzpointz:")
            i = 0
            while(i<len(sorted_points) and sorted_points[i][1]>0):
                client.send_message(message.channel, "["+str(sorted_points[i][1])+"] "+str(sorted_points[i][0]) )
                i+=1

    else:
        if content.startswith('!'):
            client.send_message(message.channel, "Did you mean '!play me some Nickelback'?")
            results = player.search("any","Nickelback")
            result = random.choice(results)
            play(message.channel,result['file'])
client.run()