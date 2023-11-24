import asyncio
import os
import random

import gspread
from aiohttp import ClientWebSocketResponse
from gspread.worksheet import Worksheet
from mipac.models.notification import NotificationNote
from mipa.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Autoposter(commands.Bot):
    def __init__(self):
        super().__init__()
        self.max_count = int(os.getenv("MAX_DUPLICATE_COUNT"))

    def get_worksheet(self) -> Worksheet:
        gc = gspread.service_account()
        sh = gc.open_by_url(os.getenv("SPREADSHEET_URL"))
        worksheet = sh.get_worksheet(0)
        return worksheet

    def get_random_line(self) -> str:
        sheet: Worksheet = self.get_worksheet()
        response = sheet.get("F4")
        if response is None or response == "":
            return
        count = int(response[0][0])
        result = random.randint(1, count)
        number = result + 2
        res = sheet.get(f"D{number}")
        text = res[0][0].strip()
        return text
    
    def get_info(self, line: str) -> dict:
        sheet = self.get_worksheet()
        result = sheet.find(line, in_column=4)
        number = result.row - 2
        where = sheet.get(f"C{result.row}")
        where = where[0][0]
        return {"number": number, "from": where}

    async def _connect_channel(self):
        await self.router.connect_channel(['main', 'global'])

    async def on_ready(self, ws: ClientWebSocketResponse):
        print(f"Connected as @{self.user.username}@{self.user.host}")
        await self._connect_channel()
        extensions = [
            "exts.post"
        ]
        for extension in extensions:
            await self.load_extension(extension)

    async def on_reconnect(self, ws: ClientWebSocketResponse):
        print("Disconnected from server.")
        await self._connect_channel()
    
    async def on_mention(self, notice: NotificationNote):
        line = self.get_random_line()
        info = self.get_info(line)
        await notice.note.api.action.reply(content=f"{line}\n \n<small>- {info['from']}에서 발췌됨. ({info['number']}번 대사)</small>", reply_id=notice.note.id)


if __name__ == '__main__':
    bot = Autoposter()
    loop = asyncio.get_event_loop()
    origin = os.getenv("MISSKEY_ORIGIN")
    loop.run_until_complete(bot.start(f"wss://{origin}/streaming", os.getenv("MISSKEY_TOKEN")))
