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

try:
	# For Python 3.0 and later
	from urllib.request import urlopen, HTTPError
except ImportError:
	# Fall back to Python 2's urllib2
	from urllib2 import urlopen, HTTPError
import time
import random
import os
import sys
import getopt

baseURL = "https://ichart.finance.yahoo.com/table.csv?g=d&s="


def download_symbol_history(download_directory, symbol):
	try:
		u = urlopen(baseURL+symbol)
		if not os.path.exists(download_directory):
			os.makedirs(download_directory)
		file = open(download_directory+"/table_"+symbol+".csv", 'wb')
		file.write(u.read())
		file.close()
		return True
	except HTTPError as e:
		if e.code == 404:
			print("Could not find data for symbol: "+symbol)
			return False
		else:
			print(e)
			return False


def main(argv):
	file_name = "symbol_list.txt"
	try:
		opts, args = getopt.getopt(argv[1:], "hf:", ["help", "file="])
	except getopt.GetoptError:
		print(argv[0]+" -f <input filename>")
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(argv[0]+" -f <input filename>")
			sys.exit()
		elif opt in ('-f', '--file'):
			file_name = arg
	rand = random.Random()
	if not os.path.isfile(file_name):
		print("Error: File "+str(file_name)+" could not be found.")
		sys.exit(2)
	with open(file_name) as f:
		num_lines = line_count(file_name)
		for i, symbol in enumerate(f):
			symbol = symbol.strip()
			print("Downloading "+symbol+" "+str(i+1)+" of "+str(num_lines))
			if os.path.isfile("data/"+"table_"+symbol+".csv"):
				print("\tSkipping already downloaded")
			else:
				if download_symbol_history("data", symbol):
					time.sleep(rand.uniform(0.0, 3.6))


def line_count(file):
	return sum(1 for line in open(file))

if __name__ == '__main__':
	main(sys.argv)
