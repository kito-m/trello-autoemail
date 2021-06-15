import datetime
import requests
import json

pprint = lambda x: print(json.dumps(x, indent=4))
make_EST_dt = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=-4)

class TrelloTool():
    def __init__(self, key, token):
        assert len(key) == 32
        self.key = key
        assert len(token) == 64
        self.token = token
        self.boards = {}
        self.check_connection()

    def check_connection(self):
        url = 'https://api.trello.com'
        response = requests.request(
                "GET",
                url
        )
        assert response.status_code == 200
        return 'Good connection: code 200 '

    @property
    def Boards(self):
        if self.boards == {}:
            url = 'https://api.trello.com/1/members/me/boards'
            query = {
                'key': self.key,
                'token': self.token,
            }
            response = requests.request(
                "GET",
                url,
                params=query
                )
            for board_data in json.loads(response.text):
                self.boards[board_data['name']] = {'id': board_data['id']}
            return self.boards
        else:
            return self.boards

    @Boards.setter
    def Boards(self, updated_Boards):
        self.boards = updated_Boards

#---------------Board Methods------------------------------------------
    def fill_board(self, board_name):
        board = self.Boards[board_name]
        self.Get_lists_for_board(board['id'])
        for key in board['lists'].keys():
            cards = self.get_cards_and_comments(board['lists'][key]['id'])
            self.add_cards_to_list(board_name, cards)

    def Get_lists_for_board(self, board_id):
        url = f'https://api.trello.com/1/boards/{board_id}/lists'
        query = {
            'key': self.key,
            'token': self.token,
        }
        response = requests.request(
            "GET",
            url,
            params=query
            )
        board_name = ""
        for key in self.Boards.keys():
                if self.Boards[key]['id'] == board_id:
                    board_name += key
        if board_name == "":
            print('self.my_trello_tool.Get_lists_for_board() Takes Board ID as the parameter')
            raise ValueError
        else:
            self.Boards[board_name]['lists'] = {}
            for list_data in json.loads(response.text):
                self.Boards[board_name]['lists'][list_data['name']] = {'id': list_data['id']}

 #---------------List Methods------------------------------------------
    def get_cards(self, list_id, raw=False):
        url = f"https://api.trello.com/1/lists/{list_id}/cards?"
        query = {
            'key': self.key,
            'token': self.token
        }
        response = requests.request(
            "GET",
            url,
            params=query
            )
        if response.text == 'invalid id':
            return response.text
        else:
            result = json.loads(response.text)
            if raw:
                return result
            else:
                cards = [{'name': i['name'], 'desc': i['desc'], 'id': i['id'], 'list_id': i['idList'], 'dueDate': i['due'], 'dateLastActivity': make_EST_dt(i['dateLastActivity'])} for i in result]
                return cards

    def get_cards_and_comments(self, list_id):
        cards = self.get_cards(list_id)
        if cards:
            create_comment_url = lambda x: f"/1/cards/{x}/actions?"
            url_string = ','.join([create_comment_url(card['id']) for card in cards])
            batch = self.make_batch_call(url_string)
            comments = self.extract_comments_from_batch(batch)
            comments_dict = self.zip_comment_kvps(comments)
            cards = self.add_comments_to_cards(comments_dict, cards)
            return cards
        else: 
            return 'No card on list'

    # makes a batch call that gets all the data pertaining to each specific card
    def make_batch_call(self, urls):
        url = "https://api.trello.com/1/batch?"
        query = {
            'key': self.key,
            'token': self.token,
            'urls': urls,
            }
        response = requests.request(
            "GET",
            url,
            params=query
            )
        result = response.text
        if result[:19] == 'Routes do not exist':
            return result[:19]
        else:
            return json.loads(result)

    # makes a list of 1 item dicts out of batch call. --> [**{name : single comment}]
    def extract_comments_from_batch(self, batch):
        comments = []
        for dictionary in batch:
            for i in dictionary['200']:
                try:
                    comments.append({i['data']['card']['id']: i['data']['text']})
                except (KeyError, IndexError):
                    pass
        return comments

    # takes list of kvps and combines items with same key
    def zip_comment_kvps(self, comments):
        comments_dict = {}
        for i in comments:
            for key, value in i.items():
                try:
                    comments_dict[key].append(value)
                except KeyError:
                    comments_dict[key] = [value]
        return comments_dict

    def add_cards_to_list(self, board_name, cards_including_comments):
        if cards_including_comments != 'No card on list':
            try:
                board = self.Boards[board_name]
                for key in board['lists'].keys():
                    for i in cards_including_comments:
                        if board['lists'][key]['id'] == i['list_id']:
                            try:
                                board['lists'][key]['cards'].append(i)
                            except KeyError:
                                board['lists'][key]['cards'] = [i]
            except KeyError:
                return 'Board not found'
        else:
            return 'No cards'

#---------------Card Methods------------------------------------------

    def add_comments_to_cards(self, comments_dict, cards):
        for card in cards:
            for key, value in comments_dict.items():
                if card['id'] == key:
                    card['comments'] = comments_dict[key]
        return cards

    def Post_trello_card(self, list_id, name, description, due_date=''):
        url = "https://api.trello.com/1/cards"
        query = {
            'key': self.key,
            'token': self.token,
            'idList': list_id,
            'name': name,
            'desc': description,
            'due': due_date
            }
        requests.request(
            "POST",
            url,
            params=query
            )
        return 'Card has been posted'

    def Delete_trello_card(self, card_id):
        url = f"https://api.trello.com/1/cards/{card_id}"
        response = requests.request(
            "DELETE",
            url
        )
        return response

    def move_card(self, card_id, destination_list_id):
        url = f'https://api.trello.com/1/'
        query = {
            'key': self.key,
            'token': self.token,
            'idList': destination_list_id,
            'cards': card_id
            }
        requests.request(
            "PUT",
            url,
            params=query
            )
        return 'Card has been moved.'

    def archive_card(self, card_id):
        url = f'https://api.trello.com/1/cards/{card_id}'
        query = {
            'key': self.key,
            'token': self.token,
            'closed': 'true'
        }
        response = requests.request(
            "PUT",
            url,
            params=query
        )
        return json.loads(response.text)

    def get_duedate(self, card_id):
        url = f'https://api.trello.com/1/cards/{card_id}/due?'
        query = {
            'key': self.key,
            'token': self.token,
        }
        response = requests.request(
            "GET",
            url,
            params=query
        )
        result = json.loads(response.text)
        date_string = result['_value']
        due_date = datetime.datetime.strptime(date_string[:date_string.index("T")], "%Y-%m-%d").date()
        return due_date

    def get_dateLastActivity(self, card_id):
        url = f'https://api.trello.com/1/cards/{card_id}/dateLastActivity?'
        query = {
            'key': self.key,
            'token': self.token,
        }
        response = requests.request(
            "GET",
            url,
            params=query
        )
        result = json.loads(response.text)
        date_string = result['_value']
        dateLastActivity = make_EST_dt(date_string)
        return dateLastActivity

    def time_since_LastActivity(self, card_id):
        LastActivity = self.get_dateLastActivity(card_id)
        time_since = datetime.datetime.now() - LastActivity
        return time_since
