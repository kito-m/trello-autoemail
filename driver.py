import datetime
from os import environ
from trello_handler.trello_tool import TrelloTool
from email_handler.email_tool import Email_tool

my_email = environ.get('CBN_EMAIL_USER')
my_pw = environ.get('CBN_EMAIL_PASS')
key = environ.get('TRELLO_KEY')
token = environ.get('TRELLO_TOKEN')

emailer = Email_tool(my_email, my_pw)
trello = TrelloTool(key, token)

trello.fill_board("MJ's Board")
Mjs_board = trello.Boards["MJ's Board"]

now = datetime.datetime.now()
now = now.strftime("%A, %B %-d @ %H:%M")

line = '-' * 20
separate = lambda x: f'{line}\n\n{x}\n\n{line}\n'

receivers = {
    'Kito': "kito@coastalbreezenews.com",
    'Brianne': 'brianne@coastalbreezenews.com',
    'Val': 'val@coastalbreezenews.com',
    'Mary': 'mary@coastalbreezenews.com'
    }


def run_driver():
    log = ""
    no_messages = True
    for key in receivers.keys():
        try: 
            cards = Mjs_board['lists'][f"Notes for {key}"]['cards']
            for card in cards:
                if trello.time_since_LastActivity(card['id']) > datetime.timedelta(minutes=15):
                        
                    message = f"""
Hey {key},

You have a message from the front desk.

from: {card['name']},

description:\n{card['desc']}


Thanks,
Front Desk
                    """
                    emailer.send_email(receivers[key], 'Message from front desk', message)
                    trello.archive_card(card['id'])
                    log += separate(f'sent message to {key} :: {now}')
                    no_messages = False
                else:
                    log += separate(f'Card for {key} too new :: {now}')
                    no_messages = False
        except KeyError:
            pass
    if no_messages:
        return f"{line}\nNo messages :: {now}\n{line}"
    else:
        return log

if __name__ == '__main__':
    print(run_driver())
