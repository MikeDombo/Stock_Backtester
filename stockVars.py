from booleano.operations import Variable
from booleano.operations.operands.constants import ArithmeticVariable


class StockPrice(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual_price = float(context['stock']['price'])
		expected_price = float(value)
		return actual_price == expected_price

	def greater_than(self, value, context):
		actual_price = float(context['stock']['price'])
		expected_price = float(value)
		return actual_price > expected_price

	def less_than(self, value, context):
		actual_price = float(context['stock']['price'])
		expected_price = float(value)
		return actual_price < expected_price

	def to_python(self, context):
		return float(context['stock']['price'])


class StockSymbol(Variable):
	operations = {"equality", "membership"}

	def equals(self, value, context):
		actual_symbol = context['stock']['symbol'].lower()
		expected_symbol = value.lower()
		return actual_symbol == expected_symbol

	def belongs_to(self, value, context):
		print(context['stock']["symbol"])
		return context['stock']["symbol"] in value

	def is_subset(self, value, context):
		return value.issubset(context['stock']["symbol"])

	def to_python(self, context):
		return str(context['stock']["symbol"])
