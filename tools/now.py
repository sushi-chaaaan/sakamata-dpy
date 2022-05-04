from datetime import datetime, timedelta, timezone, tzinfo

utc = timezone.utc


class JST(tzinfo):
    def __repr__(self):
        return self.tzname(self)

    def utcoffset(self, dt):
        # ローカル時刻とUTCの差分に等しいtimedeltaを返す
        return timedelta(hours=9)

    def tzname(self, dt):
        # タイムゾーン名を返す
        return "Asia/Tokyo"

    def dst(self, dt):
        # 夏時間を返す。有効でない場合はtimedelta(0)を返す
        return timedelta(0)


def get_now() -> datetime:
    return datetime.now(JST())


def dt_to_str(
    datetime: datetime = datetime.now(JST()), format: str = "%Y/%m/%d %H:%M:%S"
) -> str:
    """convert datetime object to string.

    Args:
        datetime (datetime, optional): a datetime object. Defaults to datetime.now(JST()).
        if there is no tzinfo, this function will replace with UTC timezone.
        format (_type_, optional): a format used in strfttime(). Defaults to "%Y/%m/%d %H:%M:%S".

    Returns:
        str: converted string.
    """
    if not datetime.tzinfo:
        datetime.replace(tzinfo=timezone.utc)
    return datetime.strftime(format)
