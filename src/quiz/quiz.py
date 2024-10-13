import discord
from discord.ext import commands
from discord.commands import Option
from src.quiz.quiz_view import QuizView
from src.random_message import get_random_url_in_messages, get_random_right_channel


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Quizz")
    async def quizz(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.channel.TextChannel,
            "The channel to get the quizz from",
            required=False,
            default="*",
        ),  # type: ignore
        channel_category: Option(
            discord.channel.CategoryChannel,
            "The category of the channel to get the quizz from",
            required=False,
            default="*",
        ),  # type: ignore
        public: Option(
            bool, "If the quizz is public or not", required=False, default=True
        ),  # type: ignore
    ):
        if channel == "*":
            if channel_category == "*":
                text_channels = ctx.guild.text_channels
            else:
                text_channels = [
                    channel
                    for channel in ctx.guild.text_channels
                    if channel.category == channel_category
                ]
            channel = get_random_right_channel(text_channels, ctx)
        else:
            # Check if the bot has permission to read messages in the channel
            if not channel.permissions_for(ctx.guild.me).read_message_history:
                await ctx.respond(
                    "I don't have permission to read messages in the channel."
                )
                return
        if channel is None:
            await ctx.respond(
                "I don't have permission to read messages in any of the channels."
            )
            return
        messages = await channel.history(limit=200).flatten()
        id, content = get_random_url_in_messages(messages, self.bot.user)
        if id is None:
            await ctx.respond(
                "I couldn't find any URLs in the messages. channel: " + channel.mention,
                ephemeral=True,
            )
        else:
            await ctx.respond(
                "**Here is some random music** (it is recommended to use an ad-blocker)",
                view=QuizView(id, content),
                ephemeral=not public,
            )


def setup(bot):
    bot.add_cog(Quiz(bot))
