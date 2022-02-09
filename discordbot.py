import asyncio
import logging
import os
import re
import traceback
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
from discord import Member
from discord.channel import DMChannel
from discord.commands import Option, permissions
from discord.ext import commands
from discord.ext.ui import MessageProvider, ViewTracker
from newdispanderfixed import dispand

import Components.member_button as membership_button
from Cogs.connect import connect
from Cogs.post_sheet import PostToSheet as sheet
from Cogs.inquiry import InquiryView, SuggestionView
from Genshin.portal import PortalView

logging.basicConfig(level=logging.INFO)

"""bot招待リンク
https://discord.com/api/oauth2/authorize?client_id=916956842440151070&permissions=1403113958646&scope=bot%20applications.commands


イベントハンドラ一覧(client)
async def の後を変えるだけで実行されるイベンドが変わる
メッセージ受信時に実行：   on_message(message)
Bot起動時に実行：      on_ready(message)
リアクション追加時に実行:  on_reaction_add(reaction, user)
新規メンバー参加時に実行： on_member_join(member)
ボイスチャンネル出入に実行： on_voice_state_update(member, before, after)"""

conn = connect()
utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

# onlinetoken@heroku
token = os.environ["DISCORD_BOT_TOKEN"]

# help-command-localize-test


class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "その他のコマンド"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return "各コマンドの説明: //help <コマンド名>\n"


intents = discord.Intents.all()
"""
bot = commands.Bot(command_prefix='//', intents=intents,
                   help_command=JapaneseHelpCommand())
                   """

INIT_EXTENSION_LIST = [
    "Cogs.concept",
    "Cogs.error",
    "Cogs.entrance",
    "Cogs.inquiry",
    "Cogs.member_count",
    "Cogs.ng_word",
    "Cogs.pin",
    "Cogs.poll",
    "Cogs.slow",
    "Cogs.starboard",
    "Cogs.stream",
    # "Cogs.talk_api",
    "Cogs.thread",
    "Cogs.tool",
]

GENSHIN_EXTENSION_LIST = ["Genshin.portal"]


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="//", intents=intents, help_command=JapaneseHelpCommand()
        )
        self.persistent_views_added = False
        for cog in INIT_EXTENSION_LIST:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
            else:
                print(f"extension [{cog}] is loaded!")
        for cog in GENSHIN_EXTENSION_LIST:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
            else:
                print(f"extension for Genshin [{cog}] is loaded!")

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(MemberVerifyButton())
            self.add_view(PortalView())
            self.add_view(InquiryView())
            self.add_view(SuggestionView())
            self.persistent_views_added = True
            print("Set Persistant Views!")
        print("------------------------------------------------")
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------------------------------------------------")
        channel = self.get_channel(log_channel)
        now = discord.utils.utcnow()
        await channel.send(
            f"起動完了({now.astimezone(jst):%m/%d-%H:%M:%S})\nBot ID:{self.user.id}"
        )
        return


bot = MyBot()


# ID-guild
guild_id = int(os.environ["GUILD_ID"])

# ID-role
everyone = int(os.environ["GUILD_ID"])
server_member_role = int(os.environ["SERVER_MEMBER_ROLE"])
mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
yt_membership_role = int(os.environ["YT_MEMBER_ROLE"])
stop_role = int(os.environ["STOP_ROLE"])
vc_stop_role = int(os.environ["VC_STOP_ROLE"])

# ID-channel
alert_channel = int(os.environ["ALERT_CHANNEL"])
stream_channel = int(os.environ["STREAM_CHANNEL"])
star_channel = int(os.environ["STAR_CHANNEL"])
dm_box_channel = int(os.environ["DM_BOX_CHANNEL"])
alert_channel = int(os.environ["ALERT_CHANNEL"])
member_check_channel = int(os.environ["MEMBER_CHECK_CHANNEL"])

# ID-log
thread_log_channel = int(os.environ["THREAD_LOG_CHANNEL"])
join_log_channel = int(os.environ["JOIN_LOG_CHANNEL"])
log_channel = int(os.environ["LOG_CHANNEL"])
vc_log_channel = int(os.environ["VC_LOG_CHANNEL"])
error_log_channel = int(os.environ["ERROR_CHANNEL"])

# Id-vc
count_vc = int(os.environ["COUNT_VC"])


# emoji
accept_emoji = "\N{Heavy Large Circle}"
reject_emoji = "\N{Cross Mark}"


# pattern
# yyyy/mm/dd
date_pattern = re.compile(r"^\d{4}/\d{2}/\d{2}")

# discord's invite url
discord_pattern = re.compile(r"discord.gg/[\w]*")

# list
stop_list = [stop_role, vc_stop_role]

