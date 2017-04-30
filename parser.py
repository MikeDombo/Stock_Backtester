import argparse
from booleano.parser import SymbolTable, Bind

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Boolean Parse')
	parser.add_argument('-b', '--buy_conditions', type=str, nargs='+', help='')
	args = parser.parse_args()
	buy_conditions = args.buy_conditions[0]

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
	p = parse_manager.parse(buy_conditions)
	print(p)
	stocks = ({'stock': {'symbol': 'usa', 'price': '100.5'}}, {'stock': {'symbol': 'uda', 'price': '110'}})
	print(p(stocks[0]))
	print(p(stocks[1]))
