from datetime import datetime

from mipa.ext import commands, tasks
from mipa.ext.commands.bot import Bot


class Post(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.max_count = bot.config.max or 3
        self.visibility = bot.config.visibility or "home"
        self.rate = bot.config.rate or 30
        self.minute = bot.config.start_time or 0

    @tasks.loop(seconds=60)
    async def _postLine(self) -> None:
        if datetime.now().minute != self.minute:
            return

        self.minute = self.minute + self.rate
        if self.minute >= 60:
            self.minute = self.minute - 60

        line = await self.bot.get_random_line()
        template = self.bot.config.note
        result = template.replace("{text}", line.text).replace("{from}", line.where).replace("{number}", line.number)
        await self.bot.client.note.action.send(content=result, visibility=self.visibility)


async def setup(bot: Bot):
    cog = Post(bot)
    await bot.add_cog(cog)
    await cog._postLine.start()
