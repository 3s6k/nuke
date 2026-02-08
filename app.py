import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import os
from collections import defaultdict
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- ヘルスチェック用ダミーサーバー ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_health_check_server():
    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()
# -----------------------------------

JST = timezone(timedelta(hours=9))
intents = discord.Intents.default()
intents.moderation = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
target_channel_id = None
# BANとキックの合計回数を保持
action_history = defaultdict(list)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="c")
async def set_channel(ctx, channel: discord.TextChannel):
    global target_channel_id
    target_channel_id = channel.id
    await ctx.send(f"通知先を {channel.mention} に設定しました。")

# 処罰（キック）を実行する共通関数
async def punish_moderator(guild, moderator):
    now = datetime.now(timezone.utc)
    # 24時間以内の履歴をフィルタリング
    action_history[moderator.id] = [t for t in action_history[moderator.id] if now - t < timedelta(hours=24)]
    action_history[moderator.id].append(now)

    if len(action_history[moderator.id]) >= 3:
        try:
            await moderator.kick(reason="24時間以内に合計3回以上のBAN/キックを実行したため")
            
            if target_channel_id:
                channel = guild.get_channel(target_channel_id)
                if channel:
                    jst_now = datetime.now(JST).strftime('%Y/%m/%d/%H/%M/%S')
                    embed = discord.Embed(
                        description=f"{moderator.mention} を荒らしの疑いでキック処分にしました\n-# {jst_now}",
                        color=0xff0000
                    )
                    await channel.send(embed=embed)
            action_history[moderator.id] = []
        except Exception as e:
            print(f"Error during punishment: {e}")

# BANを検知
@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if not entry.user.bot:
            await punish_moderator(guild, entry.user)

# キックを検知 (メンバーがサーバーを離れた時に監査ログを確認)
@bot.event
async def on_member_remove(member):
    guild = member.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
        # ターゲットがこのメンバーで、かつ直近の操作であれば
        if entry.target.id == member.id and not entry.user.bot:
            await punish_moderator(guild, entry.user)
            break

bot.run(os.getenv("DISCORD_TOKEN"))
