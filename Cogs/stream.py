from curses.ascii import ETB
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from discord import ApplicationContext

import discord
from discord.commands import permissions, slash_command
from discord.ext import commands
from discord.ui import InputText, Modal

mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
guild_id = int(os.environ["GUILD_ID"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")
utc = timezone.utc

stream_channel_mods = int(os.environ["STREAM_MOD"])


class StreamRegister(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], default_permission=False, name="stream")
    @permissions.has_role(mod_role)
    async def _test_modal(self, ctx: ApplicationContext):
        """配信を簡単にイベントに登録できます。"""
        modal = StreamModal()
        await ctx.interaction.response.send_modal(modal)
        return

    @commands.Cog.listener("on_message")
    async def _add_stream_button(self, message: discord.Message):
        if (
            not message.webhook_id
            or not self.bot.user
            or message.author.id == self.bot.user.id
        ):
            return
        if not message.embeds or isinstance(
            message.embeds[0].description, discord.embeds._EmptyEmbed
        ):
            return
        if (
            message.channel.id == stream_channel_mods
            and message.embeds[0].description
            and "待機所が作成されました" in message.embeds[0].description
        ):
            if isinstance(message.embeds[0].url, discord.embeds._EmptyEmbed):
                return
            if message.embeds[0].url:
                view = StreamView(_url=message.embeds[0].url)
            else:
                view = StreamView()
            await message.reply(content="登録はこちら", view=view)
            return


class StreamButton(discord.ui.Button):
    def __init__(self, _url: Optional[str] = None, **kwargs):
        super().__init__(
            label="配信登録",
            style=discord.ButtonStyle.success,
            custom_id="stream_register",
            **kwargs,
        )
        self._url = _url

    async def callback(self, interaction: discord.Interaction):
        # msg = await interaction.original_message()
        await interaction.response.send_modal(
            StreamModal(_url=self._url, origin_msg=interaction.message)
        )
        return


class StreamView(discord.ui.View):
    def __init__(self, _url: Optional[str] = None):
        super().__init__(timeout=None)
        if _url:
            self.add_item(StreamButton(_url=_url))
        else:
            self.add_item(StreamButton())


class StreamModal(Modal):
    def __init__(
        self, _url: Optional[str] = None, origin_msg: discord.Message | None = None
    ) -> None:
        super().__init__(title="配信登録用フォーム")
        self.origin_msg = origin_msg
        self.add_item(
            InputText(label="配信のトピック", placeholder="歌枠、雑談、など", row=0, required=True)
        )
        if _url:
            self.add_item(
                InputText(
                    label="配信のURL(メン限など掲載できない場合は空欄)",
                    placeholder="https://youtu.be/LyakqutKBpM",
                    row=1,
                    required=False,
                    value=_url,
                )
            )
        else:
            self.add_item(
                InputText(
                    label="配信のURL(メン限など掲載できない場合は空欄)",
                    placeholder="https://youtu.be/LyakqutKBpM",
                    row=1,
                    required=False,
                )
            )
        self.add_item(
            InputText(
                label="配信開始時刻",
                placeholder="2100(当日) or 2022.05.18.2100(日付指定)",
                row=2,
                required=True,
                min_length=4,
                max_length=15,
            )
        )
        self.add_item(
            InputText(
                label="予想配信時間(単位:時間)", placeholder="1.5(1時間30分)", row=3, required=True
            )
        )

    async def callback(self, interaction: discord.Interaction):
        # print(interaction.guild.id)
        event_name = self.children[0].value
        event_url = self.children[1].value
        if not event_url:
            event_url = "非公開"
        time = self.children[2].value
        if len(time) == 4:
            todate = datetime.now(timezone.utc).astimezone(jst)
            start_time_object = datetime.strptime(time, "%H%M")
            true_start_jst = start_time_object.replace(
                year=todate.year, month=todate.month, day=todate.day, tzinfo=jst
            )
        elif len(time) == 15:
            true_start = datetime.strptime(time, "%Y.%m.%d.%H%M")
            true_start_jst = true_start.replace(tzinfo=jst)
        else:
            await interaction.response.send_message(
                content="正しい時間を入力してください。\n有効な時間は\n```2022.05.18.2100(2022年5月18日21:00)もしくは\n2100(入力した日の21:00)です。```",
                ephemeral=True,
            )
            return
        true_duration = timedelta(hours=float(self.children[3].value))
        true_end = true_start_jst + true_duration
        # print(type(event_name), type(true_start_jst), type(true_end), type(event_url))
        if not interaction.guild or interaction.user:
            return
        await interaction.guild.create_scheduled_event(
            name=event_name,
            start_time=true_start_jst.astimezone(utc),
            end_time=true_end,
            location=event_url,
        )
        await interaction.response.send_message(content="配信を登録しました。")
        if self.origin_msg:
            await self.origin_msg.edit(
                content=f"登録済み\n登録してくれた人:{interaction.user.name}", view=None
            )
        return


def setup(bot):
    return bot.add_cog(StreamRegister(bot))
