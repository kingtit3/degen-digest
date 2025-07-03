from enrich.token_price import get_prices_sync


def test_price_parsing(httpx_mock):
    # mock Coingecko search and price endpoints
    search_resp = {"coins": [{"id": "pepe", "symbol": "pepe"}]}
    price_resp = {"pepe": {"usd": 0.000001, "usd_24h_change": 5.0}}

    # match any request to the search and price endpoints regardless of query-string
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/search", json=search_resp
    )
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/simple/price", json=price_resp
    )

    data = get_prices_sync(["PEPE", "UNKNOWN"])
    assert "PEPE" in data
    assert data["PEPE"]["price"] == 0.000001
    assert data["PEPE"]["change24h"] == 5.0