# other
env = os.environ["ENV"]  # main or alpha


# Dispander-All


@bot.listen("on_message")
async def on_message_dispand(message):
    avoid_word_list_prefix = ["//send-message", "//edit-message", "//send-dm"]
    if type(message.channel) == DMChannel:
        return
    else:
        for word in avoid_word_list_prefix:
            if message.content.startswith(word):
                return
        if message.content.endswith("中止に必要な承認人数: 1"):
            return
        else:
            await dispand(message)
            return


"""
デフォルトで提供されている on_message をオーバーライドすると、コマンドが実行されなくなります。
これを修正するには on_message の最後に bot.process_commands(message) を追加してみてください。
https://discordbot.jp/blog/17/
"""

# VC入退室ログ


@bot.listen()
async def on_voice_state_update(member, before, after):
    if member.guild.id == guild_id and (before.channel != after.channel):
        channel = bot.get_channel(vc_log_channel)
        now = discord.utils.utcnow().astimezone(jst)
        if before.channel is None:
            message = f"{now:%m/%d %H:%M:%S} : {member.mention} が {after.channel.mention} に参加しました。"
            await channel.send(message)
            return
        elif after.channel is None:
            message = f"{now:%m/%d %H:%M:%S} : {member.mention} が {before.channel.mention} から退出しました。"
            await channel.send(message)
            return
        else:
            message = f"{now:%m/%d %H:%M:%S} : {member.mention} が {before.channel.mention} から {after.channel.mention} に移動しました。"
            await channel.send(message)
            return


# hello?


@bot.command()
@commands.has_role(mod_role)
async def test(ctx):
    """生存確認用"""
    await ctx.send("hello")
    return


@bot.slash_command(name="user", guild_ids=[guild_id], default_permission=False)
@permissions.has_role(mod_role)
async def _newuser(
    ctx,
    member: Option(Member, "対象のIDや名前を入力してください。"),
):
    """ユーザー情報を取得できます。"""
    # guild = ctx.guild
    # member = guild.get_member(int(id))
    # この先表示する用
    await ctx.defer()
    member_created: datetime = member.created_at.astimezone(jst)
    created = member_created.strftime("%Y/%m/%d %H:%M:%S")
    member_joined: datetime = member.joined_at.astimezone(jst)
    joined = member_joined.strftime("%Y/%m/%d %H:%M:%S")
    desc = (
        f"対象ユーザー:{member.mention}\nユーザー名:{member}\nID:`{member.id}`\nBot:{member.bot}"
    )
    roles = sorted(
        [role for role in member.roles], key=lambda role: role.position, reverse=True
    )
    send_roles = "\n".join([role.mention for role in roles])
    avatars = [member.avatar, member.display_avatar]
    if member.default_avatar in avatars:
        avatar_url = member.default_avatar.url
    else:
        avatar_url = member.display_avatar.replace(size=1024, static_format="webp").url
    desc = desc + f"\n[Avatar url]({avatar_url})"
    deal = []
    if member.communication_disabled_until:
        until_jst: datetime = member.communication_disabled_until.astimezone(jst)
        until = until_jst.strftime("%Y/%m/%d %H:%M:%S")
        deal.append(f"Timeout: {until} に解除")
    stops = "\n".join([role.name for role in member.roles if role.id in stop_list])
    if stops:
        deal.append(stops)
    if not deal:
        send_deal = "なし"
    else:
        send_deal = "\n".join(deal)
    embed = discord.Embed(
        title="ユーザー情報照会結果",
        description=desc,
        color=3983615,
    )
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(
        name="アカウント作成日時",
        value=created,
    )
    embed.add_field(
        name="サーバー参加日時",
        value=joined,
    )
    embed.add_field(name=f"所持ロール({len(roles)})", value=send_roles, inline=False)
    embed.add_field(
        name="実行中措置",
        value=send_deal,
    )
    await ctx.respond(embed=embed)
    return


@bot.command(name="user")
@commands.has_role(mod_role)
async def _new_user(ctx, member: Member):
    """ユーザー情報を取得できます。"""
    guild = ctx.guild
    member = guild.get_member(member)
    # この先表示する用
    avatar_url = member.display_avatar.replace(size=1024, static_format="webp").url
    if member.avatar is None:
        avatar_url = "DefaultAvatar"
    member_reg_date = member.created_at.astimezone(jst)
    # NickNameあるか？
    if member.display_name == member.name:
        member_nickname = "None"
    else:
        member_nickname = member.display_name
    member_join_date = member.joined_at.astimezone(jst)
    # membermention = member.mention
    roles = [[x.name, x.id] for x in member.roles]
    # [[name,id],[name,id]...]
    x = ["/ID: ".join(str(y) for y in x) for x in roles]
    z = "\n".join(x)
    # Message成形-途中
    user_info_msg = f"```ユーザー名:{member} (ID:{member.id})\nBot?:{member.bot}\nAvatar url:{avatar_url}\nニックネーム:{member_nickname}\nアカウント作成日時:{member_reg_date:%Y/%m/%d %H:%M:%S}\n参加日時:{member_join_date:%Y/%m/%d %H:%M:%S}\n\n所持ロール:\n{z}```"
    await ctx.reply(user_info_msg, mention_author=False)
    return


