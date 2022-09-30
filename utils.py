import ntptime
from time import localtime


def get_format_time():
    """
    获取格式化过的时间
    """
    y, mo, d, h, mi, s, wkd, yd = localtime()
    return f"{y:04}/{mo:02}/{d:02} {h:02}:{mi:02}:{s:02}"

def get_simple_time():
    y, mo, d, h, mi, s, wkd, yd = localtime()
    return f"{d:02} | {h:02}:{mi:02}:{s:02}"

def logger(*args):
    print(f"[{get_format_time()}]", *args)

class SYNC_ERROR(Exception):
    pass

async def sync_ntp():
    """
    通过 ntp 服务器同步时间
    """
    ntptime.NTP_DELTA = 3155644800
    ntptime.host = 'ntp1.aliyun.com'
    try:
        ntptime.settime()
    except Exception as e:
        print(e)
        raise SYNC_ERROR


async def sync_time():
    try:
        await sync_ntp()
    except SYNC_ERROR as e:
        logger('ntp同步失败...')
    else:
        logger('ntp同步成功.')
