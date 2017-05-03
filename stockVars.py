from booleano.operations import Variable


class StockPrice(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual < expected

	def to_python(self, context):
		return float(context['stock']['price'])


class StockOpenPrice(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual < expected

	def to_python(self, context):
		return float(context['stock']['open_price'])


class StockClosePrice(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual < expected

	def to_python(self, context):
		return float(context['stock']['close_price'])


class StockBuyPrice(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual < expected

	def to_python(self, context):
		return float(context['stock']['buy_price'])


class StockOwned(Variable):
	operations = {"boolean"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = bool(value)
		return actual == expected

	def __call__(self, context):
		return self.to_python(context)

	def to_python(self, context):
		return bool(context['stock']['owned'])


class StockIncreaseRank(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def to_python(self, context):
		return int(context['stock']['increase_rank'])


class StockDecreaseRank(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def to_python(self, context):
		return int(context['stock']['decrease_rank'])


class StockPercChange(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = float(value)
		return actual < expected

	def to_python(self, context):
		return float(context['stock']['change_percent'])


class StockSymbol(Variable):
	operations = {"equality", "membership"}

	def equals(self, value, context):
		actual_symbol = self.to_python(context).lower()
		expected_symbol = value.lower()
		return actual_symbol == expected_symbol

	def belongs_to(self, value, context):
		return self.to_python(context) in value

	def is_subset(self, value, context):
		return value.issubset(self.to_python(context))

	def to_python(self, context):
		return str(context['stock']["symbol"])


class DateBuy(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = self.__other_to_python(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = self.__other_to_python(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = self.__other_to_python(value)
		return actual < expected

	def __other_to_python(self, value):
		return value

	def to_python(self, context):
		return context["date"]["buy"]


class DateToday(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = self.__other_to_python(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = self.__other_to_python(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = self.__other_to_python(value)
		return actual < expected

	def __other_to_python(self, value):
		return value

	def to_python(self, context):
		return context["date"]["today"]


class DateDayOfWeek(Variable):
	operations = {"equality", "inequality", "membership"}

	def equals(self, value, context):
		actual_symbol = self.to_python(context)
		expected_symbol = value.lower()
		return actual_symbol == expected_symbol

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def belongs_to(self, value, context):
		return self.to_python(context) in value

	def is_subset(self, value, context):
		return value.issubset(self.to_python(context))

	def to_python(self, context):
		return int(context['date']["day_of_week"])


class DateMonth(Variable):
	operations = {"equality", "inequality", "membership"}

	def equals(self, value, context):
		actual_symbol = self.to_python(context)
		expected_symbol = value.lower()
		return actual_symbol == expected_symbol

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def belongs_to(self, value, context):
		return self.to_python(context) in value

	def is_subset(self, value, context):
		return value.issubset(self.to_python(context))

	def to_python(self, context):
		return int(context['date']["month"])


class DateDays(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def to_python(self, context):
		return int(context["date"]["days"])


class DateMonths(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def to_python(self, context):
		return int(context["date"]["months"])


class DateYears(Variable):
	operations = {"equality", "inequality"}

	def equals(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual == expected

	def greater_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual > expected

	def less_than(self, value, context):
		actual = self.to_python(context)
		expected = int(value)
		return actual < expected

	def to_python(self, context):
		return int(context["date"]["years"])
