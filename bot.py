from binance import Client
import os
from dotenv import load_dotenv
from binance.exceptions import BinanceAPIException
import uuid
import logging
from datetime import datetime

load_dotenv()

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
    ]
)

for logger_name in ['urllib3', 'http.client', 'requests', 'binance']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class BasicBot:
	def __init__(self, api_key, api_secret, testnet=True):
		self.client = Client(api_key, api_secret, testnet=testnet)
	
	def create_futures_limit_order(self, symbol, side, type, quantity, price):
		logger.info(f"REQUEST: create_futures_limit_order | symbol={symbol}, side={side}, type={type}, quantity={quantity}, price={price}")
		try:
			res = self.client.futures_create_order(
				symbol=symbol,
				side=side,
				type=type,
				timeinforce='GTC',
				quantity=quantity,
				price=price)
			logger.info(f"RESPONSE: create_futures_limit_order | success=True | data={res}")
			return {"success": True, "data": res}
		except BinanceAPIException as e:
			logger.error(f"ERROR: create_futures_limit_order | BinanceAPIException | {e}")
			return {"success": False, "error": f"API Error: {e}"}
		except Exception as e:
			logger.error(f"ERROR: create_futures_limit_order | Unexpected error | {e}")
			return {"success": False, "error": f"Unexpected error: {e}"}

	def create_futures_market_order(self, symbol, side, type, quantity):
		logger.info(f"REQUEST: create_futures_market_order | symbol={symbol}, side={side}, type={type}, quantity={quantity}")
		try:
			res = self.client.futures_create_order(
				symbol=symbol,
				side=side,
				type=type,
				quantity=quantity)
			logger.info(f"RESPONSE: create_futures_market_order | success=True | data={res}")
			return {"success": True, "data": res}
		except BinanceAPIException as e:
			logger.error(f"ERROR: create_futures_market_order | BinanceAPIException | {e}")
			return {"success": False, "error": f"API Error: {e}"}
		except Exception as e:
			logger.error(f"ERROR: create_futures_market_order | Unexpected error | {e}")
			return {"success": False, "error": f"Unexpected error: {e}"}
		
	def create_stop_limit_order(self, symbol, side, stop_price, price, quantity, working_type="MARK_PRICE"):
		logger.info(f"REQUEST: create_stop_limit_order | symbol={symbol}, side={side}, stop_price={stop_price}, price={price}, quantity={quantity}, working_type={working_type}")
		try:
			client_algo_id = "x-4096-" + str(uuid.uuid4()).replace("-", "")[:22]
			if working_type == "LAST_PRICE":
				bt_working_type = "CONTRACT_PRICE"
			else:
				bt_working_type = "MARK_PRICE"

			res = self.client.futures_create_algo_order(
				symbol=symbol,
				side=side,
				type='STOP',
				quantity=quantity,
				price=price,
				triggerPrice=stop_price, 
				workingType=bt_working_type,
				algoType='CONDITIONAL',  
				clientAlgoId=client_algo_id,
				timeInForce='GTC'
			)
			logger.info(f"RESPONSE: create_stop_limit_order | success=True | data={res}")
			return {"success": True, "data": res}
		except BinanceAPIException as e:
			logger.error(f"ERROR: create_stop_limit_order | BinanceAPIException | {e}")
			return {"success": False, "error": f"API Error: {e}"}
		except Exception as e:
			logger.error(f"ERROR: create_stop_limit_order | Unexpected error | {e}")
			return {"success": False, "error": f"Unexpected error: {e}"}
		
	def get_mark_price(self, symbol: str):
		"""Fetches the current Mark Price for a specific futures symbol."""
		try:
			return self.client.futures_mark_price(symbol=symbol.upper())
		except Exception:
			return None