# ping-test


@bot.slash_command(guild_ids=[guild_id], name="ping")
@permissions.has_role(admin_role)
async def _ping(ctx):
    """生存確認用"""
    raw_ping = bot.latency
    ping = round(raw_ping * 1000)
    await ctx.respond(f"Pong!\nPing is {ping}ms")
    return


# receive-dm


@bot.listen("on_message")
async def on_message_dm(message):
    avoid_dm_list = ["//check", "//remove-member"]
    if type(message.channel) == DMChannel and bot.user == message.channel.me:
        if message.author.bot:
            return
        else:
            for word in avoid_dm_list:
                if message.content.startswith(word):
                    return
            channel = bot.get_channel(dm_box_channel)
            embeds = []
            if message.content or message.attachments:
                embed = await compose_embed_dm_box(message)
                embeds.append(embed)
                for attachment in message.attachments[1:]:
                    embed = discord.Embed(
                        color=3447003,
                    )
                    embed.set_image(url=attachment.proxy_url)
                    embeds.append(embed)
            for embed in message.embeds:
                embeds.append(embed)
            await channel.send(embeds=embeds)
            return
    else:
        return


# send-message


@bot.command(name="send-message")
@commands.has_role(admin_role)
async def _messagesend(ctx, channel_id: int, *, arg):
    """メッセージ送信用"""
    # channel:送信先
    channel = bot.get_channel(channel_id)
    # role:承認可能ロール
    role = ctx.guild.get_role(admin_role)
    confirm_msg = f"【メッセージ送信確認】\n以下のメッセージを{channel.mention}へ送信します。"
    exe_msg = f"{channel.mention}にメッセージを送信しました。"
    non_exe_msg = f"{channel.mention}へのメッセージ送信をキャンセルしました。"
    confirm_arg = f"\n{arg}\n------------------------"
    result = await confirm(ctx, confirm_arg, role, confirm_msg)
    if result:
        msg = exe_msg
        message = await channel.send(arg)
        desc_url = message.jump_url
        await ctx.send("Sended!")
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        msg = non_exe_msg
        desc_url = ""
        await ctx.send("Cancelled!")
        await send_exe_log(ctx, msg, desc_url)
        return


# send-dm


@bot.command(name="send-dm")
@commands.has_role(admin_role)
async def _send_dm(ctx, user: Member, *, arg):
    """DM送信用"""
    role = ctx.guild.get_role(admin_role)
    confirm_msg = f"【DM送信確認】\n以下のDMを{user.mention}へ送信します。"
    exe_msg = f"{user.mention}にDMを送信しました。"
    non_exe_msg = f"{user.mention}へのDM送信をキャンセルしました。"
    confirm_arg = f"\n{arg}\n------------------------"
    result = await confirm(ctx, confirm_arg, role, confirm_msg)
    if result:
        msg = exe_msg
        message = await user.send(arg)
        desc_url = message.jump_url
        await ctx.send("Sended!")
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        msg = non_exe_msg
        desc_url = ""
        await ctx.send("Cancelled!")
        await send_exe_log(ctx, msg, desc_url)
        return


# edit-message


@bot.command(name="edit-message")
@commands.has_role(admin_role)
async def _editmessage(ctx, channel_id: int, message_id: int, *, arg):
    """メッセージ編集用"""
    channel = bot.get_channel(channel_id)
    role = ctx.guild.get_role(admin_role)
    target = await channel.fetch_message(message_id)
    msg_url = f"https://discord.com/channels/{ctx.guild.id}/{channel_id}/{message_id}"
    confirm_msg = f"【メッセージ編集確認】\n{channel.mention}のメッセージ\n{msg_url}\nを以下のように編集します。"
    exe_msg = f"{channel.mention}のメッセージを編集しました。"
    non_exe_msg = f"{channel.mention}のメッセージの編集をキャンセルしました。"
    confirm_arg = f"\n{arg}\n------------------------"
    result = await confirm(ctx, confirm_arg, role, confirm_msg)
    if result:
        msg = exe_msg
        await target.edit(content=arg)
        desc_url = msg_url
        await ctx.send("Edited!")
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        msg = non_exe_msg
        desc_url = ""
        await ctx.send("Cancelled!")
        await send_exe_log(ctx, msg, desc_url)
        return


