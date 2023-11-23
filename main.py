import asyncio
import os
#from typing import Optional

#import aiomysql
import gspread
from aiohttp import ClientWebSocketResponse
from gspread.worksheet import Worksheet
#from mipac.models.notification import NotificationNote
from mipa.ext import commands
# from mipac.models.note import Note
from dotenv import load_dotenv

load_dotenv()

COGS = [
    "exts.tasks"
]

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__()
        self.max_count = int(os.getenv("MAX_COUNT"))

#    async def create_pool(self) -> None:
#        pool = await aiomysql.create_pool(
#            minsize=5,
#            maxsize=20,
#            host=os.getenv("MYSQL_HOST"),
#            port=int(os.getenv("MYSQL_PORT")),
#            user=os.getenv("MYSQL_USER"),
#            password=os.getenv("MYSQL_PASSWORD"),
#            db="autopost",
#            autocommit=True
#        )
#        self.pool = pool
    
#    async def query(self, query: str, fetch: bool = False) -> Optional[dict]:
#        async with self.pool.acquire() as conn:
#            async with conn.cursor(aiomysql.DictCursor) as cur:
#                await cur.execute(query)
#                if fetch:
#                    return await cur.fetchall()
#                else:
#                    return "Query Successful"

    def get_worksheet(self) -> Worksheet:
        gc = gspread.service_account()
        sh = gc.open_by_url(os.getenv("SPREADSHEET_URL"))
        worksheet = sh.get_worksheet(0)
        return worksheet

    def get_line(self) -> str:
        def get_line(self) -> str:
        sheet: Worksheet = self.bot.get_worksheet()
        response = sheet.get("F4")
        if response is None or response == "":
            return
        count = int(response[0][0])
        result = random.randint(1, count)
        number = result + 2
        res = sheet.get(f"D{number}")
        text = res[0][0].strip()
        return text

    async def _connect_channel(self):
        await self.router.connect_channel(['main', 'global'])

    async def on_ready(self, ws: ClientWebSocketResponse):
        print(f'connected: {self.user.username}')
        await self._connect_channel()
        for cog in COGS:
            await self.load_extension(cog)

    async def on_reconnect(self, ws: ClientWebSocketResponse):
        print('Disconnected from server. Will try to reconnect.')
        await self._connect_channel()
    
#    async def on_note(self, note: Note):
#        print(f'{note.author.username}: {note.content}')
    
    async def on_mention(self, notice: NotificationNote):
        print(f"{notice.note.author.username} requested {notice.note.content}")
        await note.action.reply()


if __name__ == '__main__':
    bot = MyBot()
    loop = asyncio.get_event_loop()
#    loop.run_until_complete(bot.create_pool())
    loop.run_until_complete(bot.start(os.getenv("MISSKEY_ORIGIN"), os.getenv("MISSKEY_TOKEN")))
