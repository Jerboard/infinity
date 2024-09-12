import logging
import requests
import httpx

from json import loads
from web3 import Web3
import coinaddrvalidator

import db
from config import Config
from enums import Coin


async def update_currency_rate():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    crypto_symbols = ['BTC', 'ETH', 'LTC', 'USDT', 'XMR']
    parameters = {
      'symbol': ','.join(crypto_symbols),
      'convert': 'RUB'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': Config.api_key_cm,
    }
    response = requests.get(url, headers=headers, params=parameters)
    response_json = response.json()
    exchange_rates = response_json['data']

    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=data)

    conn = connect ()
    cur = conn.cursor ()

    for symbol, data in exchange_rates.items ():
        rate = round (data ['quote'] ['RUB'] ['price'], 2)
        cur.execute ('update bot_manager_currency set rate = %s where code = %s', (rate, symbol))
        conn.commit ()


def update_currency_rate_binance():
    # url = 'https://api.binance.com/api/v3/ticker/price?symbols=["BTCRUB","LTCRUB","ETHRUB","XMRUSDT","USDTRUB"]'
    url = 'https://api.binance.com/api/v3/ticker/price?symbols=["BTCUSDT","LTCUSDT","ETHUSDT","XMRUSDT","USDTRUB"]'
    response = requests.get(url)
    if response.status_code == 200:

        symbols = loads(response.text)
        currency = {s['symbol']: float(s['price']) for s in symbols}
        # currency['XMRRUB'] = currency['XMRUSDT'] * currency['USDTRUB']
        # del currency['XMRUSDT']
        rate_rub = currency['USDTRUB']
        logging.warning(f'rate_rub: {rate_rub}')

        conn = connect()
        cur = conn.cursor()
        for k, v in currency.items():
            if k != 'USDTRUB':
                rate = v * rate_rub
                coin_code = k[:-4]
            else:
                rate = v
                coin_code = k [:-3]
            cur.execute('update bot_manager_currency set rate = %s where code = %s', (round(rate, 2), coin_code))
            conn.commit()

        cur.close()


# проверяет биткоин кошелёк
async def check_wallet(coin_code, wallet):
    if Config.debug:
        return True

    correct = False

    if coin_code == Coin.BTC:
        if wallet[:2] == '0x':
            web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/0ea1bde2fb984209ac916029f612fc33'))
            correct = web3.is_address(wallet)
        else:
            c = coinaddrvalidator.validate('btc', wallet)
            correct = c.valid

    elif coin_code == Coin.ETH:
        web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/0ea1bde2fb984209ac916029f612fc33'))
        correct = web3.is_address(wallet)

    elif coin_code == Coin.LTC:
        url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{wallet}"
        response = requests.get(url)
        if response.status_code == 200:
            correct = True

    elif coin_code == Coin.XMR:
        if len(wallet) == 95 or len(wallet) == 106:
            correct = True
        else:
            correct = False

    elif coin_code == Coin.USDT:
        api_key = "HNER2RJAJDMJTGRX5AFRDT5DBII3MGFYY6"
        if wallet[:2] == '0x':
            url = f"https://api.etherscan.io/api?module=account&action=balance&contractaddress=0xdac17f958d2ee523a2206206994597c13d831ec7&address={wallet}&tag=latest&apikey={api_key}"
            # response = requests.get(url)

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

            if response.status_code == 200 and response.json()['message'] == 'OK':
                correct = True
        else:
            url = f"https://apilist.tronscan.org/api/account?address={wallet}"
            # response = requests.get(url)

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

            try:
                res_json = response.json()['message']
            except:
                correct = True

    return correct
