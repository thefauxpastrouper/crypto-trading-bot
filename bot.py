from binance import Client
import os
from dotenv import load_dotenv
from binance.exceptions import BinanceAPIException
import uuid

load_dotenv()

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')


class BasicBot:
	def __init__(self, api_key, api_secret, testnet=True):
		self.client = Client(api_key, api_secret, testnet=testnet)
	
	def create_futures_limit_order(self, symbol, side, type, quantity, price):
		try:
			res = self.client.futures_create_order(
				symbol=symbol,
				side=side,
				type=type,
				timeinforce='GTC',
				quantity=quantity,
				price=price)
			return {"success": True, "data": res}
		except BinanceAPIException as e:
			return {"success": False, "error": f"API Error: {e}"}
		except Exception as e:
			return {"success": False, "error": f"Unexpected error: {e}"}

	def create_futures_market_order(self, symbol, side, type, quantity):
		try:
			res = self.client.futures_create_order(
				symbol=symbol,
				side=side,
				type=type,
				quantity=quantity)
			return {"success": True, "data": res}
		except BinanceAPIException as e:
			return {"success": False, "error": f"API Error: {e}"}
		except Exception as e:
			return {"success": False, "error": f"Unexpected error: {e}"}
		
	def create_stop_limit_order(self, symbol, side, stop_price, price, quantity, working_type="MARK_PRICE"):
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
			return {"success": True, "data": res}
		except BinanceAPIException as e:
			return {"success": False, "error": f"API Error: {e}"}
		except Exception as e:
			return {"success": False, "error": f"Unexpected error: {e}"}
		
	def get_mark_price(self, symbol: str):
		"""Fetches the current Mark Price for a specific futures symbol."""
		try:
			return self.client.futures_mark_price(symbol=symbol.upper())
		except Exception:
			return None

