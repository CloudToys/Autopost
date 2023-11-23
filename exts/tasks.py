from datetime import datetime

from mipa.ext import commands, tasks
from mipa.ext.commands.bot import Bot
# from mipa.ext.commands.context import Context


class Autopost(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.posted = []

    @tasks.loop(seconds=60)
    async def _postLine(self) -> None:
        now = datetime.now()
        if now.minute not in [30, 00]:
            return
        
        line = self.bot.get_line()
        while line in self.posted:
            line = self.bot.get_line()
        await self.bot.client.note.action.send(content=line, visibility="home")
        self.posted.append(line)
        if len(self.posted) > self.bot.max_count:
            self.posted.pop(0)


async def setup(bot: Bot):
    cog = Autopost(bot)
    await cog._postLine.start()
    await bot.add_cog(cog)
