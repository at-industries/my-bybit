async def afh(func, asynchrony, *args, **kwargs):
    """Async Function Handler"""
    if asynchrony:
        result = await func(*args, **kwargs)
    else:
        result = func(*args, **kwargs)
    return result


tf_to_interval = {
    '1m': 1,
    '3m': 3,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
    '2h': 120,
    '4h': 240,
    '6h': 360,
    '12h': 720,
    '1d': 'D',
    '2d': 'D',
    '1w': 'W',
    '1M': 'M',
}
