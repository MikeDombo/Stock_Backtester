import os
import csv
import datetime
import pickle
import heapq
import re
import sys
import argparse
import logging
from booleano.parser import SymbolTable, Bind

owned_stocks = {}
order_history = {}


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
				insert = {'open': data[1], 'close': data[2], 'change': percent_change(data[1], data[2]), "doh": data[3]}
				if data[0] not in date_keyed:
					date_keyed[data[0]] = {}
				date_keyed[data[0]][symbol] = insert

		#del symbol_keyed
		logger.info("Done pivoting data")
		logger.info("Dumping pivoted data to pickle")
		pickle.dump(date_keyed, open("date_keyed.pkl", "wb"))
		pickle.dump(symbol_keyed, open("symbol_keyed.pkl", "wb"))
		logger.info("Done pickling")

		dates_arr = []
		for date in date_keyed.keys():
			dates_arr.append(date)
		dates_arr.sort()
		pickle.dump(dates_arr, open("dates_arr.pkl", "wb"))

		buy_stocks(date_keyed, dates_arr, symbol_keyed, buy_parser, sell_parser)
	else:
		logger.info("Loading pickled data")
		date_keyed = pickle.load(open("date_keyed.pkl", "rb"))
		dates_arr = pickle.load(open("dates_arr.pkl", "rb"))
		symbol_keyed = pickle.load(open("symbol_keyed.pkl", "rb"))
		logger.info("Done loading pickled data")
		buy_stocks(date_keyed, dates_arr, symbol_keyed, buy_parser, sell_parser)

	output_dir = "output"
	analyze_trades(order_history, owned_stocks, dates_arr, date_keyed, output_dir)


