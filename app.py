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


def generate_sold_stocks(data_dir, date_fmt, columns, num_to_buy):
	bought_stocks = []
	if not os.path.isfile("date_keyed.pkl"):
		if not os.path.isdir(data_dir):
			logger.error("Directory "+str(data_dir)+" does not exist!")
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
		bought_stocks = find_bought_stocks(date_keyed, num_to_buy)
	else:
		logger.info("Loading pickled data")
		date_keyed = pickle.load(open("date_keyed.pkl", "rb"))
		logger.info("Done loading pickled data")
		bought_stocks = find_bought_stocks(date_keyed, num_to_buy)

	sold_stocks = []
	logger.info("Finding profits/losses")
	market_data_days = date_keyed.keys()
	for buy_order in bought_stocks:
		date = buy_order["day"]
		symbol = buy_order["symbol"]
		buy_price = buy_order["price"]
		change_bought_on = buy_order["change"]
		rank = buy_order["rank"]

		date_plus_month = market_day(date+relativedelta(months=1), market_data_days)
		date_plus_6_months = market_day(date+relativedelta(months=6), market_data_days)
		date_plus_year = market_day(date + relativedelta(years=1), market_data_days)
		date_plus_5_years = market_day(date + relativedelta(years=5), market_data_days)

		sell_order = {"symbol": symbol, "buy_date": date, "buy_price": buy_price, "buy_change": change_bought_on,
					  "sell_month": 0, "sell_6_months": 0, "sell_year": 0, "sell_5_years": 0, "buy_rank": rank}

		if date_plus_month is not False and date_plus_month is not None:
			if symbol in date_keyed[date_plus_month]:
				sell_order["sell_month"] = date_keyed[date_plus_month][symbol]["close"]
		elif date_plus_month is False:
			sell_order["sell_month"] = None
		if date_plus_6_months is not False and date_plus_6_months is not None:
			if symbol in date_keyed[date_plus_6_months]:
				sell_order["sell_6_months"] = date_keyed[date_plus_6_months][symbol]["close"]
		elif date_plus_6_months is False:
			sell_order["sell_6_months"] = None
		if date_plus_year is not False and date_plus_year is not None:
			if symbol in date_keyed[date_plus_year]:
				sell_order["sell_year"] = date_keyed[date_plus_year][symbol]["close"]
		elif date_plus_year is False:
			sell_order["sell_year"] = None
		if date_plus_5_years is not False and date_plus_5_years is not None:
			if symbol in date_keyed[date_plus_5_years]:
				sell_order["sell_5_years"] = date_keyed[date_plus_5_years][symbol]["close"]
		elif date_plus_5_years is False:
			sell_order["sell_5_years"] = None
		sold_stocks += [sell_order]

	logger.info("Done finding P&L")
	logger.info("Pickling sold stocks")
	pickle.dump(sold_stocks, open("sold_stocks.pkl", "wb"))
	logger.info("Done pickling sold stocks")
	analyze_trades(sold_stocks)


def market_day(date, market_data_days):
	"""
	Returns the next market day for which data is available.
	:param date:
	:param market_data_days:
	:return: date if a market day could be found. None if a market day could not be found. False if the day has not
	yet occurred
	"""
	if date in market_data_days:
		return date
	if date > max(market_data_days):
		return False

	for i in range(-1, 5):
		if date + relativedelta(days=i) in market_data_days:
			return date + relativedelta(days=i)

	return None


def find_bought_stocks(date_keyed, length):
	if not os.path.isfile("bought_stocks.pkl") and date_keyed is not None:
		bought_stocks = []
		logger.info("Finding daily losers")
		for date, symbol_data in date_keyed.items():
			a = find_biggest_losers(symbol_data, length)
			for symbol, rank in a:
				bought_stocks += [{'symbol': symbol, 'price': symbol_data[symbol]['close'],
								   'change': symbol_data[symbol]['change'], 'day': date, 'rank': rank}]
		# Sort the bought stocks by date of purchase
		bought_stocks = sorted(bought_stocks, key=lambda k: k['day'])

		logger.info("Dumping bought stock data to pickle")
		pickle.dump(bought_stocks, open("bought_stocks.pkl", "wb"))
		logger.info("Done pickling")
		return bought_stocks
	else:
		logger.info("Loading pickled bought stocks")
		p = pickle.load(open("bought_stocks.pkl", "rb"))
		logger.info("Done loading pickled bought stocks")
		return p


def find_biggest_losers(d, length=50):
	minheap = []
	for symbol, data in d.items():
		heapq.heappush(minheap, (data["change"], symbol))

	if len(minheap) < length:
		length = len(minheap)
	ordered_stocks = [heapq.heappop(minheap) for i in range(length)]

	return_stocks = []
	i = 0
	for change, symbol in ordered_stocks:
		return_stocks += [(symbol, i)]
		i += 1

	return return_stocks


def percent_change(open, close):
	if open is None or close is None:
		return None
	if open == 0:
		return 0
	return (close-open)/open


