# MagPie Core
from string import punctuation
from random import choice
import re
def purify_word(word):
	''' Remove punctuation, trailing whitespace, and lower a string '''
	return re.compile('[%s]' % re.escape(punctuation)).sub(
	'', word).lower().strip()
def talk_to_eachother(bot1, bot2, learn=False, limit=1000):
	''' Make two Magpie objects speak to each other
	* Make bot talk to itself by providing it as both parameters
	* limit is integer of how many dialogues before exit
	* learn is if bots will add to their markov data
	* returns log of conversation '''
	bot1_output = "Hello there %s" % bot2.name
	bot1.outputs.append(bot1_output)
	for i in range(limit-1):
		bot2.inputs.append(bot1_output)
		if learn: bot2.add_to_markovs(bot1_output)
		bot2_output = bot2.create_chain(bot1_output)
		bot2.outputs.append(bot2_output)
		print("%s: %s" % (bot2.name, bot2_output))
		bot1.inputs.append(bot2_output)
		if learn: bot1.add_to_markovs(bot2_output)
		bot1_output = bot1.create_chain(bot2_output)
		bot1.outputs.append(bot1_output)
		print("%s: %s" % (bot1.name, bot1_output))
	return '\n'.join(["{}: {}\n{}: {}".format(
	bot1.name, o, bot2.name, i) for o,i in zip(bot1.outputs, bot1.inputs)])

class Magpie():
	''' Chat Bot using Markov Chains and Keyword responses '''
	def __init__(self, name="Magpie", use_keywords=False, default="Error"):
		''' * name: name of bot to appear in dialogue
			* use_keywords: whether or not a bot will respond to its known keywords
			* default: bot's response in case of an error '''
		self.name = name
		self.use_keywords = use_keywords
		self.default = default
		self.life = True
		self.log = "Hi my name is %s.\n" % self.name
		self.triples = {}
		self.keywords = {}
		self.keyword_outputs = []
		self.inputs = []
		self.outputs = []
	def chat_loop(self, limit=None):
		''' Loop of chat dialogue; blank line ends dialogue 
		* limit is number of accepted input before termination '''
		user_input = input("Hi my name is %s.\nUser: " % self.name)
		self.handle_input(user_input)
		if limit:
			for i in range(limit-1):
				user_input = input("User: ")
				self.handle_input(user_input)
		else:
			while self.life and user_input:
				user_input = input("User: ")
				self.handle_input(user_input)
		print("Thanks for seeing me.")
		self.life = False
	def handle_input(self, text):
		''' Handle input of User '''
		if text == '':
			return
		self.inputs.append(text)
		self.respond(text)
		self.add_to_markovs(text) # Respond first to avoid copying input
	def respond(self, text):
		''' Respond to input by checking for keywords then moving to chains '''
		words = map(purify_word, text.split())
		if self.use_keywords:
			for word in words:
				if word in self.keywords:
					output = self.key(word)
					# output = self.keywords[word]
					break
			else: # ikr who knew for loops could use else
				output = self.create_chain(text)
		else:
			output = self.create_chain
		print("%s: %s" % (self.name, output))
		self.outputs.append(output)
		self.log += "User: {}\n{}: {}\n".format(
		text, self.name, output)
		return output
	def create_chain(self, text):
		''' Create chain by: 
		* Choosing random double from input
			* If a valid double isnt found - choose random single
		* Build off double until a closing punctuation is found '''
		words = [purify_word(word) for word in text.split()]
		doubles = [(word, words[i+1]) for i,word in enumerate(words[:-1])] # doubles in sentance
		for d in doubles:
			pair = choice(doubles)
			doubles.remove(pair)
			if pair in self.triples:
				break
		else: # If none of the doubles can, create a chain with only one word
			word = choice(words)
			for k in self.triples.keys():
				if word == k[0]:
					pair = (word, k[1])
					break
				elif word == k[1]:
					pair = (k[0], word)
					break
			else: # If no pair can be found with one word return error
				return self.default
		response = [w for w in pair]
		while not any((i in response[-1] for i in ['.','!','?'])):
			try:
				triple_word = choice(self.triples[pair])
				response.append(triple_word)
				pair = (pair[-1], triple_word)
			except KeyError:
				break
		return ' '.join(response)
	def read_keywords(self, lines):
		''' Read keywords file for keywords and their response
		File Format: keywords seperated by ',' | response
		key1,key2,key3,etc|What can you tell me about etc? '''
		for index, line in enumerate(lines):
			parts = line.split('|')
			#out = parts[-1].strip()
			self.keyword_outputs.append(parts[-1].strip())
			for word in parts[0].split(','):
				self.keywords[word.lower()] = index
				#self.keywords[word.lower()] = out
	def read_markovs(self, lines):
		''' Read Markov Chain data file
		* About 20 times faster than creating triples over again
		File Format: double|third word chances seperated by ','
		word1,word2|words,which,follow,this,pair,of,words '''
		for line in lines:
			parts = line.split('|')
			words = tuple(parts[0].split(','))
			results = parts[-1].strip().split(',')
			self.triples[words] = results
	def add_to_markovs(self, text):
		''' Read a line of text and add to triple data
		* The more bots contributing to this data the better responses '''
		line = [purify_word(word) for word in text.split()]
		if len(line) >= 3:
			for i, word in enumerate(line[:-2]):
				self.triples[(word, line[i+1])] = self.keywords.get(
				(word, line[i+1]), []) + [line[i+2]]
	def key(self, word):
		''' Simple key function for conciseness '''
		return self.keyword_outputs[self.keywords[word]]
	def save_log(self, file_name="chatlog.txt"):
		''' Save the log of the conversation to a .txt file
		* file_name is name of file '''
		with open("chatlog.txt", 'w') as l:
			l.write(self.log)
	def save_markovs(self, name="markovs.txt"):
		''' Save Markov data in readable file format
		* name is name of file '''
		with open(name, 'w') as f:
			for k,v in self.triples.items():
				f.write("{},{}|{}\n".format(k[0], k[1], ','.join(v)))
if __name__ == '__main__':
	m = Magpie()
	#n = Magpie(name="Nagpie")
	with open("keywords.txt") as k:
		keys = k.readlines()
		m.read_keywords(keys)
		#n.read_keywords(keys)
	with open("markovs.txt",encoding='ascii', errors='ignore') as marks:
		chains = marks.readlines()
		m.read_markovs(chains)
		#n.read_markovs(chains)
	#with open("RobotChat.txt", 'w') as l:
	#	l.write(talk_to_eachother(m,m,True,1000))
	m.chat_loop()
	m.save_log()
