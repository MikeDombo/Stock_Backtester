import sys
import argparse
import os
from booleano.parser import SymbolTable, Bind

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Boolean Parse')
	parser.add_argument('-b', '--buy_conditions', type=str, nargs='+', help='')
	args = parser.parse_args()
	buy_conditions = args.buy_conditions[0]

	import stockVars

	stock_symbol_var = stockVars.StockSymbol()

	root_table = SymbolTable("root",
		 (
			 Bind("stock", stock_symbol_var),
			 Bind("date", stock_symbol_var),
		 ),
		 SymbolTable("stock",
			 (
				 Bind("symbol", stock_symbol_var),
				 Bind("price", stockVars.StockPrice()),
			 )
			 ),
		 SymbolTable("date",
		             (
		                 Bind("symbol", stock_symbol_var),
		                 Bind("price", stockVars.StockPrice()),
		             )
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
	stocks = ({'stock': {'symbol': 'usa', 'price': '100.5'}}, {'stock':{'symbol': 'uda', 'price': '110.5'}})
	print(p(stocks[0]))
	print(p(stocks[1]))
