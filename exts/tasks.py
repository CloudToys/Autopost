import random

from gspread.worksheet import Worksheet
from mipa.ext import commands, tasks
from mipa.ext.commands.bot import Bot
# from mipa.ext.commands.context import Context


class Autopost(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.posted = []
    
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

    @tasks.loop(seconds=1800)
    async def _postLine(self) -> None:
        line = self.get_line()
        while line in self.posted:
            line = self.get_line()
        await self.bot.client.note.action.send(content=line, visibility="home")
        self.posted.append(line)
        if len(self.posted) > self.bot.max_count:
            self.posted.pop(0)


async def setup(bot: Bot):
    cog = Autopost(bot)
    await cog._postLine.start()
    await bot.add_cog(cog)