def process_csv(fn, date_fmt, columns):
	data = []
	with open(fn, 'rb') as csvF:
		reader = csv.reader(csvF)
		for row in reader:
			if row[columns[0]][0].isdigit():
				date = datetime.datetime.strptime(row[columns[0]], date_fmt).date()
				if date >= datetime.datetime.strptime("1990-01-01", '%Y-%m-%d').date():
					data += [[date, float(row[columns[1]]), float(row[columns[2]])]]
	return data


def line_count(file):
	return sum(1 for line in open(file))


def analyze_trades(sold_stocks=None):
	logger.info("Analyzing trades")
	if sold_stocks is None:
		logger.info("Loading trades from pickle")
		sold_stocks = pickle.load(open("sold_stocks.pkl", "rb"))
		logger.info("Done loading trades")

	# Make directories to store CSVs
	output_dir = "output"
	curr_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	new_dir = os.path.join(output_dir, curr_date)
	directory_num = 1
	while os.path.isdir(new_dir):
		new_dir = os.path.join(output_dir, curr_date + "_" + str(directory_num))
		directory_num += 1
	os.makedirs(new_dir)

	column_names = ["Symbol", "Buy Date", "Change on Buy Date", "Rank", "Buy Price",
					 "Sell 1 Month Change", "Sell 6 Months Change",
					 "Sell 1 Year Change", "Sell 5 Years Change",
					 "Sell 1 Month Price", "Sell 6 Months Price",
					 "Sell 1 Year Price", "Sell 5 Years Price"
					 ]
	numeric_columns = ["Change on Buy Date", "Buy Price", "Sell 1 Month Change", "Sell 6 Months Change",
					"Sell 1 Year Change", "Sell 5 Years Change", "Sell 1 Month Price", "Sell 6 Months Price",
					"Sell 1 Year Price", "Sell 5 Years Price"
					]
	import Statistics
	stock_stats = Statistics.Statistics(column_names)

	row_count = 0
	for sheet_num in range(0, (len(sold_stocks) / 1048000) + 1):
		csv_filename = os.path.join(new_dir, "stock_sales_"+str(sheet_num)+".csv")
		logger.info("Writing to CSV: "+csv_filename+". Number "+str(sheet_num + 1)+" of "+str((len(sold_stocks) / 1048000)+1))
		with open(csv_filename, "wb") as csvF:
			writer = csv.writer(csvF)
			writer.writerow(column_names)

			count = 0
			for stock in sold_stocks:
				if count < row_count:
					count += 1
					continue
				if count > 1048000 * (sheet_num + 1):
					break
				row_data = [stock["symbol"], stock["buy_date"], stock["buy_change"], stock["buy_rank"], stock["buy_price"],
							 percent_change(stock["buy_price"], stock["sell_month"]),
							 percent_change(stock["buy_price"], stock["sell_6_months"]),
							 percent_change(stock["buy_price"], stock["sell_year"]),
							 percent_change(stock["buy_price"], stock["sell_5_years"]),
							 stock["sell_month"], stock["sell_6_months"], stock["sell_year"], stock["sell_5_years"]
							 ]
				writer.writerow(row_data)
				stock_stats.add_data_multi(numeric_columns, [stock["buy_change"], stock["buy_price"],
							 percent_change(stock["buy_price"], stock["sell_month"]),
							 percent_change(stock["buy_price"], stock["sell_6_months"]),
							 percent_change(stock["buy_price"], stock["sell_year"]),
							 percent_change(stock["buy_price"], stock["sell_5_years"]),
							 stock["sell_month"], stock["sell_6_months"], stock["sell_year"], stock["sell_5_years"]
							 ])
				count += 1
				row_count += 1

	for name in numeric_columns:
		print(name+" :\t%s" % stock_stats.get_stats(name))


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)
if __name__ == '__main__':
	if not os.path.isfile("sold_stocks.pkl"):
		parser = argparse.ArgumentParser(description='Process Stock Data')
		parser.add_argument('-d', '--directory', type=str, nargs=1, help='Directory containing csv files of stock data')
		parser.add_argument('-df', '--csv_date_format', type=str, nargs='+', help='Python string format for date')
		parser.add_argument('-oc', '--open_column', type=int, nargs=1, help='Zero-indexed CSV column for the open price')
		parser.add_argument('-cc', '--close_column', type=int, nargs=1, help='Zero-indexed CSV column for the close price')
		parser.add_argument('-dc', '--date_column', type=int, nargs=1, help='Zero-indexed CSV column for the date')
		parser.add_argument('-n', '--num_to_buy', type=int, nargs=1, help='Number of stocks to buy per day')

		args = parser.parse_args()
		data_dir = "data"
		date_fmt = '%Y-%m-%d'
		date_column = 0
		open_column = 1
		close_column = 4
		num_to_buy = 100

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
		if args.num_to_buy:
			num_to_buy = args.num_to_buy[0]

		generate_sold_stocks(data_dir, date_fmt, (date_column, open_column, close_column), num_to_buy)
	else:
		analyze_trades()
