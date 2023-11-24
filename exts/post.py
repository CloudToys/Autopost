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
        now = datetime.now()
        if now.minute not in [30, 00]: # Only post in n:30 and n:00
            return
        
        line = self.bot.get_random_line()
        while line in self.posted:
            line = self.bot.get_random_line()
        template = self.bot.config.reply
        result = template.replace("{text}", line.text).replace("{from}", line.where).replace("{number}", line.number)
        await self.bot.client.note.action.send(content=result, visibility=self.visibility)
        self.posted.append(line)
        if len(self.posted) > self.max_count:
            self.posted.pop(0)


async def setup(bot: Bot):
    cog = Post(bot)
    if bot.config.rate is not None:
        cog._postLine.seconds = bot.config.rate * 60
    await cog._postLine.start()
    await bot.add_cog(cog)
