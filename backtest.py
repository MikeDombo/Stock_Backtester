import os
import csv
import datetime
import pickle
import heapq
from dateutil.relativedelta import relativedelta
import re
import sys
import argparse
import logging
from booleano.parser import SymbolTable, Bind

owned_stocks = {}
order_history = []


def generate_sold_stocks(data_dir, date_fmt, columns):
	if not os.path.isfile("date_keyed.pkl") or not os.path.isfile("dates_arr.pkl"):
		if not os.path.isdir(data_dir):
			logger.error("Directory " + str(data_dir) + " does not exist!")
			sys.exit(2)
		symbol_keyed = {}
		regex = r"table_([\w\d\.]+)\.csv"
		logger.info("Reading in CSVs")
		for fn in os.listdir(data_dir):
			if os.path.isfile(os.path.join(data_dir, fn)):
				symbol = re.findall(regex, fn)[0].upper()
				symbol_keyed[symbol] = process_csv(os.path.join(data_dir, fn), date_fmt, columns)
		logger.info("Done Reading in CSVs")

		date_keyed = {}
		logger.info("Beginning to pivot data")
		for symbol, d in symbol_keyed.items():
			for data in d:
				insert = {'open': data[1], 'close': data[2], 'change': percent_change(data[1], data[2])}
				if data[0] not in date_keyed:
					date_keyed[data[0]] = {}
				date_keyed[data[0]][symbol] = insert

		del symbol_keyed
		logger.info("Done pivoting data")
		logger.info("Dumping pivoted data to pickle")

		pickle.dump(date_keyed, open("date_keyed.pkl", "wb"))
		logger.info("Done pickling")

		dates_arr = []
		for date in date_keyed.keys():
			dates_arr.append(date)
		dates_arr.sort()
		pickle.dump(dates_arr, open("dates_arr.pkl", "wb"))

		buy_stocks(date_keyed, dates_arr, buy_parser, sell_parser)
	else:
		logger.info("Loading pickled data")
		date_keyed = pickle.load(open("date_keyed.pkl", "rb"))
		dates_arr = pickle.load(open("dates_arr.pkl", "rb"))
		logger.info("Done loading pickled data")
		buy_stocks(date_keyed, dates_arr, buy_parser, sell_parser)

	print(owned_stocks)


def buy_stocks(date_keyed, date_keys, buy_parser, sell_parser):
	logger.info("Finding stocks to buy and sell day-by-day")
	for date in date_keys:
		symbol_data = date_keyed[date]
		losers = find_biggest_losers(symbol_data)
		winners = find_biggest_winners(symbol_data)
		# Consider putting winners and losers back into date_keyed to be used by the sell method
		for symbol, s_data in symbol_data.items():
			test_data = {"stock": {"symbol": symbol, "open_price": s_data["open"],
			                       "close_price": s_data["close"], "price": s_data["close"],
			                       "increase_rank": winners[symbol], "decrease_rank": losers[symbol],
			                       "change_percent": s_data["change"]},
			             "date": {"today": get_unix_time_date(date),
			                      "buy": 0, "day_of_week": date.isoweekday(),
			                      "month": date.month, "days": 86400, "months": 2592000, "years": 31536000}
			             }

			if buy_parser(test_data):
				# Stocks will only be purchased when the stock is not currently owned
				purchase_order(date, symbol, test_data)

			# Check if the stock is owned
			if symbol in owned_stocks and owned_stocks[symbol] is not None:
				test_data["date"]["buy"] = get_unix_time_date(owned_stocks[symbol]["buy_date"])
				# Check if we should sell this stock today
				if sell_parser(test_data):
					sell_order(date, symbol, test_data)


def find_biggest_losers(d):
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


def find_biggest_winners(d):
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


def get_unix_time_date(date):
	return (date - datetime.datetime(1970, 1, 1).date()).total_seconds()


def get_unix_time_(date):
	return (date - datetime.datetime(1970, 1, 1)).total_seconds()


def purchase_order(date, symbol, extra_data):
	if symbol not in owned_stocks or owned_stocks[symbol] is None:
		owned_stocks[symbol] = {'buy_date': date, 'buy_price': extra_data["stock"]["price"]}
		order_history.append({"type": "purchase", "symbol": symbol, 'buy_date': date,
		                      'buy_price': extra_data["stock"]["price"]})


