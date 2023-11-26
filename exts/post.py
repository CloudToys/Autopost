import asyncio
from datetime import datetime

from mipa.ext import commands, tasks
from mipa.ext.commands.bot import Bot


class Post(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.max_count = bot.config.max or 3
        self.visibility = bot.config.visibility or "home"
        self.posted = []

    @tasks.loop(seconds=1800)
    async def _postLine(self) -> None:
        line = self.bot.get_random_line()
        while line.text in self.posted:
            line = self.bot.get_random_line()
        template = self.bot.config.note
        result = template.replace("{text}", line.text).replace("{from}", line.where).replace("{number}", line.number)
        await self.bot.client.note.action.send(content=result, visibility=self.visibility)
        self.posted.append(line)
        if len(self.posted) > self.max_count:
            self.posted.pop(0)


async def setup(bot: Bot):
    cog = Post(bot)
    await bot.add_cog(cog)
    if bot.config.rate is not None:
        cog._postLine.seconds = bot.config.rate * 60
    if bot.config.start_time is not None:
        print("Waiting until time is coming")
        now = datetime.now()
        while now.minute != bot.config.start_time:
            await asyncio.sleep(1)
            now = datetime.now()
        await cog._postLine.start()
