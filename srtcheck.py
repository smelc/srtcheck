#!/usr/bin/python3.1

# Licence: Do whatever you want with that.

# TODO : check that times are increasing ? -> should be a warning, not an error
# since it looks like it occurs to have overlapping subtitles

import sys
import re

warnings_encountered = False

def print_warning_or_error(msg,typemsg,lineno) :
	print("File "+filename+": "+typemsg+", on line "+str(lineno)+", "+msg)

def print_warning(msg,lineno) :
	print_warning_or_error(msg,"Warning",lineno)
	warnings_encountered = True

def print_error(msg,lineno) :
	print_warning_or_error(msg,"Error",lineno)

""" Check if str(str_input) is equal to expected_integer """
""" Print a warning if this not the case. Pure method otherwise. """
""" Return int(str_input)-expected_integer """
""" Exit the program if an error is discovered. """
def checkcounter(str_input,expected_integer,lineno) :
	try:
		if(int(str_input) != expected_integer) :
			print_warning("I've found subtitle number "+str(str_input)+" while I was expecting subtitle number "+str(expected_integer)+".",lineno)
	except ValueError:
		print_error("unexpected input : is a subtitle number missing (I was expecting #"+str(expected_integer)+") ?",lineno)
		sys.exit(3)

arrowpattern = re.compile('^\s*(\S*)\s*-->\s*(\S*)\s*$') # \s is space, \S is not-space

""" check if str_input has the form nn:nn:nn,nnn --> nn:nn:nn,nnn where n should be digits"""
""" return if str_input is correct. Exit the program otherwise. """
def checkduration(str_input,lineno) :
	# Debugging purposes
	if verbose :
		print("Checking line "+str(lineno)+".")
		print(str_input)
	# /Debug
	result = arrowpattern.match(str_input) # there will be 2 groups afterwards if it matches
	# This is specific to python 3.1 (does not work in 3.3 for example). See the standard library on re to change that
	if(result != None):
		check_time(result.group(1),"left",lineno)
		check_time(result.group(2),"right",lineno)
		# TODO check that left < right
	else:
		print_error("invalid syntax: regular expression (.*) --> (.*) did not match.",lineno)
		print(str_input)
		sys.exit(3)

deuxpointspattern = re.compile('^(\d{2}):(\d{2}):(\d{2}),(\d{3})$')

""" check if str_input has the form nn:nn:nn,nnn where n should be digits"""
""" input: side indicates if we are on the left or right of a '-->' """
""" output: return if str_input is correct. Exit the program otherwise. """
def check_time(str_input,side,lineno) :
	result = deuxpointspattern.match(str_input)	
	if(result != None):
		un = result.group(1)
		deux = result.group(2)
		trois = result.group(3)
		quatre = result.group(4)
		if(un == None or deux == None or trois == None or quatre == None) :
			print_error("invalid syntax.",lineno) # can it be reached ?
			sys.exit(3)
	else:
		print_error("invalid syntax: regular expression nn:nn:nn,nnn did not match.",lineno)
		sys.exit(3)
#	result = deuxpointspattern.groups() # there are 4 groups afterwards if if matched
#	if(len(result)!=4):
#		sys.exit(-1)

""" input: lineno is the number of lines read so far """
""" output: return False if eof is reached """
""" output: return the line number of the first blank line otherwise """
def eat_non_blanklines_followed_by_one_blank_line(filehandler,lineno) :
	string = filehandler.readline()
	lineno+=1
	while(string!="\n" and not string=="") : # while line is not blank (i.e. it is a newline or an empty line (the last one without \n)) 
		# Debugging purposes
		if verbose :
			print("Checking line "+str(lineno)+".")
			print(string)
		string = filehandler.readline()
		lineno+=1
	if string == "":
		return False
	else:
		return lineno

""" Check syntax of subtitle file 'filename'. The file is decoded according to encoding 'desired_encoding'. """
def checkfile(filename,desired_encoding) :
	filehandler = open(filename, 'r',encoding=desired_encoding)
	# see http://diveintopython3.org/files.html for more about the encoding
	result = True
	number_of_sub_so_far = 0
	lineno = 0 # number of lines read so far
	global retry
	while(result) :
		# main loop
		str_input = filehandler.readline()
		if(str_input == "") : # eof was reached
			result = False
		else:
			lineno+=1
			res=checkcounter(str_input,number_of_sub_so_far+1,lineno) # verify subtitle number
			number_of_sub_so_far+=1
			try:
				str_input = filehandler.readline()
			except UnicodeDecodeError:
				print("Catched decoding error when reading "+filename+" supposing it was encoded in "+desired_encoding+".")
				if not retry :
					print("Retrying with encoding iso-8859-1.")
					retry = True
					filehandler.close()
					checkfile(filename,"iso-8859-1")
				else :
					print("Exiting.")
					sys.exit(4)
			if(str_input == "") : # eof was reached
				result = False
			else:
				lineno+=1
				checkduration(str_input,lineno) # verify nn:nn:nn,nnn --> nn:nn:nn,nnn line
				result=eat_non_blanklines_followed_by_one_blank_line(filehandler,lineno) # skip subtitle text
				# Remark: the blank line in-between subtitle n-1 and subtitle n is eaten by the previous method call
				# at this point, result is either False (eof was reached) or it is an integer (the number of lines checked so far)
				lineno = result

# entry point of main
if len(sys.argv) <= 1 :
	print("I need at least one argument. Exiting.")
	sys.exit(1)

l = list(filter(lambda x : x == "-v" or x == "--verbose",sys.argv[1:]))
verbose = len(l) >= 1

for filename in filter(lambda x : x!="--help" and x != "-h" and x != "-v" and x != "--verbose",sys.argv[1:]) :
	retry = False
	checkfile(filename,"latin1")	

if warnings_encountered:
	sys.exit(2)
else:
	sys.exit(0)
