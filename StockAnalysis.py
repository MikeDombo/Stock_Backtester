class StockAnalysis(object):
	def __init__(self, order_history, owned_stocks, dates_arr, date_keyed, buy_conditions, sell_conditions):
		self.order_history = order_history
		self.owned_stocks = owned_stocks
		self.dates_arr = dates_arr
		self.date_keyed = date_keyed
		self.buy_conditions = buy_conditions
		self.sell_conditions = sell_conditions

	def analyze_trades(self, output_dir):
		import datetime
		import os
		from StockProcessing import StockProcessing

		# Make directories to store CSVs
		curr_date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		new_dir = os.path.join(output_dir, curr_date)
		directory_num = 1
		while os.path.isdir(new_dir):
			new_dir = os.path.join(output_dir, curr_date + "_" + str(directory_num))
			directory_num += 1
		os.makedirs(new_dir)

		with open(os.path.join(new_dir, "generator_options.txt"), "w") as text_file:
			text_file.write("Buy Conditions: %s \r\n" % self.buy_conditions)
			text_file.write("Sell Conditions: %s \r\n" % self.sell_conditions)

		column_names = ["Buy Date", "Symbol", "Buy Price", "Sell Date", "Sell Price", "% Change"]
		numeric_columns = ["Buy Price", "Sell Price", "% Change"]

		column_data = []
		numeric_data = []
		for symbol, trades in self.order_history.items():
			trades = sorted(trades, key=lambda k: k['date'])
			for trade_num, trade in enumerate(trades):
				if trade["type"] == "sell":
					column_data.append([trades[trade_num - 1]["date"], symbol, trades[trade_num - 1]["price"],
					                    trade["date"], trade["price"],
					                    StockProcessing.percent_change(trades[trade_num - 1]["price"], trade["price"])
					                    ])
					numeric_data.append([trades[trade_num - 1]["price"], trade["price"],
					                     StockProcessing.percent_change(trades[trade_num - 1]["price"],
					                                                    trade["price"])])

		sold_stats = self.__write_to_csv_split(column_data, numeric_data, column_names, numeric_columns, "sold_stocks",
		                                       new_dir)

		print("\r\n\r\n")

		with open(os.path.join(new_dir, "analysis.txt"), "w") as analysis_text_file:
			print(str("*" * 120) + "\r\n")
			self.__print_and_write(analysis_text_file,
			                       "Analyzing Trades For Stock Data Between %s And %s" % (
			                       self.dates_arr[0], self.dates_arr[-1]))
			self.__print_and_write(analysis_text_file, "\r\n" + str("*" * 120))
			self.__print_and_write(analysis_text_file, "\r\nStocks That Were Bought And Sold\n" + str("=" * 60))
			for name in numeric_columns:
				self.__print_and_write(analysis_text_file, name + " :\t%s" % sold_stats.get_stats(name))

			column_data = []
			numeric_data = []
			last_day = self.dates_arr[-1]
			for symbol, trade in self.owned_stocks.items():
				column_dat = [trade["date"], symbol, trade["price"]]
				numeric_dat = [trade["price"]]
				if symbol in self.date_keyed[last_day]:
					symbol_last_day = self.date_keyed[last_day][symbol]
					column_dat.extend(
						[last_day, symbol_last_day["close"],
						 StockProcessing.percent_change(trade["price"], symbol_last_day["close"])])
					numeric_dat.extend(
						[symbol_last_day["close"],
						 StockProcessing.percent_change(trade["price"], symbol_last_day["close"])])
				else:
					column_dat.extend([last_day, 0, -1])
					numeric_dat.extend([0, -1])
				column_data.append(column_dat)
				numeric_data.append(numeric_dat)

			column_names = ["Buy Date", "Symbol", "Buy Price", "Would-be Sell Date", "Would-be Sell Price",
			                "Would-be % Change"]
			numeric_columns = ["Buy Price", "Would-be Sell Price", "Would-be % Change"]

			unsold_stats = self.__write_to_csv_split(column_data, numeric_data, column_names, numeric_columns,
			                                         "unsold_stocks",
			                                         new_dir)

			s = "\r\n\r\nStocks That Were Only Bought And Never Sold. (Would-be means what would happen if the stocks were " \
			    "sold on the last day, %s)\n" % last_day + str("=" * 60)
			self.__print_and_write(analysis_text_file, s)

			for name in numeric_columns:
				self.__print_and_write(analysis_text_file, name + " :\t%s" % unsold_stats.get_stats(name))

			self.__print_and_write(analysis_text_file, "\r\n\r\n" + str("*" * 100) + "\r\n")
			import locale
			locale.setlocale(locale.LC_ALL, '')

			num = float(sold_stats.get_stats("% Change")["mean"] * 100)
			self.__print_and_write(analysis_text_file,
			                       "Percent gain/loss if you bought an equal dollar amount of each stock: %s%%"
			                       % locale.format('%.4f', num, grouping=True))

			amount_spent = sold_stats.get_stats("Buy Price")["sum"]
			amount_from_sales = sold_stats.get_stats("Sell Price")["sum"]
			num = float(StockProcessing.percent_change(amount_spent, amount_from_sales) * 100)
			self.__print_and_write(analysis_text_file, "Percent gain/loss if you bought equal number of stocks: %s%%"
			                       % locale.format('%.4f', num, grouping=True))

			self.__print_and_write(analysis_text_file,
			                       "\r\nPercent gain/loss including stocks that were unsold. (Assumes they "
			                       "are sold on the last day)")

			chn = sold_stats.get_values("% Change") + unsold_stats.get_values("Would-be % Change")
			num = float((sum(chn) / len(chn)) * 100)
			self.__print_and_write(analysis_text_file,
			                       "Percent gain/loss if you bought an equal dollar amount of each stock: %s%%"
			                       % locale.format('%.4f', num, grouping=True))

			amount_spent = sold_stats.get_stats("Buy Price")["sum"] + unsold_stats.get_stats("Buy Price")["sum"]
			amount_from_sales = sold_stats.get_stats("Sell Price")["sum"] + \
			                    unsold_stats.get_stats("Would-be Sell Price")["sum"]
			num = float(StockProcessing.percent_change(amount_spent, amount_from_sales) * 100)
			self.__print_and_write(analysis_text_file, "Percent gain/loss if you bought equal number of stocks: %s%%"
			                       % locale.format('%.4f', num, grouping=True))

		print("\r\n\r\n")

	@staticmethod
	def __print_and_write(fp, s):
		print(s)
		fp.write(s + str("\r\n"))

	@staticmethod
	def __write_to_csv_split(column_data, numeric_data, column_names, numeric_columns, filename, output_dir):
		from Statistics import Statistics
		import sys
		import os
		import csv

		stock_stats = Statistics(column_names)

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
