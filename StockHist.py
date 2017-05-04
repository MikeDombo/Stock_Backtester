class StockHist(object):
	date_keyed = {}

	def __init__(self, symbol, date, date_keyed, symbol_keyed):
		self.symbol = symbol
		self.date = date
		self.date_keyed = date_keyed
		self.symbol_keyed = symbol_keyed

	def get(self, index=0):
		for i, d in enumerate(self.symbol_keyed):
			if d[0] == self.date:
				break
		sd = self.symbol_keyed[i - index]
		data = self.date_keyed[sd[0]][self.symbol]

		return {"open_price": data["open"], "close_price": data["close"], "price": data["close"],
		        "increase_rank": data["increase_rank"], "decrease_rank": data["decrease_rank"],
		        "change_percent": data["change"]
		        }
