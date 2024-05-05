import time, pickle, os.path
import telepot  # https://github.com/nickoala/telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from match import *
from phrases import text

class tgchessBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        '''Set up local variables'''
        super(tgchessBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self.gamelog = {}
        self.msglog = []
        self.statslog = {} # Store player stats [W, D, L]

        self.startsheet, self.helpsheet = self.generate_sheets()

    def generate_sheets(self):
        startsheet = "Hello! This is the Telegram Chess Bot @TeleChessRobot. \U0001F601\n"
        startsheet += "For the full command list, type `/help`.\n"
        startsheet += "(You may want to use `/help@TeleChessRobot` instead if there are multiple bots in your chat.)\n\n"
        startsheet += "*About*\n\n"
        startsheet += "You can play chess using @TeleChessRobot. To play with friends, create a group and invite @TeleChessRobot into it. If you wish to play alone, talk to @TeleChessRobot on a 1-on-1 private message.\n\n"
        startsheet += "_How to play_: Someone creates a game and picks a colour (white or black). Someone else (could be the same person) joins and is automatically assigned the other side.\n\n"
        startsheet += "_Make your best move_: Make a move by typing `/move <your move>` or just `<your move>`. @TeleChessRobot is able to recognise both SAN and UCI notations. E.g. `/move e4` or `/move e2e4`, `/move Nf3` or `g1f3`\n\n"
        startsheet += "Every chat conversation is capped to have only 1 match going on at any point in time to avoid confusion (In case multiple people try to play matches simultaneously in the same group chat). For a more enjoyable experience, you may wish to create a group chat with 3 members: You, your friend/opponent and @TeleChessRobot\n\n"
        startsheet += "*Inline Commands*\n\n"
        startsheet += "You may also make use of inline commands by typing `@TeleChessRobot <command>`.\n"
        startsheet += "Currently available commands: `@TeleChessRobot /start`, `@TeleChessRobot /help`, `@TeleChessRobot /stats`.\n\n"
        startsheet += "`@TeleChessRobot /stats` displays how many wins, draws and losses you accumulated across all games you have played via @TeleChessRobot. If user base grows sufficiently large, we intend to incorporate a global ELO rating system.\n\n"
        startsheet += "At the moment, we are unable to support inline commands to play your matches unfortunately.\n\n"
        startsheet += "*Contact*\n\n"
        startsheet += "Contact me at @mahdavifar2002 for bug reports, etc."

        helpsheet = "Allowed commands:\n"
        helpsheet += "`/help`: Display help sheet\n"
        helpsheet += "`/create <white/black>`: Creates a chess match with your preferred colour. E.g. `/create white`\n"
        helpsheet += "`/join`: Join the existing match\n"
        helpsheet += "`/show`: Show current board state\n"
        helpsheet += "`/move <move>` or `<move>`: Make a move using SAN or UCI. E.g. `/move e4` or `/move e2e4`, `/move Nf3` or `g1f3`. To learn more: [https://en.wikipedia.org/wiki/Algebraic_notation_(chess)]\n"
        helpsheet += "`/undo`: Unmake the last move of computer and yours.\n"
        helpsheet += "`/level <number>`: Change level of game difficulty. The number represents how long (in second) the computer will think before making the move.\n"
        helpsheet += "`/offerdraw`: Offer a draw. Making a move automatically cancels any existing draw offers.\n"
        helpsheet += "`/rejectdraw`: Reject opponent's draw offer. Making a move automatically rejects any existing draw offers.\n"
        helpsheet += "`/claimdraw`: Accept a draw offer or claim a draw when `fifty-move rule` or `threefold repetition` is met. To learn more: [https://en.wikipedia.org/wiki/Draw_(chess)]\n"
        helpsheet += "`/resign`: Resign from the match\n"
        helpsheet += "`/stats`: View your game stats across all matches\n\n"
        helpsheet += "If there are multiple bots, append `@TeleChessRobot` behind your commands. E.g. `/move@TeleChessRobot e4`"

        return startsheet, helpsheet

    def save_state(self):
        '''Saves gamelog, msglog and statslog for persistence'''
        with open("gamelog.txt", "wb") as f:
            pickle.dump(self.gamelog, f)

        with open("msglog.txt", "wb") as f:
            pickle.dump(self.msglog, f)

        with open("statslog.txt", "wb") as f:
            pickle.dump(self.statslog, f)

    def load_state(self):
        '''Loads gamelog, msglog and statslog for persistence'''
        try:
            with open("gamelog.txt", "rb") as f:
                self.gamelog = pickle.load(f)
        except EOFError:
            self.gamelog = {}

        try:
            with open("msglog.txt", "rb") as f:
                self.msglog = pickle.load(f)
        except EOFError:
            self.msglog = []

        try:
            with open("statslog.txt", "rb") as f:
                self.statslog = pickle.load(f)
        except EOFError:
            self.statslog = {}

    def is_in_game(self, players, sender_id):
        '''Checks if message sender is involved in the match'''
        return sender_id == players[0] or sender_id == players[2]

    def lang(self, chat_id):
        try:
            return self.statslog[chat_id][3]
        except:
            return 'en'

    def init_stats(self, player_id, lang='en'):
        self.statslog[player_id] = [0,0,0, lang]

    def game_end(self, chat_id, players, winner):
        '''Handle end of game situation'''
        # Remove match from game logs
        del self.gamelog[chat_id]

        # Update player stats [W, D, L] and print results
        if players[0] not in self.statslog: self.init_stats(players[0])
        if players[2] not in self.statslog: self.init_stats(players[2])
        white_stats = self.statslog[players[0]]
        black_stats = self.statslog[players[2]]

        # Format and send game outcome
        outcome = ""
        if winner == "White":
            white_stats[0] += 1
            black_stats[2] += 1
            outcome = "White wins! {} (W) versus {} (B) : 1-0".format(players[1], players[3])
        elif winner == "Black":
            white_stats[2] += 1
            black_stats[0] += 1
            outcome = "Black wins! {} (W) versus {} (B) : 0-1".format(players[1], players[3])
        elif winner == "Draw":
            white_stats[1] += 1
            black_stats[1] += 1
            outcome = "It's a draw! {} (W) versus {} (B) : 0.5-0.5".format(players[1], players[3])
        self.statslog[players[0]] = white_stats
        self.statslog[players[2]] = black_stats

        bot.sendMessage(chat_id, outcome)

    def get_sender_details(self, msg):
        '''Extract sender id and name to be used in the match'''
        sender_id = msg["from"]["id"]
        if "username" in msg["from"]:
            sender_username = msg["from"]["username"]
        elif "last_name" in msg["from"]:
            sender_username = msg["from"]["last_name"]
        elif "first_name" in msg["from"]:
            sender_username = msg["from"]["first_name"]
        else:
            sender_username = "Nameless"
        return sender_id, sender_username

    def get_games_involved(self, sender_id):
        return [g for g in self.gamelog.values() if self.is_in_game(g.get_players(), sender_id)]
    
    def create_game(self, chat_id, sender_id, sender_username, color):
        self.gamelog[chat_id] = Match(chat_id)
        match = self.gamelog[chat_id]

        bot.sendMessage(chat_id, text[2][self.lang(chat_id)].format(sender_username, color), parse_mode = "Markdown")

        if color == "white":
            match.joinw(sender_id, sender_username)
            match.joinb(-1, "Computer")
        else:
            match.joinb(sender_id, sender_username)
            match.joinw(-1, "Computer")
            ai_move = match.ai_move()
            res = match.make_move(ai_move)
            bot.sendMessage(chat_id, ai_move)


    def on_chat_message(self, msg):
        self.msglog.append(msg)
        content_type, chat_type, chat_id = telepot.glance(msg)
        sender_id, sender_username = self.get_sender_details(msg)
        print(msg, sender_id, sender_username)

        # Note:
        # if chat_id == sender_id, then it's a human-to-bot 1-on-1 chat
        # if chat_id != sender_id, then chat_id is group chat id
        print('Chat Message:', content_type, chat_type, chat_id, msg[content_type])

        tokens = msg[content_type].split(" ")
        match = self.gamelog[chat_id] if chat_id in self.gamelog.keys() else None
        players = match.get_players() if match != None else None

        if tokens[0] == "شروع" or tokens[0] == "/start" or tokens[0] == "/start@TeleChessRobot":
            if sender_id not in self.statslog: self.init_stats(sender_id, 'en')
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🇮🇷 فارسی', callback_data='fa'), InlineKeyboardButton(text='🇬🇧 English', callback_data='en')],
            ])

            bot.sendMessage(chat_id, text[0][self.lang(chat_id)], parse_mode = "Markdown", disable_web_page_preview = True, reply_markup=keyboard)
        elif tokens[0] == "راهنما" or tokens[0] == "/help" or tokens[0] == "/help@TeleChessRobot":
            bot.sendMessage(chat_id, text[1][self.lang(chat_id)], parse_mode = "Markdown", disable_web_page_preview = True)
        elif tokens[0] == "برگشت" or tokens[0] == "/undo" or tokens[0] == "/undo@TeleChessRobot":
            if match == None:
                bot.sendMessage(chat_id, text[3][self.lang(chat_id)])
            else:
                try:
                    match.undo_move()
                    bot.sendMessage(chat_id, text[4][self.lang(chat_id)], parse_mode = "Markdown", disable_web_page_preview = True)
                except:
                    bot.sendMessage(chat_id, text[5][self.lang(chat_id)], parse_mode = "Markdown", disable_web_page_preview = True)
        elif tokens[0] == "سطح" or tokens[0] == "/level" or tokens[0] == "/level@TeleChessRobot":
            if len(tokens) < 2 or not tokens[1].isdigit():
                bot.sendMessage(chat_id, text[6][self.lang(chat_id)], parse_mode='Markdown')
            elif match == None:
                bot.sendMessage(chat_id, text[7][self.lang(chat_id)])
            else:
                match.level = int(tokens[1])
                bot.sendMessage(chat_id, text[8][self.lang(chat_id)])
        elif tokens[0] == "ایجاد" or tokens[0] == "/create" or tokens[0] == "/create@TeleChessRobot":
            # !create <current player color: white/black>
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='⬜', callback_data='white'), InlineKeyboardButton(text='⬛', callback_data='black')],
            ])

            if match != None:
                bot.sendMessage(chat_id, text[9][self.lang(chat_id)])
            elif len(tokens) < 2:
                bot.sendMessage(chat_id, text[10][self.lang(chat_id)], parse_mode='Markdown', reply_markup=keyboard)
            else:
                color = tokens[1].lower()
                if color != "white" and color != "black":
                    bot.sendMessage(chat_id, text[10][self.lang(chat_id)], parse_mode='Markdown', reply_markup=keyboard)
                else:
                    self.create_game(chat_id, sender_id, sender_username, color)
        elif tokens[0] == "/join" or tokens[0] == "/join@TeleChessRobot":
            if match == None:
                bot.sendMessage(chat_id, "There is no chess match going on.")
            elif match.white_id != None and match.black_id != None:
                bot.sendMessage(chat_id, "Game is already full.")
            else:
                match.join(sender_id, sender_username)
                players = match.get_players()
                bot.sendMessage(chat_id, "Chess match joined.\n{} (W) versus {} (B)".format(players[1], players[3]), parse_mode = "Markdown")

                # Print starting game state
                filename = match.print_board(chat_id)
                turn_id = match.get_turn_id()
        elif tokens[0] == "تصویر" or tokens[0] == "/show" or tokens[0] == "/show@TeleChessRobot":
            if match == None:
                bot.sendMessage(chat_id, "There is no chess match going on.")
            elif match.white_id == None or match.black_id == None:
                bot.sendMessage(chat_id, "Game still lacks another player.")
            else:
                filename = match.print_board(chat_id)
                turn_id = match.get_turn_id()
                bot.sendPhoto(chat_id, open(filename, "rb")) #, caption = "@{} ({}) to move.".format(match.get_name(turn_id), match.get_color(turn_id)))
        elif tokens[0] == "حرکت" or tokens[0] == "/move" or tokens[0] == "/move@TeleChessRobot" or (match and match.parse_move(tokens[0])): # !move <SAN move>
            if match == None:
                bot.sendMessage(chat_id, text[3][self.lang(chat_id)])
            elif not self.is_in_game(players, sender_id):
                bot.sendMessage(chat_id, "You are not involved in the chess match.")
            elif match.get_turn_id() != sender_id:
                bot.sendMessage(chat_id, "It's not your turn.")
            else:
                had_offer = False
                if match.drawoffer != None:
                    had_offer = True
                move = tokens[0] if match.parse_move(tokens[0]) else ''.join(tokens[1:])
                res = match.make_move(move)
                if res == "Invalid":
                    bot.sendMessage(chat_id, text[11][self.lang(chat_id)].format(move), parse_mode = "Markdown")
                else:
                    if had_offer:
                        bot.sendMessage(chat_id, 'Draw offer cancelled.')
                    filename = match.print_board(chat_id)
                    if res == "Checkmate":
                        bot.sendMessage(chat_id, text[12][self.lang(chat_id)])
                        self.game_end(chat_id, players, match.get_color(sender_id))
                    elif res == "Stalemate":
                        bot.sendMessage(chat_id, text[13][self.lang(chat_id)])
                        self.game_end(chat_id, players, "Draw")
                    else:
                        # AI move codes
                        ai_move = match.ai_move()
                        bot.sendMessage(chat_id, ai_move)

                        res = match.make_move(ai_move)
                        
                        filename = match.print_board(chat_id)
                        if res == "Checkmate":
                            bot.sendMessage(chat_id, text[12][self.lang(chat_id)])
                            self.game_end(chat_id, players, match.get_color(sender_id))
                        elif res == "Stalemate":
                            bot.sendMessage(chat_id, text[13][self.lang(chat_id)])
                            self.game_end(chat_id, players, "Draw")
                        elif res == "Check":
                            bot.sendMessage(chat_id, text[14][self.lang(chat_id)])
                        else:
                            turn_id = match.get_turn_id()

        elif tokens[0] == "/offerdraw" or tokens[0] == "/offerdraw@TeleChessRobot": # Offer a draw
            if match == None:
                bot.sendMessage(chat_id, "There is no chess match going on.")
            elif not self.is_in_game(players, sender_id):
                bot.sendMessage(chat_id, "You are not involved in the chess match.")
            elif match.get_turn_id() != sender_id:
                bot.sendMessage(chat_id, "It's not your turn.")
            else:
                match.offer_draw(sender_id)
                bot.sendMessage(chat_id, "{} ({}) offers a draw.".format(sender_username, match.get_color(sender_id)))
        elif tokens[0] == "/rejectdraw" or tokens[0] == "/rejectdraw@TeleChessRobot": # Reject draw offer
            if match == None:
                bot.sendMessage(chat_id, "There is no chess match going on.")
            elif not self.is_in_game(players, sender_id):
                bot.sendMessage(chat_id, "You are not involved in the chess match.")
            elif match.drawoffer == match.get_opp_id(sender_id):
                match.reject_draw()
                bot.sendMessage(chat_id, 'Draw offer cancelled by {} ({}).'.format(sender_username, match.get_color(sender_id)))
            else:
                bot.sendMessage(chat_id, "There is no draw offer to reject.")
        elif tokens[0] == "/claimdraw" or tokens[0] == "/claimdraw@TeleChessRobot": # Either due to offer or repeated moves
            if match == None:
                bot.sendMessage(chat_id, "There is no chess matches going on.")
            elif not self.is_in_game(players, sender_id):
                bot.sendMessage(chat_id, "You are not involved in the chess match.")
            elif match.get_turn_id() != sender_id:
                bot.sendMessage(chat_id, "It's not your turn.")
            elif match.board.can_claim_draw() or match.drawoffer == match.get_opp_id(sender_id):
                self.game_end(chat_id, players, "Draw")
            else:
                bot.sendMessage(chat_id, "Current match situation does not warrant a draw.")
        elif tokens[0] == "لغو" or tokens[0] == "/resign" or tokens[0] == "/resign@TeleChessRobot":
            if match == None:
                bot.sendMessage(chat_id, text[3][self.lang(chat_id)])
            elif not self.is_in_game(players, sender_id):
                bot.sendMessage(chat_id, "You are not involved in the chess match.")
            else:
                bot.sendMessage(chat_id, text[15][self.lang(chat_id)].format(sender_username, match.get_color(sender_id)), parse_mode='Markdown')
                self.game_end(chat_id, players, match.get_opp_color(sender_id))
        elif tokens[0] == "آمار" or tokens[0] == "/stats" or tokens[0] == "/stats@TeleChessRobot":
            if sender_id not in self.statslog:
                bot.sendMessage(chat_id, text[16][self.lang(chat_id)])
            else:
                pstats = self.statslog[sender_id]
                bot.sendMessage(chat_id, text[17][self.lang(chat_id)].format(sender_username, pstats[0], pstats[1], pstats[2]))

    def on_callback_query(self, msg):
        '''Handle callback queries for choosing color'''
        self.msglog.append(msg)
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        sender_id, sender_username = self.get_sender_details(msg)
        print(msg, sender_id, sender_username)

        print('Callback Query:', query_id, chat_id, query_data)

        bot.answerCallbackQuery(query_id, text='Got it')

        match = self.gamelog[chat_id] if chat_id in self.gamelog.keys() else None
        players = match.get_players() if match != None else None

        if query_data in ['fa', 'en']:
            self.init_stats(sender_id, query_data)
            
        elif query_data in ['white', 'black']:
            if match != None:
                bot.sendMessage(chat_id, text[9][self.lang(chat_id)])
            else:
                color = query_data
                self.create_game(chat_id, sender_id, sender_username, color)

    def on_inline_query(self, msg):
        '''Handles online queries by dynamically checking if it matches any keywords in the bank'''
        self.msglog.append(msg)
        print(msg)

        query_id, from_id, query_string = telepot.glance(msg, flavor = "inline_query")
        def compute_answer():
            bank = [{"type": "article", "id": "/start", "title": "/start", "description": "Starts the bot in this chat", "message_text": "/start"},
                    {"type": "article", "id": "/help", "title": "/help", "description": "Displays help sheet for @TeleChessRobot", "message_text": "/help"},
                    {"type": "article", "id": "/stats", "title": "/stats", "description": "Displays your match statistics with @TeleChessRobot", "message_text": "/stats"}]
            ans = [opt for opt in bank if query_string in opt["id"]]
            for opt in bank:
                print(query_string, opt["id"], query_string in opt["id"])
            return ans

        self._answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        '''Just logs the message. Does nothing for now'''
        self.msglog.append(msg)
        print(msg)

############
# AUTO RUN #
############
telegram_bot_token = "7034924272:AAFX4c25CQwjdgJrTDRnWar37S_7NnVsqhU"
bot = tgchessBot(telegram_bot_token)

# For persistence
if not os.path.exists("gamelog.txt"):
    with open("gamelog.txt", "wb") as f:
        pickle.dump({}, f)
if not os.path.exists("msglog.txt"):
    with open("msglog.txt", "wb") as f:
        pickle.dump([], f)
if not os.path.exists("statslog.txt"):
    with open("statslog.txt", "wb") as f:
        pickle.dump({}, f)
bot.load_state()
print("Previous state loaded.")

# For server log
print("Bot is online: ", bot.getMe())
bot.message_loop()
print("Listening...")

# Keep the program running.
while 1:
    time.sleep(10)
    bot.save_state() # Save state periodically
