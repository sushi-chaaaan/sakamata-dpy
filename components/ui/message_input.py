import discord
from discord import Embed, Interaction, ui
from discord.ext.ui.button import Button
from discord.ext.ui.message import Message
from discord.ext.ui.modal import Modal
from discord.ext.ui.state import state
from discord.ext.ui.view import View

from model.color import Color


class MessageInputView(View):
    content: str = state("content")  # type: ignore
    disable_all: bool = state("disable_all")  # type: ignore
    inputted_once: bool = state("inputted_once")  # type: ignore

    def __init__(
        self,
        target: discord.User
        | discord.Member
        | discord.abc.GuildChannel
        | discord.Thread,
        title: str,
        attachment: discord.Attachment | None = None,
    ):
        super().__init__()
        self.content: str = ""
        self.target = target
        self.title: str = title
        self.attachment: discord.Attachment | None = attachment
        self.execute: bool = False

        # control state
        self.disable_all: bool = False
        self.inputted_once: bool = False

    @property
    def embed(self) -> Embed:
        embed = Embed(
            title=self.title,
            description=self.content,
            color=Color.default.value,
        )
        embed.add_field(
            name="送信先",
            value=self.target.mention,
        )
        if self.attachment:
            if self.attachment.content_type in ["image/png", "image/jpeg"]:
                embed.set_image(url=self.attachment.url)
            else:
                embed.add_field(
                    name="添付ファイル",
                    value=f"[{self.attachment.filename}]({self.attachment.url})",
                )
        return embed

    async def body(self) -> Message | View:
        return Message(
            embeds=[self.embed],
            components=[
                InputButton()
                .row(0)
                .disabled(self.disable_all)
                .modal(
                    InputModal(
                        components=[
                            ui.TextInput(
                                label="入力するメッセージ",
                                style=discord.TextStyle.paragraph,
                                required=True,
                                max_length=2000,
                            ),
                        ]
                    ).on_submit(
                        self.input_modal  # type: ignore
                    ),
                ),
                ExecuteButton()
                .row(0)
                .disabled(self.disable_all or not self.inputted_once)
                .on_click(self.execute_button),
                CancelButton()
                .row(0)
                .disabled(self.disable_all)
                .on_click(self.cancel_button),
            ],
        )

    async def input_modal(self, interaction: Interaction, inputted: dict[str, str]):
        self.inputted_once = True
        self.content = inputted["入力するメッセージ"]
        return

    async def execute_button(self, interaction: Interaction):
        await interaction.response.defer()

        await interaction.followup.send("送信しました。")
        self.disable_all = True
        self.execute = True
        self.stop()
        return

    async def cancel_button(self, interaction: Interaction):
        await interaction.response.defer()
        self.disable_all = True
        await interaction.followup.send("キャンセルしました。")
        self.stop()
        return


class InputButton(Button):
    def __init__(self):
        super().__init__(
            label="入力(input)",
            style=discord.ButtonStyle.blurple,
            custom_id="components.ui.message_input.input",
        )


class ExecuteButton(Button):
    def __init__(self):
        super().__init__(
            label="実行(start)",
            style=discord.ButtonStyle.blurple,
            custom_id="components.ui.message_input.execute",
        )


class CancelButton(Button):
    def __init__(self):
        super().__init__(
            label="キャンセル(cancel)",
            style=discord.ButtonStyle.red,
            custom_id="components.ui.message_input.cancel",
        )


class InputModal(Modal):
    def __init__(self, components: list[ui.TextInput]):
        super().__init__(title="メッセージ入力", components=components)