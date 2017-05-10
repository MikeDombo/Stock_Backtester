# Copyright (c) 2017 by Michael Dombrowski <http://MikeDombrowski.com/>.
#
# This file is part of Python Customizable Stock Backtester <http://github.com/md100play/Stock_Backtester/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.


class StockProcessing(object):
	def __init__(self, data_dir, date_fmt, columns):
		self.owned_stocks = {}
		self.order_history = {}
		self.data_dir = data_dir
		self.date_fmt = date_fmt
		self.csv_columns = columns
		self.symbol_keyed = {}
		self.date_keyed = {}
		self.dates_arr = []

		import logging
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s | %(message)s')
		self.logger = logging.getLogger(__name__)

	def generate_sold_stocks(self):
		import os
		import re
		import pickle
		import sys

		if not os.path.isfile("date_keyed.pkl") or not os.path.isfile("dates_arr.pkl"):
			if not os.path.isdir(self.data_dir):
				self.logger.error("Directory " + str(self.data_dir) + " does not exist!")
				sys.exit(2)
			regex = r"table_([\w\d\.]+)\.csv"
			self.logger.info("Reading in CSVs")
			for fn in os.listdir(self.data_dir):
				if os.path.isfile(os.path.join(self.data_dir, fn)):
					symbol = re.findall(regex, fn)[0].upper()
					self.symbol_keyed[symbol] = self.__process_csv(os.path.join(self.data_dir, fn), self.date_fmt, self.csv_columns)
			self.logger.info("Done Reading in CSVs")

			self.logger.info("Beginning to pivot data")
			for symbol, d in self.symbol_keyed.items():
				for data in d:
					insert = {'open': data[1], 'close': data[2], 'change': self.percent_change(data[1], data[2]),
					          "doh": data[3]}
					if data[0] not in self.date_keyed:
						self.date_keyed[data[0]] = {}
					self.date_keyed[data[0]][symbol] = insert

			self.logger.info("Done pivoting data")
			self.logger.info("Dumping pivoted data to pickle")
			pickle.dump(self.date_keyed, open("date_keyed.pkl", "wb"))
			pickle.dump(self.symbol_keyed, open("symbol_keyed.pkl", "wb"))
			self.logger.info("Done pickling")

			for date in self.date_keyed.keys():
				self.dates_arr.append(date)
			self.dates_arr.sort()
			pickle.dump(self.dates_arr, open("dates_arr.pkl", "wb"))
		else:
			self.logger.info("Loading pickled data")
			self.date_keyed = pickle.load(open("date_keyed.pkl", "rb"))
			self.dates_arr = pickle.load(open("dates_arr.pkl", "rb"))
			self.symbol_keyed = pickle.load(open("symbol_keyed.pkl", "rb"))
			self.logger.info("Done loading pickled data")

	def buy_stocks(self, buy_parser, sell_parser):
		from StockHist import StockHist
		self.logger.info("Finding stocks to buy and sell day-by-day")
		for date in self.dates_arr:
			symbol_data = self.date_keyed[date]
			losers = self.__find_biggest_losers(symbol_data)
			winners = self.__find_biggest_winners(symbol_data)
			for symbol, s_data in symbol_data.items():
				self.date_keyed[date][symbol]["increase_rank"] = winners[symbol]
				self.date_keyed[date][symbol]["decrease_rank"] = losers[symbol]

				days_of_hist = s_data["doh"]
				sh = StockHist(symbol, date, self.date_keyed, self.symbol_keyed[symbol])
				test_data = {"stock": {"symbol": symbol, "data": sh, "open_price": s_data["open"],
				                       "close_price": s_data["close"], "price": s_data["close"],
				                       "increase_rank": winners[symbol], "decrease_rank": losers[symbol],
				                       "change_percent": s_data["change"]},
				             "date": {"today": self.get_unix_time_date(date), "days_of_history": days_of_hist,
				                      "buy": 0, "day_of_week": date.isoweekday(),
				                      "month": date.month, "days": 86400, "months": 2592000, "years": 31536000}
				             }
				test_data["stock"]["owned"] = symbol in self.owned_stocks and self.owned_stocks[symbol] is not None

				if buy_parser(test_data):
					# Stocks will only be purchased when the stock is not currently owned
					self.__purchase_order(date, symbol, test_data)

				# Check if the stock is owned
				if test_data["stock"]["owned"]:
					test_data["date"]["buy"] = self.get_unix_time_date(self.owned_stocks[symbol]["date"])
					test_data["stock"]["buy_price"] = self.owned_stocks[symbol]["price"]
					# Check if we should sell this stock today
					if sell_parser(test_data):
						self.__sell_order(date, symbol, test_data)

		self.logger.info("Done finding stocks to buy and sell")

	def __purchase_order(self, date, symbol, extra_data):
		if symbol not in self.owned_stocks or self.owned_stocks[symbol] is None:
			self.owned_stocks[symbol] = {'date': date, 'price': extra_data["stock"]["data"].get(0)["price"]}

			data = {"type": "purchase", 'date': date, 'price': extra_data["stock"]["data"].get(0)["price"]}
			if symbol not in self.order_history:
				self.order_history[symbol] = [data]
			else:
				self.order_history[symbol].append(data)

	def __sell_order(self, date, symbol, extra_data):
		self.owned_stocks.pop(symbol)
		data = {"type": "sell", 'date': date, 'price': extra_data["stock"]["data"].get(0)["price"]}
		if symbol not in self.order_history:
			self.order_history[symbol] = [data]
		else:
			self.order_history[symbol].append(data)

	@staticmethod
	def __find_biggest_losers(d):
		import heapq
		minheap = []
		for symbol, data in d.items():
			heapq.heappush(minheap, (data["change"], symbol))
		ordered_stocks = [heapq.heappop(minheap) for i in range(len(minheap))]
		return_stocks = {}
		i = 0
		for change, symbol in ordered_stocks:
			return_stocks[symbol] = i
			i += 1

		return return_stocks

	@staticmethod
	def __find_biggest_winners(d):
		import heapq
		minheap = []
		for symbol, data in d.items():
			heapq.heappush(minheap, (data["change"], symbol))
		ordered_stocks = [heapq.heappop(minheap) for i in range(len(minheap))]
		ordered_stocks = reversed(ordered_stocks)
		return_stocks = {}
		i = 0
		for change, symbol in ordered_stocks:
			return_stocks[symbol] = i
			i += 1

		return return_stocks

	@staticmethod
	def get_unix_time_date(date):
		import datetime
		return (date - datetime.datetime(1970, 1, 1).date()).total_seconds()

	@staticmethod
	def get_unix_time(date):
		import datetime
		return (date - datetime.datetime(1970, 1, 1)).total_seconds()

	@staticmethod
	def __process_csv(fn, date_fmt, columns):
		import sys
		import datetime
		import csv

		data = []
		read_mode = 'rb'
		if sys.version_info >= (3, 0):
			read_mode = 'rt'
		with open(fn, read_mode) as csvF:
			reader = csv.reader(csvF)
			for row in reader:
				if row[columns[0]][0].isdigit():
					date = datetime.datetime.strptime(row[columns[0]], date_fmt).date()
					data += [[date, float(row[columns[1]]), float(row[columns[2]])]]
			data.sort(key=lambda x: x[0])
			doh = 0
			for dr in data:
				dr.append(doh)
				doh += 1

		return data

	@staticmethod
	def percent_change(original, new_val):
		if original is None or new_val is None:
			return None
		if original == 0:
			return 0
		return (new_val - original) / original
