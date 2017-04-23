import urllib2
import time
import random
import os
import sys
import getopt

baseURL = "https://ichart.finance.yahoo.com/table.csv?g=d&s="


def download_symbol_history(download_directory, symbol):
	try:
		u = urllib2.urlopen(baseURL+symbol)
		if not os.path.exists(download_directory):
			os.makedirs(download_directory)
		file = open(download_directory+"/table_"+symbol+".csv", 'wb')
		file.write(u.read())
		file.close()
		return True
	except urllib2.HTTPError as e:
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
