import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import os
from collections import defaultdict

# 日本時間 (JST)
JST = timezone(timedelta(hours=9))

intents = discord.Intents.default()
intents.moderation = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# グローバル変数で通知チャンネルとBAN履歴を保持
target_channel_id = None
ban_history = defaultdict(list)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # UptimeRobotなどの死活監視用メッセージ
    print("Bot is running and monitored by UptimeRobot.")

# 通知チャンネルを設定するコマンド: /c #チャンネル
@bot.command(name="c")
async def set_channel(ctx, channel: discord.TextChannel):
    global target_channel_id
    target_channel_id = channel.id
    await ctx.send(f"通知先を {channel.mention} に設定しました。")

@bot.event
async def on_member_ban(guild, user):
    now = datetime.now(timezone.utc)
    
    # 監査ログから直近のBAN実行者を取得
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        moderator = entry.user
        if moderator.bot: return

        # 24時間以内のBAN回数をカウント
        ban_history[moderator.id] = [t for t in ban_history[moderator.id] if now - t < timedelta(hours=24)]
        ban_history[moderator.id].append(now)

        # 3回目を超えたらキック
        if len(ban_history[moderator.id]) >= 3:
            try:
                # 荒らしの疑いでキック
                await moderator.kick(reason="24時間以内に3回以上のBANを実行したため")
                
                # 指定されたチャンネルへ通知
                if target_channel_id:
                    channel = guild.get_channel(target_channel_id)
                    if channel:
                        jst_now = datetime.now(JST).strftime('%Y/%m/%d/%H/%M/%S')
                        embed = discord.Embed(
                            description=f"{moderator.mention} を荒らしの疑いでキック処分にしました\n-# {jst_now}",
                            color=0xff0000 # 赤色
                        )
                        await channel.send(embed=embed)

                # カウントリセット
                ban_history[moderator.id] = []
                
            except discord.Forbidden:
                print(f"Error: {moderator.name} をキックする権限がBotにありません。")
            except Exception as e:
                print(f"Error: {e}")

# Koyebの環境変数 DISCORD_TOKEN を使用
bot.run(os.getenv("DISCORD_TOKEN"))
