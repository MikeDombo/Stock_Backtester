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


def generate_sold_stocks(data_dir, date_fmt, columns):
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
		symbol_keyed = None
		logger.info("Done pivoting data")
		logger.info("Dumping pivoted data to pickle")

		pickle.dump(date_keyed, open("date_keyed.pkl", "wb"))
		logger.info("Done pickling")
		bought_stocks = find_bought_stocks(date_keyed)
	else:
		logger.info("Loading pickled data")
		date_keyed = pickle.load(open("date_keyed.pkl", "rb"))
		logger.info("Done loading pickled data")
		bought_stocks = find_bought_stocks(date_keyed)

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
		if date_plus_month is not False:
			if symbol in date_keyed[date_plus_month]:
				sell_order["sell_month"] = date_keyed[date_plus_month][symbol]["close"]
		if date_plus_6_months is not False:
			if symbol in date_keyed[date_plus_6_months]:
				sell_order["sell_6_months"] = date_keyed[date_plus_6_months][symbol]["close"]
		if date_plus_year is not False:
			if symbol in date_keyed[date_plus_year]:
				sell_order["sell_year"] = date_keyed[date_plus_year][symbol]["close"]
		if date_plus_5_years is not False:
			if symbol in date_keyed[date_plus_5_years]:
				sell_order["sell_5_years"] = date_keyed[date_plus_5_years][symbol]["close"]
		sold_stocks += [sell_order]

	logger.info("Done finding P&L")
	logger.info("Pickling sold stocks")
	pickle.dump(sold_stocks, open("sold_stocks.pkl", "wb"))
	logger.info("Done pickling sold stocks")
	analyze_trades(sold_stocks)


def market_day(date, market_data_days):
	if date in market_data_days:
		return date
	if date > max(market_data_days):
		return False

	for i in range(-1, 5):
		if date + relativedelta(days=i) in market_data_days:
			return date + relativedelta(days=i)

	return False


def find_bought_stocks(date_keyed):
	if not os.path.isfile("bought_stocks.pkl") and date_keyed is not None:
		bought_stocks = []
		logger.info("Finding daily losers")
		for date, symbol_data in date_keyed.items():
			a = find_biggest_losers(symbol_data)
			for symbol, rank in a:
				bought_stocks += [{'symbol': symbol, 'price': symbol_data[symbol]['close'],
								   'change': symbol_data[symbol]['change'], 'day': date, 'rank': rank}]

		logger.info("Dumping bought stock data to pickle")
		pickle.dump(bought_stocks, open("bought_stocks.pkl", "wb"))
		logger.info("Done pickling")
		return bought_stocks
	else:
		logger.info("Loading pickled bought stocks")
		p = pickle.load(open("bought_stocks.pkl", "rb"))
		logger.info("Done loading pickled bought stocks")
		return p


def find_biggest_losers(d):
	minheap = []
	for symbol, data in d.items():
		heapq.heappush(minheap, (data["change"], symbol))

	length = 10000
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

	row_count = 0
	for sheet_num in range(0, (len(sold_stocks) / 1048000)+1):
		logger.info("Writing to CSV: "+"stock_sales_"+str(sheet_num)+".csv"+". Number "+str(sheet_num + 1)+" of "+str((len(sold_stocks) / 1048000)+1))
		with open("stock_sales_"+str(sheet_num)+".csv", "wb") as csvF:
			writer = csv.writer(csvF)
			writer.writerow(["Symbol", "Buy Date", "Change on Buy Date", "Rank", "Buy Price",
							 "Sell 1 Month Change", "Sell 6 Months Change",
							 "Sell 1 Year Change", "Sell 5 Years Change",
							 "Sell 1 Month Price", "Sell 6 Months Price",
							 "Sell 1 Year Price", "Sell 5 Years Price"
							 ])

			count = 0
			for i,stock in enumerate(sold_stocks):
				if count < row_count:
					count += 1
					continue
				if count > 1048000 * (sheet_num + 1):
					break
				writer.writerow([stock["symbol"], stock["buy_date"], stock["buy_change"], stock["buy_rank"], stock["buy_price"],
								 percent_change(stock["buy_price"], stock["sell_month"]),
								 percent_change(stock["buy_price"], stock["sell_6_months"]),
								 percent_change(stock["buy_price"], stock["sell_year"]),
								 percent_change(stock["buy_price"], stock["sell_5_years"]),
								 stock["sell_month"], stock["sell_6_months"], stock["sell_year"], stock["sell_5_years"]
								 ])
				count += 1
				row_count += 1


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

		generate_sold_stocks(data_dir, date_fmt, (date_column, open_column, close_column))
	else:
		analyze_trades()
