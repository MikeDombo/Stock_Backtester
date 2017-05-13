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

import logging
import argparse
import sys
from StockAnalysis import StockAnalysis
from StockProcessing import StockProcessing
from booleano.parser import SymbolTable, Bind

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
	                                     ],
	                                     SymbolTable("today", []),
	                                     SymbolTable("days_of_history", []),
	                                     SymbolTable("day_of_week", []),
	                                     SymbolTable("month", [])
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

	sp = StockProcessing(data_dir, date_fmt, (date_column, open_column, close_column))
	sp.generate_sold_stocks()
	sp.buy_stocks(buy_parser, sell_parser)

	sa = StockAnalysis(sp.order_history, sp.owned_stocks, sp.dates_arr, sp.date_keyed, buy_conditions, sell_conditions)
	sa.analyze_trades("output")

	import os
	import psutil
	p = psutil.Process(os.getpid())
	print("Execution took %s seconds" % p.cpu_times().user)
