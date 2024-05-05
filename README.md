# About
@TeleChessRobot is a Telegram bot. You can play chess using @TeleChessRobot. To play with friends, create a group and invite @TeleChessRobot into it. If you wish to play alone, talk to @TeleChessRobot on a 1-on-1 private message.

# Hosting @TeleChessRobot on your own server

* Register a bot with the [BotFather](https://telegram.me/botfather)
* After installing `Python3` and `pip` on a server, perform the following:

```
sudo pip3 install telepot
sudo pip3 install python-chess
sudo pip3 install Pillow
sudo pip3 install cairosvg
```

* Install `stockfish` chess engine on your linux console using the following command:
```
sudo apt-get install stockfish
```

* Download the code from my [Github repo](https://github.com/mahdavifar2002/TeleChessRobot)
* Replace the `telegram_bot_token` variable (near the bottom of `TeleChessRobot.py`) with your own bot token from BotFather
* Shoot up a `screen` and run `python3 TeleChessRobot.py`. Detach using `Ctrl + A + D`. The bot will continue running and handle messages in the background as long as your server is up.

# Blog post
To learn more, read the blog post here: http://davinchoo.com/project/tgchess/

# Acknowledgements
This bot is built with the help of [`TeleChessRobot`](https://github.com/cxjdavin/TeleChessRobot), [`telepot`](https://github.com/nickoala/telepot), [`python-chess`](https://github.com/niklasf/python-chess) and [`Pillow`](https://pillow.readthedocs.io/en/3.2.x/), with chess piece images from [Cburnett](https://en.wikipedia.org/wiki/User:Cburnett) on [Wikipedia](https://en.wikipedia.org/wiki/Chess_piece).

Many thanks to [`vesatoivonen`](https://github.com/vesatoivonen) for useful suggestions and bug fixes.
