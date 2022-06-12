from discord import ui


class TrackedModal:
    """represents a modal that is tracked by an interaction

    Args:
        modal: :class:`discord.ui.Modal`
            the modal to track.

    Attributes:
        select_values: :class:`dict[str|list[str]]`
            selected values of select menus in modal.
            key is the index of select menus.
        text_inputs: :class:`dict[str, str|None]`
        text input value in modal.
        key is the label of text inputs.

    ```python
        {
            "text_inputs": {
                "label": "value",
                "label2": None,
            },
            "select_values": {
                "0": "values",
                "1": "values",
            },
        }
    ```
    """

    def __init__(self, modal: ui.Modal) -> None:

        # raw components
        self.__buttons: list[ui.Button] = []
        self.__selects: list[ui.Select] = []
        self.__text_inputs: list[ui.TextInput] = []

        # tracked components
        self.select_values: dict[str, list[str]] = {}
        self.text_inputs: dict[str, str | None] = {}

        # convert to raw components
        for item in modal.children:
            if isinstance(item, ui.TextInput):
                # add to raw components
                self.__text_inputs.append(item)

            elif isinstance(item, ui.Select):
                # add to raw components
                self.__selects.append(item)

            elif isinstance(item, ui.Button):
                # add to raw components
                self.__buttons.append(item)
            else:
                continue

        # convert to tracked components
        self.select_values = {
            str(i): item.values for i, item in enumerate(self.__selects)
        }
        self.text_inputs = {item.label: item.value for item in self.__text_inputs}
