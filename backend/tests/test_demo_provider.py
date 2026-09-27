import asyncio

from app.providers.demo_market_data import DemoMarketDataProvider


def test_historical_candles_are_deterministic():
    provider = DemoMarketDataProvider()

    async def run():
        a = await provider.get_candles("RELIANCE", days=100)
        b = await provider.get_candles("RELIANCE", days=100)
        return a, b

    a, b = asyncio.run(run())
    assert [c.close for c in a] == [c.close for c in b]
    assert [c.volume for c in a] == [c.volume for c in b]


def test_different_symbols_produce_different_series():
    provider = DemoMarketDataProvider()

    async def run():
        a = await provider.get_candles("RELIANCE", days=50)
        b = await provider.get_candles("TCS", days=50)
        return a, b

    a, b = asyncio.run(run())
    assert [c.close for c in a] != [c.close for c in b]


def test_unknown_symbol_raises():
    provider = DemoMarketDataProvider()

    async def run():
        await provider.get_candles("NOT_A_REAL_SYMBOL", days=10)

    try:
        asyncio.run(run())
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_all_quotes_flagged_demo():
    provider = DemoMarketDataProvider()

    async def run():
        symbols = await provider.list_symbols()
        return await provider.get_quotes(symbols)

    quotes = asyncio.run(run())
    assert len(quotes) > 0
    assert all(q.is_demo for q in quotes)
