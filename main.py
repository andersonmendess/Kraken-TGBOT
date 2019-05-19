import json, math
from datetime import datetime
import urllib.error
import urllib.parse
import urllib.request

from telegram.ext import Updater, Filters, MessageHandler

TOKEN = "### BOT TOKEN ###"
baseURL = "https://raw.githubusercontent.com/KrakenProject/official_devices/master"
website = 'krakenproject.github.io/?device='

helpMessage = "***Commands:***\n\n/devices - get all supported devices\n/codename - get latest build"

def run(updater):
    updater.start_polling()

def command_handler(bot, update):
    print(update.message.text)
    res = handleMessage(update.message.text);
    update.message.reply_markdown(res)

def getDevices():
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read());
    res = ["***Supported Devices: ***\n\n"];
    for device in devices:
        res.append(device['name'] + ' - /' + device['codename'] + "\n")
    return ''.join(res)   

def getDeviceInfo(codename):
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read());
    for device in devices:
        if device['codename'] == codename:
            return device
    return ''

def getLastestBuild(codename):
    request = urllib.request.urlopen(baseURL + '/builds/'+codename+'.json');
    builds = json.loads(request.read());
    return builds['response'][len(builds)];

def getChangelogFile(filename, codename):
    try:
        return str(urllib.request.urlopen(baseURL + '/changedlog/' + codename + '/' + 
            filename.replace('zip','txt')).read()).split("'")[1]
    except Exception as e:
        return None

def humanSize(bytes):
    if bytes == 0:
      return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def humanDate(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y/%m/%d %H:%M')

def handleMessage(msg):
    if '/' in msg:
        # Clean and normalize the input message
        msg = msg.replace("/","")
        msg = msg.replace("@KrakenProject_bot",'')

        if msg.isupper() == True:
            msg = msg.lower()
        
        if msg.istitle() == True:
            msg = msg[0].lower() + msg[1:]

        if msg == 'devices':
            return getDevices()

        if msg == 'help':
            return helpMessage

        # grab device/build/changelog
        device = getDeviceInfo(msg)
        build = getLastestBuild(msg)
        changelog = getChangelogFile(build['filename'], msg)
          
        # setup the message and send
        if device['maintainer_name'] is not None and build['filename'] is not None:
            # dirty place XD
            res = ("***Latest Kraken for {} ({})***\n\n".format(device['name'],device['codename'])+
            "***Developer:*** [{}]({})\n".format(device['maintainer_name'], device['maintainer_url'])+
            "***Website:*** [{}]({})\n".format(device['codename'] + ' Page', website + device['codename'])+
            "***XDA:*** [{}]({})\n\n".format(device['codename'] + ' Thread', device['xda_thread'])+
            "***Build:*** [{}]({})\n".format(build['filename'], build['url'])+
            "***Size:*** {}\n".format(humanSize(int(build['size'])))+
            "***Date:*** {}\n\n".format(humanDate(int(build['datetime']))))

            # ignore changelog if needed
            if changelog is not None:
                res += ("***Changelog:***\n```\n{}```".format(changelog.replace('\\n','\n')))

            return res;

if __name__ == '__main__':
    print("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(MessageHandler(Filters.command, command_handler))

    run(updater)