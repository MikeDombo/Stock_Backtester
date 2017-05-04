class StockHist(object):
	def __init__(self, symbol, date, date_keyed, date_keys):
		self.symbol = symbol
		self.date = date
		self.date_keys = date_keys

		self.date_keyed = date_keyed

	def get(self, index=0):
		start = self.date_keys.index(self.date)

		date = self.date_keys[start + index]
		data = self.date_keyed[date][self.symbol]

		return {"open_price": data["open"], "close_price": data["close"], "price": data["close"],
		        "increase_rank": data["increase_rank"], "decrease_rank": data["decrease_rank"],
		        "change_percent": data["change"]
		        }
