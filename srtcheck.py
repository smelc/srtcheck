#!/usr/bin/python3.1

# Licence: do whatever you want with that.

# TODO : check that times are increasing

import sys
import re

warnings_encountered = False

def print_warning_or_error(msg,typemsg,lineno) :
	print("File "+filename+": "+typemsg+", on line "+str(lineno)+" "+msg)

def print_warning(msg,lineno) :
	print_warning_or_error(msg,"Warning",lineno)
	warnings_encountered = True

def print_error(msg,lineno) :
	print_warning_or_error(msg,"Error",lineno)

""" Check if str(str_input) is equal to expected_integer """
""" Print a warning if this not the case. Pure method otherwise. """
def checkcounter(str_input,expected_integer,lineno) :
	if(int(str_input) != expected_integer) :
		print_warning("I've found subtitle number "+str(str_input)+" while I was exepecting subtitle number "+str(expected_integer)+".",lineno)

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
	while(string!="\n") : # if line is not empty or
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

""" Check syntax of subtitle file 'filename' """
def checkfile(filename) :
	filehandler = open(filename, 'r') # default encoding used here *** take care... *** This works for file encoded 
					  # in iso-8859-15 even if the local encoding is utf-8.
	# see http://diveintopython3.org/files.html for more about the encoding
	result = True
	number_of_sub_so_far = 0
	lineno = 0 # number of lines read so far
	while(result) :
		# main loop
		str_input = filehandler.readline()
		if(str_input == "") : # eof was reached
			result = False
		else:
			lineno+=1
			checkcounter(str_input,number_of_sub_so_far+1,lineno) # verify subtitle number
			number_of_sub_so_far+=1
			str_input = filehandler.readline()
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
	checkfile(filename)	

if warnings_encountered:
	sys.exit(2)
else:
	sys.exit(0)
