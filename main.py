import asyncio
import json
import random

import gspread_asyncio
from aiohttp import ClientWebSocketResponse
from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadWorksheet as Worksheet
from mipac.models.notification import NotificationNote
from mipa.ext import commands


class Config:
    def __init__(self, path: str) -> None:
        file = open(path)
        raw = json.load(file)
        self.token = raw.get("token")
        self.origin = raw.get("origin")
        self.credentials = raw.get("credentialsJSONFile")
        self.max = raw.get("duplicateQueueAfter")
        self.rate = raw.get("rate")
        self.start_time = raw.get("startFrom")
        self.visibility = raw.get("visibility")
        self.worksheet = raw.get("worksheet")
        template = raw.get("template")
        self.note = template.get("auto")
        self.reply = template.get("mention")
        if any([
            self.token is None,
            self.origin is None,
            self.credentials is None,
            self.worksheet is None,
            self.note is None,
            self.reply is None
        ]):
            raise ValueError("config.json 파일에 일부 필수 값이 누락되었습니다.")

    def get_creds(self):
        creds = Credentials.from_service_account_file(self.credentials)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped


class Line:
    def __init__(self, data: dict) -> None:
        self.location = data["row"] + 2
        self.text = data["text"]
        self.where = data["where"]
        self.number = data["number"]
    
    @classmethod
    async def from_number(cls: "Line", row: int, sheet: Worksheet) -> "Line":
        res = await sheet.get(f"D{row}")
        text = res[0][0].strip()
        res = await sheet.get(f"C{row}")
        where = res[0][0].strip()
        res = await sheet.get(f"B{row}")
        number = res[0][0].strip()
        data = {"row": row, "number": number, "where": where, "text": text}
        return cls(data)


class Autoposter(commands.Bot):
    def __init__(self):
        super().__init__()
        self.config: Config = Config("./config.json")
        self.agcm = gspread_asyncio.AsyncioGspreadClientManager(self.config.get_creds)

    async def get_worksheet(self) -> Worksheet:
        client = await self.agcm.authorize()
        spreadsheet = await client.open_by_url(self.config.worksheet)
        worksheet = await spreadsheet.get_worksheet(0)
        return worksheet

    async def get_random_line(self) -> Line:
        sheet: Worksheet = await self.get_worksheet()
        response = await sheet.get("F4")
        if response is None or response == "":
            return
        count = int(response[0][0])
        result = random.randint(1, count)
        number = result + 2
        return await Line.from_number(number, sheet)
    
    async def get_line(self, number: int) -> Line:
        sheet: Worksheet = await self.get_worksheet()
        return await Line.from_number(number, sheet)

    async def _connect_channel(self) -> None:
        await self.router.connect_channel(['main', 'global'])

    async def on_ready(self, ws: ClientWebSocketResponse) -> None:
        print(f"Connected as @{self.user.username}@{self.config.origin}")
        await self._connect_channel()
        extensions = [
            "exts.post"
        ]
        for extension in extensions:
            await self.load_extension(extension)

    async def on_reconnect(self, ws: ClientWebSocketResponse) -> None:
        print("Disconnected from server. Reconnecting...")
        await self._connect_channel()
    
    async def on_mention(self, notice: NotificationNote) -> None:
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
