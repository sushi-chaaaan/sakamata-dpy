import gspread as gs


class GSheet:
    def __init__(self, *, sheet_key: str, cred: str) -> None:
        gc = gs.service_account(filename=cred)
        self.sheet = gc.open_by_key(sheet_key)