def analyze_trades(order_history, owned_stocks, dates_arr, date_keyed, output_dir):
	# Make directories to store CSVs
	curr_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	new_dir = os.path.join(output_dir, curr_date)
	directory_num = 1
	while os.path.isdir(new_dir):
		new_dir = os.path.join(output_dir, curr_date + "_" + str(directory_num))
		directory_num += 1
	os.makedirs(new_dir)

	with open(os.path.join(new_dir, "generator_options.txt"), "w") as text_file:
		text_file.write("Buy Conditions: %s \r\n" % buy_conditions)
		text_file.write("Sell Conditions: %s \r\n" % sell_conditions)

	column_names = ["Buy Date", "Symbol", "Buy Price", "Sell Date", "Sell Price", "% Change"]
	numeric_columns = ["Buy Price", "Sell Price", "% Change"]

	column_data = []
	numeric_data = []
	for symbol, trades in order_history.items():
		trades = sorted(trades, key=lambda k: k['date'])
		for trade_num, trade in enumerate(trades):
			if trade["type"] == "sell":
				column_data.append([trades[trade_num - 1]["date"], symbol, trades[trade_num - 1]["price"],
				                    trade["date"], trade["price"],
				                    percent_change(trades[trade_num - 1]["price"], trade["price"])
				                    ])
				numeric_data.append([trades[trade_num - 1]["price"], trade["price"],
				                     percent_change(trades[trade_num - 1]["price"], trade["price"])])

	sold_stats = write_to_csv_split(column_data, numeric_data, column_names, numeric_columns, "sold_stocks", new_dir)

	print("\r\n\r\n")

	with open(os.path.join(new_dir, "analysis.txt"), "w") as analysis_text_file:
		print(str("*" * 120) + "\r\n")
		print_and_write(analysis_text_file,
		                "Analyzing Trades For Stock Data Between %s And %s" % (dates_arr[0], dates_arr[-1]))
		print_and_write(analysis_text_file, "\r\n" + str("*" * 120))
		print_and_write(analysis_text_file, "\r\nStocks That Were Bought And Sold\n" + str("=" * 60))
		for name in numeric_columns:
			print_and_write(analysis_text_file, name + " :\t%s" % sold_stats.get_stats(name))

		column_data = []
		numeric_data = []
		last_day = dates_arr[-1]
		for symbol, trade in owned_stocks.items():
			column_dat = [trade["date"], symbol, trade["price"]]
			numeric_dat = [trade["price"]]
			if symbol in date_keyed[last_day]:
				symbol_last_day = date_keyed[last_day][symbol]
				column_dat.extend(
					[last_day, symbol_last_day["close"], percent_change(trade["price"], symbol_last_day["close"])])
				numeric_dat.extend([symbol_last_day["close"], percent_change(trade["price"], symbol_last_day["close"])])
			else:
				column_dat.extend([last_day, 0, -1])
				numeric_dat.extend([0, -1])
			column_data.append(column_dat)
			numeric_data.append(numeric_dat)

		column_names = ["Buy Date", "Symbol", "Buy Price", "Would-be Sell Date", "Would-be Sell Price",
		                "Would-be % Change"]
		numeric_columns = ["Buy Price", "Would-be Sell Price", "Would-be % Change"]

		unsold_stats = write_to_csv_split(column_data, numeric_data, column_names, numeric_columns, "unsold_stocks",
		                                  new_dir)

		s = "\r\n\r\nStocks That Were Only Bought And Never Sold. (Would-be means what would happen if the stocks were " \
		    "sold on the last day, %s)\n" % last_day + str("=" * 60)
		print_and_write(analysis_text_file, s)

		for name in numeric_columns:
			print_and_write(analysis_text_file, name + " :\t%s" % unsold_stats.get_stats(name))

		print_and_write(analysis_text_file, "\r\n\r\n" + str("*" * 100) + "\r\n")
		import locale
		locale.setlocale(locale.LC_ALL, '')

		num = float(sold_stats.get_stats("% Change")["mean"] * 100)
		print_and_write(analysis_text_file, "Percent gain/loss if you bought an equal dollar amount of each stock: %s%%"
		                % locale.format('%.4f', num, grouping=True))

		amount_spent = sold_stats.get_stats("Buy Price")["sum"]
		amount_from_sales = sold_stats.get_stats("Sell Price")["sum"]
		num = float(percent_change(amount_spent, amount_from_sales) * 100)
		print_and_write(analysis_text_file, "Percent gain/loss if you bought equal number of stocks: %s%%"
		                % locale.format('%.4f', num, grouping=True))

		print_and_write(analysis_text_file, "\r\nPercent gain/loss including stocks that were unsold. (Assumes they "
		                                    "are sold on the last day)")

		chn = sold_stats.get_values("% Change") + unsold_stats.get_values("Would-be % Change")
		num = float((sum(chn) / len(chn)) * 100)
		print_and_write(analysis_text_file, "Percent gain/loss if you bought an equal dollar amount of each stock: %s%%"
		                % locale.format('%.4f', num, grouping=True))

		amount_spent = sold_stats.get_stats("Buy Price")["sum"] + unsold_stats.get_stats("Buy Price")["sum"]
		amount_from_sales = sold_stats.get_stats("Sell Price")["sum"] + unsold_stats.get_stats("Would-be Sell Price")[
			"sum"]
		num = float(percent_change(amount_spent, amount_from_sales) * 100)
		print_and_write(analysis_text_file, "Percent gain/loss if you bought equal number of stocks: %s%%"
		                % locale.format('%.4f', num, grouping=True))

	print("\r\n\r\n")


def print_and_write(fp, s):
	print(s)
	fp.write(s + str("\r\n"))


def write_to_csv_split(column_data, numeric_data, column_names, numeric_columns, filename, output_dir):
	import Statistics
	stock_stats = Statistics.Statistics(column_names)

	max_rows = 1048000
	row_count = 0
	for sheet_num in range(0, int((len(column_data) / max_rows) + 1)):
		csv_filename = os.path.join(output_dir, filename + "_" + str(sheet_num) + ".csv")
		opener = open(csv_filename, "wb")

		# Fix for Python 3.x
		if sys.version_info >= (3, 0):
			opener = open(csv_filename, "w", newline='')

		with opener as csvF:
			writer = csv.writer(csvF)
			writer.writerow(column_names)

			count = 0
			for r, row_data in enumerate(column_data):
				if count < row_count:
					count += 1
					continue
				if count > max_rows * (sheet_num + 1):
					break

				writer.writerow(row_data)
				stock_stats.add_data_multi(numeric_columns, numeric_data[r])

				count += 1
				row_count += 1

	return stock_stats


