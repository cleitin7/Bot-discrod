import discord
from discord import app_commands
from discord.ext import commands
import os

# Configurações
TOKEN = "MTM2MDAxMzMyOTM3MjAyNTEzNA.GKk5_8.lArHWMMj1_ztCwDQ8wGnzpW42bDqK-37jdxMIQ"
GUILD_ID = 1198358681130111148 # ID do servidor
CARGO_VERIFICADO_ID = 1199831805432430673
CARGO_STAFF_ID = 1198827127001317396

# Bot e Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Verificação View
class VerificacaoView(discord.ui.View):
    @discord.ui.button(label="Verificar", style=discord.ButtonStyle.success)
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(CARGO_VERIFICADO_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Você foi verificado com sucesso!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erro ao atribuir cargo.", ephemeral=True)

# Embed View com interatividade
class EmbedBuilder(discord.ui.Modal, title="Criador de Embed"):
    titulo = discord.ui.TextInput(label="Título", placeholder="Digite o título do embed", required=True)
    descricao = discord.ui.TextInput(label="Descrição", style=discord.TextStyle.paragraph, required=True)
    cor = discord.ui.TextInput(label="Cor (hex)", placeholder="#ff0000", required=False)
    imagem = discord.ui.TextInput(label="URL da imagem (opcional)", placeholder="https://exemplo.com/imagem.png", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cor_embed = int(self.cor.value.replace("#", ""), 16) if self.cor.value else 0x3498db
        except:
            cor_embed = 0x3498db

        embed = discord.Embed(title=self.titulo.value, description=self.descricao.value, color=cor_embed)
        if self.imagem.value:
            embed.set_image(url=self.imagem.value)

        await interaction.response.send_message(embed=embed)

# Comando de Embed
@bot.tree.command(name="embed", description="Cria um embed personalizado com menu")
async def embed(interaction: discord.Interaction):
    await interaction.response.send_modal(EmbedBuilder())

# Verificação Comando
@bot.tree.command(name="verificar", description="Envia painel de verificação")
async def verificar(interaction: discord.Interaction):
    embed = discord.Embed(title="Verificação", description="Clique no botão abaixo para se verificar.", color=discord.Color.green())
    view = VerificacaoView()
    await interaction.response.send_message(embed=embed, view=view)  # Agora visível para todos

# Ticket View
class TicketView(discord.ui.View):
    def __init__(self, cargo_id, canal_id):
        super().__init__()
        self.cargo_id = cargo_id
        self.canal_id = canal_id

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.primary)
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        cargo = interaction.guild.get_role(self.cargo_id)
        canal = interaction.guild.get_channel(self.canal_id)
        if canal:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                cargo: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            ticket_channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
            await ticket_channel.send(f"{interaction.user.mention}, sua solicitação foi aberta!")
            await interaction.response.send_message(f"🎫 Ticket criado em {ticket_channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Canal de ticket inválido.", ephemeral=True)

# Ticket Comando
@bot.tree.command(name="ticket", description="Envia painel de abertura de ticket")
@app_commands.describe(cargo_id="ID do cargo responsável", canal_id="ID do canal onde os tickets devem ser criados")
async def ticket(interaction: discord.Interaction, cargo_id: int, canal_id: int):
    view = TicketView(cargo_id, canal_id)
    embed = discord.Embed(title="Central de Atendimento", description="Clique abaixo para abrir um ticket.", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Evento de prontidão
@bot.event
async def on_ready():
    print(f"🤖 Bot logado como {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

bot.run(TOKEN)
