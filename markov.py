from timeit import default_timer
from string import punctuation
from os import listdir
import re
markovs = {}
def purify_word(word):
	''' Remove punctuation, trailing whitespace, and lower a string
	* http://stackoverflow.com/a/266162/3466576 '''
	return re.compile('[%s]' % re.escape(punctuation)).sub(
	'', word).lower().strip()
def purify_list(l):
	''' Purify the words of a list and add periods to ending word '''
	for i, line in enumerate(l):
		l[i] = list(map(purify_word, line.split()))
		if l[i]: l[i][-1] += '.' # Add period to sentance ends
def read_file(file_name):
	''' Read a file and split into a list of sentances
	* http://stackoverflow.com/a/13184791/3466576 '''
	delim = ('.', '?', '!')
	pattern = '|'.join(map(re.escape, delim))
	with open("samples/" + file_name, errors="ignore") as f:
		text = f.read()
		words = re.split(pattern, text)
	purify_list(words)
	print("%s read." % file_name)
	return words
def find_chains(word_list):
	''' Find chains in list of lists of sentances '''
	global markovs
	for line in word_list:
		if len(line) >= 3:
			for i, word in enumerate(line[:-2]):
				markovs[(word, line[i+1])] = markovs.get(
				(word, line[i+1]), []) + [line[i+2]]
	print("Markoved")
def write_dictionary(d, name="markovs.txt"):
	''' Write dictionary of markovs in readable format:
	* File Format: double|third word chances seperated by ','
	* word1,word2|words,which,follow,this,pair,of,words '''
	with open(name, 'w') as f:
		for k,v in d.items():
			f.write("{},{}|{}\n".format(k[0], k[1], ','.join(v)))
if __name__ == '__main__':
	start = default_timer()
	samples = listdir("samples")
	lines = 0
	for f in samples:
		w = read_file(f)
		lines += len(w)
		find_chains(w)
	write_dictionary(markovs)
	print("Run time for %s sentances: %s" % (lines, default_timer() - start))
