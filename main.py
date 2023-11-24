import asyncio
import json
import random

import gspread
from aiohttp import ClientWebSocketResponse
from gspread.worksheet import Worksheet
from mipac.models.notification import NotificationNote
from mipa.ext import commands


class Config:
    def __init__(self, path: str) -> None:
        file = open(path)
        raw = json.load(file)
        self.token = raw.get("token")
        self.origin = raw.get("origin")
        self.max = raw.get("max_duplicate")
        self.rate = raw.get("rate")
        self.visibility = raw.get("visibility")
        self.worksheet = raw.get("worksheet")
        template = raw.get("template")
        self.note = template.get("auto")
        self.reply = template.get("mention")
        if any([
            self.token is None,
            self.origin is None,
            self.worksheet is None,
            self.note is None,
            self.reply is None
        ]):
            raise ValueError("config.json 파일에 일부 필수 값이 누락되었습니다.")


class Line:
    def __init__(self, row: int, bot: "Autoposter") -> None:
        sheet = bot.get_worksheet()
        self.location = row
        res = sheet.get(f"D{row}")
        self.text = res[0][0].strip()
        res = sheet.get(f"C{row}")
        self.where = res[0][0].strip()
        res = sheet.get(f"B{row}")
        self.number = res[0][0].strip()


class Autoposter(commands.Bot):
    def __init__(self):
        super().__init__()
        self.config: Config = Config("./config.json")

    def get_worksheet(self) -> Worksheet:
        gc = gspread.service_account()
        sh = gc.open_by_url(self.config.worksheet)
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
        return Line(number, self)
    
    def get_line(self, number: int) -> str:
        return Line(number, self)

    async def _connect_channel(self):
        await self.router.connect_channel(['main', 'global'])

    async def on_ready(self, ws: ClientWebSocketResponse):
        print(f"Connected as @{self.user.username}@{self.config.origin}")
        await self._connect_channel()
        extensions = [
            "exts.post"
        ]
        for extension in extensions:
            await self.load_extension(extension)

    async def on_reconnect(self, ws: ClientWebSocketResponse):
        print("Disconnected from server. Reconnecting...")
        await self._connect_channel()
    
    async def on_mention(self, notice: NotificationNote):
        if notice.note.reply_id is not None:
            return

        line: Line = self.get_random_line()
        template = self.config.reply
        result = template.replace("{text}", line.text).replace("{from}", line.where).replace("{number}", line.number)
        await notice.note.api.action.reply(content=result, visibility=notice.note.visibility, reply_id=notice.note.id)


if __name__ == '__main__':
    bot = Autoposter()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.start(f"wss://{bot.config.origin}/streaming", bot.config.token))
