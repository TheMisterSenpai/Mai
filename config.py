from dotenv import load_dotenv

from pathlib import Path
import os 

#загрузка .env
load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path = env_path)


#bot_setting
BOT_PREFIX = 'm'

#API
TOKEN = os.getenv['TOKEN']
MONGO = os.getenv['MONGO']
YOUTUBE_API = os.getenv['YTAPI']

#ID
BOT_ID = '802987390033330227'

#color
BANLISTNOT = 0x008000
BANLISTYES = 0xff0000
INFO = 0xffc0cb

#status
ID_GUILD = os.getenv['GUILD']
KEY = os.getenv['KEY']

#bug
BUG_ID = os.getenv['GUILDBUG']
BUGKEY = os.getenv['KEYBUG']