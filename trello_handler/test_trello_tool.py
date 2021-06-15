import datetime
import json
import os
import unittest

from trello_handler.trello_tool import TrelloTool

pprint = lambda x: print(json.dumps(x, indent=4))

now = datetime.datetime.now()

key = os.environ.get('TRELLO_KEY')
token = os.environ.get('TRELLO_TOKEN')

class TestTrelloTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.my_trello_tool = TrelloTool(key, token)

    def tearDown(self):
        del self.my_trello_tool

    def test_init(self):
        self.assertEqual(len(self.my_trello_tool.key), 32)
        self.assertEqual(len(self.my_trello_tool.token), 64)
        self.assertRaises((AssertionError), TrelloTool, 'bad key', 'bad token')
        self.assertRaises((AssertionError), TrelloTool, key, 'bad token')
        self.assertRaises((AssertionError), TrelloTool, 'bad key', token)

    def test_check_connection(self):
        self.assertEqual(self.my_trello_tool.check_connection(), 'Good connection: code 200 ')

    def test_Boards(self):
        boards = self.my_trello_tool.Boards
        assert len(boards) > 0
        self.assertIsInstance(boards, dict)

    def test_Boards_setter(self):
        self.my_trello_tool.Boards = 'new value'
        self.assertEqual(self.my_trello_tool.Boards, 'new value')

    def test_get_cards(self):
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        empty_list_cards = self.my_trello_tool.get_cards(test_board['lists']['empty list']['id'])
        self.assertEqual(empty_list_cards, [])
        list_with_cards_and_comments = self.my_trello_tool.get_cards(test_board['lists']['list with cards and comments']['id'])
        self.assertIsInstance(list_with_cards_and_comments[0], dict)
        list_with_just_cards = self.my_trello_tool.get_cards(test_board['lists']['list with just cards']['id'])
        self.assertIsInstance(list_with_just_cards[0], dict)
        raw_cards = self.my_trello_tool.get_cards(test_board['lists']['list with just cards']['id'], raw=True)
        self.assertIsInstance(raw_cards[0]['badges']['attachmentsByType']['trello'], dict)

    def test_Get_list_for_board(self):
        test_board_id = self.my_trello_tool.Boards['test board']['id']
        self.my_trello_tool.Get_lists_for_board(test_board_id)
        assert len(self.my_trello_tool.Boards['test board']['lists']) > 0

    def test_get_cards_and_comments(self):
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        cards_with_comments = self.my_trello_tool.get_cards_and_comments(test_board['lists']['list with cards and comments']['id'])
        self.assertIsInstance(cards_with_comments[0]['comments'], list)
        cards_without_comments = self.my_trello_tool.get_cards_and_comments(test_board['lists']['list with just cards']['id'])
        self.assertIsInstance(cards_without_comments[0], dict)
        no_cards_no_comments = self.my_trello_tool.get_cards_and_comments(test_board['lists']['empty list']['id'])
        self.assertEqual(no_cards_no_comments, "No card on list")
        
    def test_add_cards_to_lists(self):
        nonexistant_board = self.my_trello_tool.add_cards_to_list('nonexistant board', [])
        self.assertEqual(nonexistant_board, 'Board not found')
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        cards_without_comments = self.my_trello_tool.get_cards_and_comments(test_board['lists']['list with just cards']['id'])
        self.my_trello_tool.add_cards_to_list('test board', cards_without_comments)
        self.assertRaises(KeyError, lambda: test_board['lists']['list with just cards']['cards'][0]['comments'])
        cards_with_comments = self.my_trello_tool.get_cards_and_comments(test_board['lists']['list with cards and comments']['id'])
        self.my_trello_tool.add_cards_to_list('test board', cards_with_comments)
        self.assertIsInstance(test_board['lists']['list with cards and comments']['cards'][0]['comments'], list)
        no_cards_no_comments = self.my_trello_tool.get_cards_and_comments(test_board['lists']['empty list']['id'])
        self.my_trello_tool.add_cards_to_list('test board', no_cards_no_comments)
        self.assertRaises((KeyError), lambda: test_board['lists']['empty list']['cards'])

    def test_fill_board(self):
        self.my_trello_tool.fill_board("test board")
        test_board = self.my_trello_tool.Boards["test board"]
        self.assertEqual(test_board['lists']["list with cards and comments"]['cards'][0]['comments'][0], "I'm the comment to a Trello card")

    def test_make_batch_call(self):
        result_with_comment = self.my_trello_tool.make_batch_call(f'/1/cards/60b7ca53f0073e0d9277ecd4/actions?')
        self.assertIsInstance(result_with_comment[0], dict)
        result_without_comment = self.my_trello_tool.make_batch_call(f'/1/cards/60bd268ac2f144823b7975cc/actions?')
        self.assertEqual(result_without_comment[0]["200"], [])
        result_with_bad_url = self.my_trello_tool.make_batch_call(f'/1/cards//actions?')
        self.assertEqual(result_with_bad_url, "Routes do not exist")
        
    def test_archive_card(self):
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        #Make card
        self.my_trello_tool.Post_trello_card(test_board['lists']['list with just cards']['id'], 'This is a good card to archive', 'description')
        self.my_trello_tool.fill_board('test board')
        cards = test_board['lists']['list with just cards']['cards']
        for card in cards:
            if card['name'] == 'This is a good card to archive':
                #Archive card
                result = self.my_trello_tool.archive_card(card['id'])
                self.assertEqual(result['closed'], True)
                #Delete Card
                self.my_trello_tool.Delete_trello_card(card['id'])
        
    def test_get_card_due_date(self):
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        self.my_trello_tool.Post_trello_card(test_board['lists']['list with just cards']['id'], 'This card has a due date', 'description', '5-10-25')
        self.my_trello_tool.fill_board('test board')
        cards = test_board['lists']['list with just cards']['cards']
        for card in cards:
            if card['name'] == 'This card has a due date':
                self.assertEqual(self.my_trello_tool.get_duedate(card['id']), datetime.date(2025, 5, 10))
                self.my_trello_tool.archive_card(card['id'])
                self.my_trello_tool.Delete_trello_card(card['id'])

    def test_get_dateLastActivity(self):
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        self.my_trello_tool.fill_board('test board')
        card = test_board['lists']['list with just cards']['cards'][1]
        last_activity = self.my_trello_tool.get_dateLastActivity(card['id'])
        self.assertIsInstance(last_activity, datetime.datetime)

    def test_time_since_LastActivity(self):
        test_board = self.my_trello_tool.Boards['test board']
        self.my_trello_tool.Get_lists_for_board(test_board['id'])
        self.my_trello_tool.fill_board('test board')
        card = test_board['lists']['list with just cards']['cards'][0]
        time_since_last_activity = self.my_trello_tool.time_since_LastActivity(card['id']) 
        self.assertGreater(time_since_last_activity, datetime.timedelta(minutes=15))

if __name__ == '__main__':
    unittest.main()