# deal-member
# deal:対処。ban/kickなど
deal = None
# add_dm:デフォルトDMに追加で送信するコンテンツ
add_dm = None

# timeout-member


@bot.user_command(guild_ids=[guild_id], name="緊急タイムアウト")
@permissions.has_role(mod_role)
# user commands return the member
async def _emergency_timeout(ctx, member: Member):
    await member.timeout_for(duration=timedelta(days=1), reason="Emergency Timeout")
    await ctx.respond(f"{member.mention}を緊急タイムアウトしました。", ephemeral=True)
    msg = f"{member.mention}を緊急タイムアウトしました。"
    desc_url = ""
    until = discord.utils.utcnow().astimezone(jst) + timedelta(days=1)
    until_str = until.strftime("%Y/%m/%d %H:%M:%S")
    await send_context_timeout_log(ctx, msg, desc_url, until_str)
    return


@bot.command(name="timeout")
@commands.has_role(mod_role)
async def _timeout(ctx, member: Member, input_until: str, if_dm: str = "dm:true"):
    """メンバーをタイムアウト"""
    until = datetime.strptime(input_until, "%Y%m%d")
    until_jst = until.replace(tzinfo=jst)
    role = ctx.guild.get_role(mod_role)
    valid_if_dm_list = ["dm:true", "dm:false"]
    until_str = until_jst.strftime("%Y/%m/%d/%H:%M")
    if if_dm not in valid_if_dm_list:
        await ctx.reply(
            content="不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはFalseを指定してください。",
            mention_author=False,
        )
        msg = "不明な引数を検知したため処理を終了しました。"
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        deal = "timeout"
        add_dm = f"あなたは{until_str}までサーバーでの発言とボイスチャットへの接続を制限されます。"
        DM_content = await make_deal_dm(ctx, deal, add_dm)
        if if_dm == "dm:false":
            DM_content = ""
        else:
            pass
        confirm_msg = f"【timeout実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\n期限:{until_str}\nDM送信:{if_dm}\nDM内容:{DM_content}"
        exe_msg = f"{member.mention}をタイムアウトしました。"
        non_exe_msg = f"{member.mention}のタイムアウトをキャンセルしました。"
        confirm_arg = ""
        result = await confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            if if_dm == "dm:true":
                sent_dm = await member.send(DM_content)
                desc_url = sent_dm.jump_url
                await member.timeout(until_jst.astimezone(utc), reason=None)
                await ctx.send("timeouted!")
                await send_timeout_log(ctx, msg, desc_url, until_str)
                return
            elif if_dm == "dm:false":
                desc_url = ""
                await member.timeout(until_jst.astimezone(utc), reason=None)
                await ctx.send("timeouted!")
                await send_timeout_log(ctx, msg, desc_url, until_str)
                return
            else:
                return
        else:
            msg = non_exe_msg
            desc_url = ""
            await send_exe_log(ctx, msg, desc_url)
            await ctx.send("Cancelled!")
            return


# untimeout-member


@bot.command(name="untimeout")
@commands.has_role(admin_role)
async def _untimeout(ctx, member: Member):
    """メンバーのタイムアウトを解除"""
    role = ctx.guild.get_role(admin_role)
    confirm_msg = f"【untimeout実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})"
    exe_msg = f"{member.mention}のタイムアウトを解除しました。"
    non_exe_msg = f"{member.mention}のタイムアウトの解除をキャンセルしました。"
    confirm_arg = ""
    result = await confirm(ctx, confirm_arg, role, confirm_msg)
    if result:
        msg = exe_msg
        desc_url = ""
        await member.remove_timeout(reason=None)
        await ctx.send("untimeouted!")
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        msg = non_exe_msg
        desc_url = ""
        await ctx.send("Cancelled!")
        await send_exe_log(ctx, msg, desc_url)
        return


@bot.listen("on_member_update")
async def _on_member_untimeout(before: Member, after: Member):
    if before.timed_out and not after.timed_out:
        channel = bot.get_channel(log_channel)
        embed = discord.Embed(
            title="Timeout 解除通知",
            color=3447003,
            description=f"{after.mention}のタイムアウトが終了しました。",
            timestamp=discord.utils.utcnow(),
        )
        await channel.send(embed=embed)
        return


# kick-member