def sell_order(date, symbol, extra_data):
	owned_stocks.pop(symbol)
	order_history.append({"type": "sell", "symbol": symbol, 'sell_date': date,
	                      'sell_price': extra_data["stock"]["price"]})


def percent_change(original, new_val):
	if original is None or new_val is None:
		return None
	if original == 0:
		return 0
	return (new_val - original) / original


def process_csv(fn, date_fmt, columns):
	data = []
	with open(fn, 'rb') as csvF:
		reader = csv.reader(csvF)
		for row in reader:
			if row[columns[0]][0].isdigit():
				date = datetime.datetime.strptime(row[columns[0]], date_fmt).date()
				data += [[date, float(row[columns[1]]), float(row[columns[2]])]]
	return data


def line_count(file):
	return sum(1 for line in open(file))


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process Stock Data')
	parser.add_argument('-d', '--directory', type=str, nargs=1, help='Directory containing csv files of stock data')
	parser.add_argument('-b', '--buy_conditions', type=str, nargs='+',
	                    help='Conditions under which a stock should be purchased')
	parser.add_argument('-s', '--sell_conditions', type=str, nargs='+',
	                    help='Conditions under which an owned stock should be sold')
	parser.add_argument('-df', '--csv_date_format', type=str, nargs='+', help='Python string format for date')
	parser.add_argument('-oc', '--open_column', type=int, nargs=1, help='Zero-indexed CSV column for the open price')
	parser.add_argument('-cc', '--close_column', type=int, nargs=1, help='Zero-indexed CSV column for the close price')
	parser.add_argument('-dc', '--date_column', type=int, nargs=1, help='Zero-indexed CSV column for the date')

	args = parser.parse_args()
	data_dir = "data"
	date_fmt = '%Y-%m-%d'
	date_column = 0
	open_column = 1
	close_column = 4

	if args.directory:
		data_dir = args.directory[0]
	if args.csv_date_format:
		date_fmt = args.csv_date_format[0]
	if args.open_column:
		open_column = args.open_column[0]
	if args.close_column:
		close_column = args.close_column[0]
	if args.date_column:
		date_column = args.date_column[0]
	if not args.buy_conditions or not args.sell_conditions:
		print("Buy or sell conditions missing")
		sys.exit(2)

	buy_conditions = args.buy_conditions[0]
	sell_conditions = args.sell_conditions[0]

	import stockVars

	stock_symbol_var = stockVars.StockSymbol()
	today_var = stockVars.DateToday()

	root_table = SymbolTable("root",
	                         [
		                         Bind("stock", stock_symbol_var),
		                         Bind("date", today_var),
	                         ],
	                         SymbolTable("stock",
	                                     [
		                                     Bind("symbol", stock_symbol_var),
		                                     Bind("open_price", stockVars.StockOpenPrice()),
		                                     Bind("close_price", stockVars.StockClosePrice()),
		                                     Bind("price", stockVars.StockPrice()),
		                                     Bind("increase_rank", stockVars.StockIncreaseRank()),
		                                     Bind("decrease_rank", stockVars.StockDecreaseRank()),
		                                     Bind("change_percent", stockVars.StockPercChange()),
	                                     ]
	                                     ),
	                         SymbolTable("date",
	                                     [
		                                     Bind("today", today_var),
		                                     Bind("buy", stockVars.DateBuy()),
		                                     Bind("day_of_week", stockVars.DateDayOfWeek()),
		                                     Bind("month", stockVars.DateMonth()),
		                                     Bind("days", stockVars.DateDays()),
		                                     Bind("months", stockVars.DateMonths()),
		                                     Bind("years", stockVars.DateYears()),
	                                     ]
	                                     )
	                         )

	from booleano.parser import Grammar

	new_tokens = {
		'and': '&&',
		'or': '||',
		'belongs_to': 'in',
		'is_subset': 'subset of'
	}
	english_grammar = Grammar(**new_tokens)
	from booleano.parser import EvaluableParseManager

	parse_manager = EvaluableParseManager(root_table, english_grammar)

	buy_parser = parse_manager.parse(buy_conditions)
	sell_parser = parse_manager.parse(sell_conditions)

	print(buy_parser)
	print(sell_parser)

	generate_sold_stocks(data_dir, date_fmt, (date_column, open_column, close_column))
