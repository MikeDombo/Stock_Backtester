# Copyright (c) 2017 by Michael Dombrowski <http://MikeDombrowski.com/>.
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


class Statistics(object):

	def __init__(self, stat_list=()):
		self.__stats = {}
		for n in stat_list:
			self.__stats[n] = {'min': None, 'max': None, 'count': 0, 'mean': None, 'values': [], 'sum': 0}

	def add_data(self, name, data):
		if data is None:
			return

		c_data = self.__stats[name]

		c_data['sum'] += data
		c_data['values'].append(data)
		c_data['count'] += 1

		if c_data['min'] is None:
			c_data['min'] = data
		elif data < c_data['min']:
			c_data['min'] = data
		if c_data['max'] is None:
			c_data['max'] = data
		elif data > c_data['max']:
			c_data['max'] = data
		if c_data['mean'] is None:
			c_data['mean'] = data
		else:
			c_data['mean'] = c_data['sum'] / float(c_data['count'])

	def add_data_multi(self, names, datas):
		assert len(names) == len(datas)
		for i, name in enumerate(names):
			self.add_data(name, datas[i])

	def __calc_stddev(self, name):
		numerator = 0
		for x in self.__stats[name]['values']:
			numerator += (x - self.__stats[name]['mean']) ** 2
		variance = numerator / (self.__stats[name]['count'] - 1)
		import math
		return math.sqrt(variance)

	def get_stats(self, name):
		self.__stats[name]["stddev"] = self.__calc_stddev(name)
		stat = self.__stats[name].copy()
		stat.pop('values')
		return stat

	def get_values(self, name):
		return self.__stats[name]["values"]
