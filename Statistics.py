
class Statistics(object):
	__stats = {}

	def __init__(self, stat_list=()):
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
		stat = self.__stats[name]
		stat.pop('values')
		return stat