@bot.command(name="kick")
@commands.has_role(admin_role)
async def _kick_user(ctx, member: Member, if_dm: str = "dm:true"):
    """メンバーをキック"""
    role = ctx.guild.get_role(admin_role)
    valid_if_dm_list = ["dm:true", "dm:false"]
    if if_dm not in valid_if_dm_list:
        await ctx.reply(
            content="不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはdm:falseを指定してください。",
            mention_author=False,
        )
        msg = "不明な引数を検知したため処理を終了しました。"
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        deal = "kick"
        add_dm = ""
        DM_content = await make_deal_dm(ctx, deal, add_dm)
        if if_dm == "dm:false":
            DM_content = ""
        else:
            pass
        confirm_msg = f"【kick実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\nDM送信:{if_dm}\nDM内容:{DM_content}"
        exe_msg = f"{member.mention}をキックしました。"
        non_exe_msg = f"{member.mention}のキックをキャンセルしました。"
        confirm_arg = ""
        result = await confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            if if_dm == "dm:true":
                sent_dm = await member.send(DM_content)
                desc_url = sent_dm.jump_url
                await member.kick(reason=None)
                await ctx.send("kicked!")
                await send_exe_log(ctx, msg, desc_url)
                return
            elif if_dm == "dm:false":
                desc_url = ""
                await member.kick(reason=None)
                await ctx.send("kicked!")
                await send_exe_log(ctx, msg, desc_url)
                return
            else:
                return
        else:
            msg = non_exe_msg
            desc_url = ""
            await send_exe_log(ctx, msg, desc_url)
            await ctx.send("Cancelled!")
            return


# ban-member


@bot.command(name="ban")
@commands.has_role(admin_role)
async def _ban_user(ctx, member: Member, if_dm: str = "dm:true"):
    """メンバーをBAN"""
    role = ctx.guild.get_role(admin_role)
    valid_if_dm_list = ["dm:true", "dm:false"]
    if if_dm not in valid_if_dm_list:
        await ctx.reply(
            content="不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはdm:falseを指定してください。",
            mention_author=False,
        )
        msg = "不明な引数を検知したため処理を終了しました。"
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        deal = "BAN"
        add_dm = """
今後、あなたはクロヱ水族館に参加することはできません。

BANの解除を希望する場合は以下のフォームをご利用ください。
クロヱ水族館BAN解除申請フォーム
https://forms.gle/mR1foEyd9JHbhYdCA
"""
        DM_content = await make_deal_dm(ctx, deal, add_dm)
        if if_dm == "dm:false":
            DM_content = ""
        else:
            pass
        confirm_msg = f"【BAN実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\nDM送信:{if_dm}\nDM内容:{DM_content}"
        exe_msg = f"{member.mention}をBANしました。"
        non_exe_msg = f"{member.mention}のBANをキャンセルしました。"
        confirm_arg = ""
        result = await confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            if if_dm == "dm:true":
                sent_dm = await member.send(DM_content)
                desc_url = sent_dm.jump_url
                await member.ban(reason=None)
                await ctx.send("baned!")
                await send_exe_log(ctx, msg, desc_url)
                return
            elif if_dm == "dm:false":
                desc_url = ""
                await member.ban(reason=None)
                await ctx.send("baned!")
                await send_exe_log(ctx, msg, desc_url)
                return
            else:
                return
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
            await send_exe_log(ctx, msg, desc_url)
            return


# Unban-member


@bot.command(name="unban")
@commands.has_role(admin_role)
async def _unban_user(ctx, id: int):
    """ユーザーのBANを解除"""
    user = await bot.fetch_user(id)
    role = ctx.guild.get_role(admin_role)
    target = [user for entry in await ctx.guild.bans() if entry.user.id == user.id]
    if not target:
        await ctx.reply("BANリストにないユーザーを指定したため処理を停止します。", mention_author=False)
        msg = "BANリストにないユーザーを指定したため処理を停止しました。"
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        confirm_msg = f"【Unban実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{user}(ID:{user.id})"
        exe_msg = f"{user.mention}のBANを解除しました。"
        non_exe_msg = f"{user.mention}のBANの解除をキャンセルしました。"
        confirm_arg = ""
        result = await confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            desc_url = ""
            await ctx.guild.unban(user)
            await ctx.send("Unbaned!")
            await send_exe_log(ctx, msg, desc_url)
            return
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
            await send_exe_log(ctx, msg, desc_url)
            return


# check-member


