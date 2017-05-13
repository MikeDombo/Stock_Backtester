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


class DateHist(object):
	def __init__(self, symbol, date, date_keyed, symbol_keyed):
		self.symbol = symbol
		self.date = date
		self.date_keyed = date_keyed
		self.symbol_keyed = symbol_keyed

	def get(self, index=0):
		for i, d in enumerate(self.symbol_keyed):
			if d[0] == self.date:
				break
		sd = self.symbol_keyed[i - index]
		data = self.date_keyed[sd[0]][self.symbol]

		from StockProcessing import StockProcessing

		return {"today": StockProcessing.get_unix_time_date(sd[0]), "days_of_history": data["doh"],
		        "day_of_week": sd[0].isoweekday(), "month": sd[0].month}
