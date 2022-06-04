from discord import ui


def to_unavailable(view: ui.View) -> ui.View:
    for c in view.children:
        if isinstance(c, ui.Button) or isinstance(c, ui.Select):
            c.disabled = True
        else:
            pass
    return view
