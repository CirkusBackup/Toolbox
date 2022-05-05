from urllib import request
import json


class send_message_to_slack():

    tex = 'Icecream?'
    username = 'Icecream Bot'
    icon_emoji = ':icecream:'
    channel = '#general'

    def send(self):
        self.post = {
            'text': f'{self.tex}',
            'username': f'{self.username}',
            'icon_emoji': f'{self.icon_emoji}',
            'channel': f'{self.channel}'
        }

        try:
            json_data = json.dump(self.post)

            slack_hook = None

            # Read in the slack hook id
            # with open('', 'r') as file:
            #     pass

            # TODO read in the slack bot id and send the message to it.

            # req = request.Request(
            #     slack_hook,
            #     data=json_data.enconde('ascii'),
            #     headers={'Content-Type': 'application/json'}
            # )
            # request.urlopen(req)
        except Exception as e:
            print("Exception while trying to send message to slack: " + str(e))

    # def send(self):

    #     self.post = {"text": "{0}".format(self.tex),"username": self.username,"icon_emoji": self.icon_emoji,"channel" : self.channel}

    #     try:
    #         json_data = json.dumps(self.post)
    #         file = open("C:/Users/Chris/Documents/maya/2017/scripts/toSlack","r")
    #         slackHook = file.read()
    #         req = Request(slackHook,
    #                               data=json_data.encode('ascii'),
    #                               headers={'Content-Type': 'application/json'})
    #         resp = urlopen(req)
    #     except Exception as em:
    #         print("EXCEPTION: " + str(em))


def icecreamBot():
    newBot = send_message_to_slack()
    newBot.icon_emoji = ':icecream:'
    newBot.username = 'Icecream Bot'
    newBot.tex = 'Icecream?'
    newBot.channel = '#general'
    newBot.send()

#import Tools.toSlack as toSlack;toSlack.icecreamBot()
