import discord


class QuizView(discord.ui.View):
    video_id: str
    base_message: str
    
    def __init__(self, video_id: str, base_message: str):
        self.video_id = video_id
        self.base_message = base_message
        super().__init__()
        
        self.add_item(discord.ui.Button(label="Go listen it !", style=discord.ButtonStyle.link, url="https://fytecas.github.io/liszt-bot/?id=" + video_id))
    
    @discord.ui.button(label="Think I got it", style=discord.ButtonStyle.primary, row=1)
    async def got_it(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("**Here is the original message:**\n"+ self.base_message, ephemeral=True)