class StockHist(object):
	def __init__(self, symbol, date, symbol_data, date_keyed):
		self.symbol = symbol
		self.date = date
		self.open = []
		self.close = []
		self.price = []
		self.change = []
		self.incr_rank = []
		self.decr_rank = []

		symbol_data.sort(key=lambda x: x[0])
		symbol_data.reverse()
		self.date_keyed = date_keyed
		self.symbol_data = symbol_data

	def get(self, index=0):
		for sd in self.symbol_data:
			if sd[0] > self.date or len(self.price) > index:
				continue
			self.open.append(sd[1])
			self.close.append(sd[2])
			self.price.append(sd[2])
			self.change.append(self.date_keyed[sd[0]][self.symbol]["change"])
			self.incr_rank.append(self.date_keyed[sd[0]][self.symbol]["increase_rank"])
			self.decr_rank.append(self.date_keyed[sd[0]][self.symbol]["decrease_rank"])

		returner = {"open_price": self.open[index], "close_price": self.close[index], "price": self.price[index],
		            "increase_rank": self.incr_rank[index], "decrease_rank": self.decr_rank[index],
		            "change_percent": self.change[index]
		            }

		self.open = []
		self.close = []
		self.price = []
		self.change = []
		self.incr_rank = []
		self.decr_rank = []

		return returner