def buy_stocks(date_keyed, date_keys, symbol_keyed, buy_parser, sell_parser):
	from StockHist import StockHist
	logger.info("Finding stocks to buy and sell day-by-day")
	for date in date_keys:
		symbol_data = date_keyed[date]
		losers = find_biggest_losers(symbol_data)
		winners = find_biggest_winners(symbol_data)
		for symbol, s_data in symbol_data.items():
			date_keyed[date][symbol]["increase_rank"] = winners[symbol]
			date_keyed[date][symbol]["decrease_rank"] = losers[symbol]

			days_of_hist = s_data["doh"]
			sh = StockHist(symbol, date, date_keyed, symbol_keyed[symbol])
			test_data = {"stock": {"symbol": symbol, "data": sh, "open_price": s_data["open"],
			                       "close_price": s_data["close"], "price": s_data["close"],
			                       "increase_rank": winners[symbol], "decrease_rank": losers[symbol],
			                       "change_percent": s_data["change"]},
			             "date": {"today": get_unix_time_date(date), "days_of_history": days_of_hist,
			                      "buy": 0, "day_of_week": date.isoweekday(),
			                      "month": date.month, "days": 86400, "months": 2592000, "years": 31536000}
			             }
			test_data["stock"]["owned"] = symbol in owned_stocks and owned_stocks[symbol] is not None

			if buy_parser(test_data):
				# Stocks will only be purchased when the stock is not currently owned
				purchase_order(date, symbol, test_data)

			# Check if the stock is owned
			if test_data["stock"]["owned"]:
				test_data["date"]["buy"] = get_unix_time_date(owned_stocks[symbol]["date"])
				test_data["stock"]["buy_price"] = owned_stocks[symbol]["price"]
				# Check if we should sell this stock today
				if sell_parser(test_data):
					sell_order(date, symbol, test_data)

	logger.info("Done finding stocks to buy and sell")


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


def get_unix_time(date):
	return (date - datetime.datetime(1970, 1, 1)).total_seconds()


def purchase_order(date, symbol, extra_data):
	if symbol not in owned_stocks or owned_stocks[symbol] is None:
		owned_stocks[symbol] = {'date': date, 'price': extra_data["stock"]["data"].get(0)["price"]}

		data = {"type": "purchase", 'date': date, 'price': extra_data["stock"]["data"].get(0)["price"]}
		if symbol not in order_history:
			order_history[symbol] = [data]
		else:
			order_history[symbol].append(data)


def sell_order(date, symbol, extra_data):
	owned_stocks.pop(symbol)
	data = {"type": "sell", 'date': date, 'price': extra_data["stock"]["data"].get(0)["price"]}
	if symbol not in order_history:
		order_history[symbol] = [data]
	else:
		order_history[symbol].append(data)


def percent_change(original, new_val):
	if original is None or new_val is None:
		return None
	if original == 0:
		return 0
	return (new_val - original) / original


def process_csv(fn, date_fmt, columns):
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
	parser.add_argument('-cf', '--condition_file', type=str, nargs=1,
	                    help='File containing buy and sell conditions')
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
	if (not args.buy_conditions or not args.sell_conditions) and not args.condition_file:
		print("Buy or sell conditions missing")
		sys.exit(2)

	if args.condition_file:
		read_mode = 'rb'
		if sys.version_info >= (3, 0):
			read_mode = 'rt'
		with open(args.condition_file[0], read_mode) as cond_file:
			data = cond_file.read()

		import re
		regex = r"Buy Conditions:\s+(?P<buy_cond>.*)\s*Sell Conditions:\s+(?P<sell_cond>.*)"
		reg = re.compile(regex, re.MULTILINE)
		m = reg.match(data)

		buy_conditions = m.group(reg.groupindex["buy_cond"])
		sell_conditions = m.group(reg.groupindex["sell_cond"])

	else:
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
		                                     Bind("owned", stockVars.StockOwned()),
		                                     Bind("buy_price", stockVars.StockBuyPrice()),
	                                     ],
	                                     SymbolTable("decrease_rank", []),
	                                     SymbolTable("increase_rank", []),
	                                     SymbolTable("open_price", []),
	                                     SymbolTable("close_price", []),
	                                     SymbolTable("price", []),
	                                     SymbolTable("change_percent", []),
	                                     ),
	                         SymbolTable("date",
	                                     [
		                                     Bind("today", today_var),
		                                     Bind("buy", stockVars.DateBuy()),
		                                     Bind("days_of_history", stockVars.DateDaysOfHistory()),
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

	import os
	import psutil
	p = psutil.Process(os.getpid())
	print("Execution took %s seconds" % p.cpu_times().user)
