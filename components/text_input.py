import discord
from discord import ui
from discord.ext import commands


class TextInputTracker:
    def __init__(self) -> None:
        pass

    async def track_modal(
        self,
        *,
        ctx: commands.Context,
        title: str,
        custom_id: str,
        min_length: int,
        max_length: int,
        timeout: float | None = None,
    ) -> str | None:
        view = MessageInputView(
            timeout=timeout,
            title=title,
            custom_id=custom_id,
            min_length=min_length,
            max_length=max_length,
        )
        await ctx.send(view=view)
        await view.wait()
        if not view.value:
            return None
        return view.value


class MessageInputView(ui.View):
    def __init__(
        self,
        *,
        timeout: float | None = None,
        title: str,
        custom_id: str,
        min_length: int,
        max_length: int,
    ):
        super().__init__(timeout=timeout)
        self.title = title
        self.custom_id = custom_id
        self.min = min_length
        self.max = max_length
        self.value = None

    @ui.button(
        label="入力",
        custom_id="message_input_button",
        style=discord.ButtonStyle.blurple,
        emoji="\N{Pencil}",
        row=0,
    )
    async def input_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = MessageInput(
            title=self.title,
            custom_id=self.custom_id,
            min_length=self.min,
            max_length=self.max,
        )
        if interaction.message:
            view = to_unavailable(self)
            await interaction.message.edit(view=view)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.content
        self.stop()


def to_unavailable(view: ui.View) -> ui.View:
    new_view = discord.ui.View(timeout=view.timeout)
    for c in view.children:
        if isinstance(c, ui.Button):
            _c = FollowupButton(
                style=c.style,
                label=c.label,
                disabled=False,
                custom_id="unavailable_" + c.custom_id if c.custom_id else None,
                url=c.url,
                emoji=c.emoji,
                row=c.row,
            )
            new_view.add_item(_c)
        elif isinstance(c, ui.Select):
            c.disabled = True
            new_view.add_item(c)
        else:
            new_view.add_item(c)
    return new_view


class FollowupButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        content = "このボタンは既に使用されています。\nもう一度はじめからコマンドを実行してください。"
        if interaction.response.is_done():
            await interaction.followup.send(content=content, ephemeral=True)
        else:
            await interaction.response.send_message(content=content, ephemeral=True)
        return


class MessageInput(ui.Modal):
    def __init__(
        self,
        *,
        title: str = ...,
        timeout: float | None = None,
        custom_id: str,
        min_length: int,
        max_length: int,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self._content = ui.TextInput(
            label="入力フォーム",
            style=discord.TextStyle.paragraph,
            placeholder="メッセージを入力",
            min_length=min_length,
            max_length=max_length,
        )
        self.add_item(self._content)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.content = self._content.value
        self.interaction = interaction
        self.stop()
        return
