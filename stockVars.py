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

from booleano.operations import Variable, ArrayVariable


class StockPrice(ArrayVariable):
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
		if self.index == 0:
			return float(context['stock']['price'])
		else:
			return float(context['stock']["data"].get(self.index)['price'])


class StockOpenPrice(ArrayVariable):
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
		if self.index == 0:
			return float(context['stock']['open_price'])
		else:
			return float(context['stock']["data"].get(self.index)['open_price'])


class StockClosePrice(ArrayVariable):
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
		if self.index == 0:
			return float(context['stock']['close_price'])
		else:
			return float(context['stock']["data"].get(self.index)['close_price'])


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


class StockIncreaseRank(ArrayVariable):
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
		if self.index == 0:
			return int(context['stock']['increase_rank'])
		else:
			return int(context['stock']["data"].get(self.index)['increase_rank'])


class StockDecreaseRank(ArrayVariable):
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
		if self.index == 0:
			return int(context['stock']['decrease_rank'])
		else:
			return int(context['stock']["data"].get(self.index)['decrease_rank'])


class StockPercChange(ArrayVariable):
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
		if self.index == 0:
			return float(context['stock']['change_percent'])
		else:
			return float(context['stock']["data"].get(self.index)['change_percent'])


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


class DateDaysOfHistory(Variable):
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
		return int(context['date']['days_of_history'])