@bot.command(name="check")
@commands.dm_only()
async def _check_member(ctx):
    """メンバーシップ認証用"""
    if ctx.message.attachments == []:
        await ctx.reply(content="画像が添付されていません。画像を添付して送り直してください。", mention_author=False)
        msg = "メンバー認証コマンドに画像が添付されていなかったため処理を停止しました。"
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        await ctx.reply(content="認証要求を受理しました。\nしばらくお待ちください。", mention_author=False)
        channel = bot.get_channel(member_check_channel)
        guild = bot.get_guild(guild_id)
        exe_msg = f"{ctx.message.author.mention}のメンバーシップ認証を承認しました。"
        non_exe_msg = f"{ctx.message.author.mention}のメンバーシップ認証を否認しました。"
        future = asyncio.Future()
        view = membership_button.MemberConfView(ctx, future)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(MessageProvider(channel))
        await future
        if future.done():
            if future.result():
                btn_msg = tracker.message
                msg = exe_msg
                desc_url = tracker.message.jump_url
                member = guild.get_member(ctx.message.author.id)
                ref_msg = await btn_msg.reply(
                    f"{ctx.message.author.display_name}さんの次回支払日を返信してください。"
                )

                def check(message):
                    return (
                        bool(date_pattern.fullmatch(message.content))
                        and message.author != bot.user
                        and message.reference
                        and message.reference.message_id == ref_msg.id
                    )

                date = await bot.wait_for("message", check=check)
                status: Optional[str] = await sheet(member, date.content).check_status()
                if status is None:
                    await date.reply("シートに反映されました。", mention_author=False)
                    add_role = guild.get_role(yt_membership_role)
                    await member.add_roles(add_role)
                    await ctx.reply(
                        content="メンバーシップ認証を承認しました。\nメンバー限定チャンネルをご利用いただけます!",
                        mention_author=False,
                    )
                    log_channel_object = bot.get_channel(log_channel)
                    embed = discord.Embed(
                        title="実行ログ",
                        color=3447003,
                        description=msg,
                        url=f"{desc_url}",
                        timestamp=discord.utils.utcnow(),
                    )
                    embed.set_author(
                        name=bot.user, icon_url=bot.user.display_avatar.url
                    )
                    embed.add_field(
                        name="実行日時",
                        value=f"{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}",
                    )
                    await log_channel_object.send(embed=embed)
                    return
                else:
                    await date.reply(
                        "予期せぬエラーによりシートに反映できませんでした。\nロールの付与は行われませんでした。",
                        mention_author=False,
                    )
                    channel = bot.get_channel(error_log_channel)
                    channel.send(status)
            else:
                msg = non_exe_msg
                desc_url = tracker.message.jump_url
                get_reason = await tracker.message.reply(
                    content=f"DMで送信する{ctx.author.display_name}さんの不承認理由を返信してください。",
                    mention_author=False,
                )

                def check(message):
                    return (
                        message.content
                        and message.author != bot.user
                        and message.reference
                        and message.reference.message_id == get_reason.id
                    )

                message = await bot.wait_for("message", check=check)
                reply_msg = f"メンバーシップ認証を承認できませんでした。\n理由:\n　{message.content}"
                await ctx.reply(content=reply_msg, mention_author=False)
                await message.reply("否認理由を送信しました。", mention_author=False)
                log_channel_object = bot.get_channel(log_channel)
                embed = discord.Embed(
                    title="実行ログ",
                    color=3447003,
                    description=msg,
                    url=f"{desc_url}",
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_author(name=bot.user, icon_url=bot.user.display_avatar.url)
                embed.add_field(
                    name="実行日時",
                    value=f"{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}",
                )
                await log_channel_object.send(embed=embed)
                return


class MemberVerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="認証を始める",
        style=discord.ButtonStyle.gray,
        emoji="\N{Envelope with Downwards Arrow Above}",
        custom_id="start_membership_verify_button",
    )
    async def _start_verify(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        res_image_name = "receive_dm.png"
        self_path = os.path.dirname(__file__)
        path = self_path + r"/images/receive_dm.png"
        res_image = discord.File(fp=path, filename=res_image_name, spoiler=False)

        embed = discord.Embed(
            title="認証を開始します。",
            description="BotからのDMを確認してください。",
            color=15767485,
        )
        embed.add_field(
            name="BotからDMが届かない場合は？",
            value="サーバー設定の\n「プライバシー設定」から、\n「サーバーにいるメンバーからのダイレクトメッセージを許可する」\nをONにしてください。",
        )
        embed.set_image(url=f"attachment://{res_image_name}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                embed=embed, file=res_image, ephemeral=True
            )
        else:
            await interaction.followup.send(embed=embed, file=res_image, ephemeral=True)
        # Send DM
        DM_embed, dm_image = _compose_dm_embeds()
        try:
            await interaction.user.send(embed=DM_embed, file=dm_image)
        except discord.Forbidden as e:
            hook_image = discord.File(fp=path, spoiler=False)
            print("Error at start membership verify: ", e)
            await interaction.followup.send(
                content="DMの送信に失敗しました。\nDMが受信できない設定に\nなっている可能性があります。\n\nサーバー設定の\n「プライバシー設定」から、\n「サーバーにいるメンバーからのダイレクトメッセージを許可する」\nをONにしてください。",
                file=hook_image,
                ephemeral=True,
            )
        return


def _compose_dm_embeds() -> tuple[discord.Embed, discord.File]:
    image_name = "auth_1.png"
    self_path = os.path.dirname(__file__)
    path = self_path + r"/images/auth_1.png"
    image = discord.File(fp=path, filename=image_name, spoiler=False)
    embed = discord.Embed(
        title="メンバーシップ認証", description="以下の手順に従って\n認証を開始してください。", color=15767485
    )
    embed.add_field(
        inline=False,
        name="手順1",
        value="Discordアカウントの画像と、\n[こちら](https://www.youtube.com/paid_memberships)から確認できる\n__**次回支払日が確認できる画像**__\n(例:下の画像)を準備する。",
    )
    embed.add_field(
        inline=False,
        name="手順2",
        value="このDMに、\n__手順1で準備した画像を__\n__全て添付して__、\n`//check`と送信する。",
    )
    embed.add_field(
        inline=False,
        name="手順3",
        value="Botから\n```認証要求を受理しました。\nしばらくお待ちください。```\nと返信があれば完了です。\n管理者の対応をお待ちください。",
    )
    embed.add_field(
        name="Botから完了の返信が来ない場合は？",
        value="コマンドが間違っている\n(正しいコマンドは`//check`)、\n画像を添付していないなどの\n可能性があります。\n\n全て正しいのに解決しない場合は、\nこのDMにその旨を書いて\n送信してください。",
    )
    embed.set_image(url=f"attachment://{image_name}")
    return embed, image


@bot.command(name="send_verify_button")
@commands.has_role(admin_role)
async def _send_verify_button(ctx: commands.Context):
    embed = discord.Embed(
        title="Youtubeメンバーシップ認証",
        description="\N{Envelope with Downwards Arrow Above}を押すと認証が始まります。",
        color=15767485,
    )
    await ctx.send(embed=embed, view=MemberVerifyButton())
    return


# remove-member


@bot.command(name="remove-member")
@commands.dm_only()
async def _remove_member(ctx):
    """メンバーシップ継続停止時"""
    await ctx.reply(content="メンバーシップ継続停止を受理しました。\nしばらくお待ちください。", mention_author=False)
    channel = bot.get_channel(member_check_channel)
    guild = bot.get_guild(guild_id)
    exe_msg = f"{ctx.message.author.mention}のメンバーシップ継続停止を反映しました。"
    future = asyncio.Future()
    view = membership_button.MemberRemoveView(future, ctx)
    tracker = ViewTracker(view, timeout=None)
    await tracker.track(MessageProvider(channel))
    await future
    if future.done():
        if future.result():
            msg = exe_msg
            desc_url = tracker.message.jump_url
            member = guild.get_member(ctx.message.author.id)
            membership_role_object = guild.get_role(yt_membership_role)
            await member.remove_roles(membership_role_object)
            await ctx.reply(
                content="メンバーシップ継続停止を反映しました。\nメンバーシップに再度登録された際は`//check`で再登録してください。",
                mention_author=False,
            )
            log_channel_object = bot.get_channel(log_channel)
            embed = discord.Embed(
                title="実行ログ",
                color=3447003,
                description=msg,
                url=f"{desc_url}",
                timestamp=discord.utils.utcnow(),
            )
            embed.set_author(name=bot.user, icon_url=bot.user.display_avatar.url)
            embed.add_field(
                name="実行日時",
                value=f"{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}",
            )
            await log_channel_object.send(embed=embed)
            return


# member-update-dm


@bot.command(name="update-member")
@commands.has_role(admin_role)
async def _update_member(ctx, *update_member: Member):
    """メンバーシップ更新案内"""
    role = ctx.guild.get_role(admin_role)
    update_member_mention = [x.mention for x in update_member]
    update_member_str = "\n".join(update_member_mention)
    confirm_msg = f"【DM送信確認】\nメンバーシップ更新DMを\n{update_member_str}\nへ送信します。"
    exe_msg = f"{update_member_str}にメンバーシップ更新DMを送信しました。"
    non_exe_msg = f"{update_member_str}へのメンバーシップ更新DM送信をキャンセルしました。"
    DM_content = "【メンバーシップ更新のご案内】\n沙花叉のメンバーシップの更新時期が近づいた方にDMを送信させていただいております。\nお支払いが完了して次回支払日が更新され次第、以前と同じように\n`//check`\nで再認証を行ってください。\n\nメンバーシップを継続しない場合は\n`//remove-member`\nと送信してください。(__**メンバー限定チャンネルの閲覧ができなくなります。**__)"
    confirm_arg = f"\n{DM_content}\n------------------------"
    turned = await confirm(ctx, confirm_arg, role, confirm_msg)
    if turned:
        for x in update_member:
            await x.send(DM_content)
        await ctx.send("Sended!")
        msg = exe_msg
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        return
    elif turned is False:
        msg = non_exe_msg
        desc_url = ""
        await send_exe_log(ctx, msg, desc_url)
        await ctx.send("Cancelled!")
        return
    else:
        return


# Deal-DM


async def make_deal_dm(ctx, deal, add_dm):
    DM_content = f"""【あなたは{deal}されました】
クロヱ水族館/Chloeriumの管理者です。

あなたのサーバーでの行為がサーバールールに違反していると判断し、{deal}しました。
{add_dm}"""
    return DM_content


# confirm-system


async def confirm(ctx, confirm_arg, role, confirm_msg) -> bool:
    send_confirm_msg = f"{confirm_msg}\n------------------------{confirm_arg}\nコマンド承認:{role.mention}\n実行に必要な承認人数: 1\n中止に必要な承認人数: 1"
    message = await ctx.send(send_confirm_msg)
    await message.add_reaction(accept_emoji)
    await message.add_reaction(reject_emoji)
    valid_reactions = [accept_emoji, reject_emoji]
    # wait-for-reaction

    def check_confirm(payload):
        return (
            role in payload.member.roles
            and str(payload.emoji) in valid_reactions
            and payload.message_id == message.id
        )

    payload = await bot.wait_for("raw_reaction_add", check=check_confirm)
    # exe
    if str(payload.emoji) == accept_emoji:
        return True
    else:
        return False


# create_log_send_embed_base


async def create_base_log_embed(ctx, msg, desc_url):
    embed = discord.Embed(
        title="実行ログ",
        color=3447003,
        description=msg,
        url=f"{desc_url}",
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="実行者", value=f"{ctx.author.mention}")
    embed.add_field(name="実行コマンド", value=f"[コマンドリンク]({ctx.message.jump_url})")
    embed.add_field(
        name="実行日時", value=f"{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}"
    )
    return embed.copy()


# send-exe-log


async def send_exe_log(ctx, msg, desc_url):
    embed = await create_base_log_embed(ctx, msg, desc_url)
    channel = bot.get_channel(log_channel)
    await channel.send(embed=embed)
    return


# send-timeout-log


async def send_timeout_log(ctx, msg, desc_url, until_str):
    embed = await create_base_log_embed(ctx, msg, desc_url)
    channel = bot.get_channel(log_channel)
    embed.insert_field_at(2, name="解除日時", value=f"{until_str}")
    await channel.send(embed=embed)
    return


# context-embed
async def create_base_context_log_embed(ctx, msg, desc_url):
    embed = discord.Embed(
        title="Context Menu 実行ログ",
        color=3447003,
        description=msg,
        url=f"{desc_url}",
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="実行者", value=f"{ctx.author.mention}")
    embed.add_field(
        name="実行日時", value=f"{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}"
    )
    return embed.copy()


# send-context-log


async def send_context_log(ctx, msg, desc_url):
    embed = await create_base_context_log_embed(ctx, msg, desc_url)
    channel = bot.get_channel(log_channel)
    await channel.send(embed=embed)
    return


# send-context-tiemout-log


async def send_context_timeout_log(ctx, msg, desc_url, until_str):
    embed = await create_base_context_log_embed(ctx, msg, desc_url)
    channel = bot.get_channel(log_channel)
    embed.insert_field_at(2, name="解除日時", value=f"{until_str}")
    await channel.send(embed=embed)
    return


# compose-embed


async def compose_embed_dm_box(message):
    embed = discord.Embed(
        title="DMを受信しました。",
        url=message.jump_url,
        color=3447003,
        description=message.content,
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url,
    )
    embed.add_field(name="送信者", value=f"{message.author.mention}")
    embed.add_field(
        name="受信日時", value=f"{message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}"
    )
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(url=message.attachments[0].proxy_url)
    return embed


# YoutubeAPI
API_KEY = os.environ["GOOGLE_API_KEY"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


# create-event-slash


@bot.command(name="private")
async def _private(ctx):
    role = ctx.guild.get_role(server_member_role)
    channels = sorted(
        [channel for channel in ctx.guild.channels if channel.category],
        key=lambda channel: channel.position,
    )
    for channel in channels:
        result = channel.permissions_for(role).view_channel
        print(channel.name, result)
    return


# create a user command for the supplied guilds
# @bot.user_command(guild_ids=[guild_id])
# async def mention(ctx, member: Member):  # user commands return the member
#     await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")

if __name__ == "__main__":
    bot.run(token)
