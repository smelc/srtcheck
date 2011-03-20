#!/usr/bin/python3.1

# Licence: Do whatever you want with that.

# TODO : check that times are increasing ? -> should be a warning, not an error
# since it looks like it occurs to have overlapping subtitles

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-v", "--verbose", help="print the lines being checked", default=False, dest="verbose",action="store_true")
parser.add_option("-t", "--try-encoding", help="try the given encoding to read files if default fails. --try-encoding can be given multiple times", type="string", dest="encoding_to_try", action="append",default=[])
parser.add_option("-o", "--only-encoding", help="only use the given encoding to read files", type="string", dest="only_encoding", action="store",default=None)

(options, args) = parser.parse_args()

import sys
import re

warnings_encountered = False

def print_warning_or_error(msg,typemsg,lineno) :
	if numberoffiles == 1 :
		print(typemsg+", on line "+str(lineno)+", "+msg)
	else :
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
	if options.verbose :
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

""" input: lineno is the number of lines read so far """
""" output: return False if eof is reached """
""" output: return the line number of the first blank line otherwise """
def eat_non_blanklines_followed_by_one_blank_line(lineno,desired_encoding) :
	global filehandler
	str_input = filehandler.readline()
	lineno+=1
	while(str_input!="\n" and not str_input=="") : # while line is not blank (i.e. it is a newline or an empty line (the last one without \n)) 
		# Debugging purposes
		if options.verbose :
			print("Checking line "+str(lineno)+".")
			print(str_input)
		str_input = filehandler.readline()
		lineno+=1
	if str_input == "":
		return False
	else:
		return lineno

def treat_decoding_error(desired_encoding) :
	global encodings_left_to_try,filename,filehandler
	if numberoffiles > 1 :
		print("Catched decoding error when reading "+filename+" supposing it was encoded in "+desired_encoding+".")
	else:
		print("Catched decoding error when reading the file supposing it was encoded in "+desired_encoding+".")

	if len(encodings_left_to_try) > 0:
		ec_to_try = encodings_left_to_try[0]
		encodings_left_to_try = encodings_left_to_try[1:]
		print("Retrying with encoding "+ec_to_try+".")
		filehandler.close()
		checkfile(ec_to_try)
	else :
		if(options.only_encoding!=None):
			print("Because you used --only-encoding, I have no more encoding to try.")
		else:
			print("I have no more encoding to try.")
			print("Did you specify one with --try-encoding ?")
		print("Exiting.")
		sys.exit(4)

""" Check syntax of subtitle file 'filename'. The file is decoded according to encoding 'desired_encoding'. """
def checkfile(desired_encoding) :
	global filename,filehandler
	filehandler = open(filename, 'r',encoding=desired_encoding)
	# see http://diveintopython3.org/files.html for more about the encoding
	result = True
	number_of_sub_so_far = 0
	lineno = 0 # number of lines read so far
	global encodings_left_to_try
	while(result) :
		# main loop
		str_input = filehandler.readline() 
		if(str_input == "") : # eof was reached
			result = False
		else:
			lineno+=1
			res=checkcounter(str_input,number_of_sub_so_far+1,lineno) # verify subtitle number
			number_of_sub_so_far+=1
			str_input = filehandler.readline()
			if(str_input == "") : # eof was reached
				result = False
			else:
				lineno+=1
				checkduration(str_input,lineno) # verify nn:nn:nn,nnn --> nn:nn:nn,nnn line
				result=eat_non_blanklines_followed_by_one_blank_line(lineno,desired_encoding) # skip subtitle text
				# Remark: the blank line in-between subtitle n-1 and subtitle n is eaten by the previous method call
				# at this point, result is either False (eof was reached) or it is an integer (the number of lines checked so far)
				lineno = result

# entry point of main

# sanity checks
if len(sys.argv) <= 1 :
	print("I need at least one argument. Exiting.")
	sys.exit(1)

if options.only_encoding != None and options.encoding_to_try != []:
	print("Error: options --try-encoding and --only-encoding are incompatible!")
	print("Exiting.")
	sys.exit(5)
# /sanity checks

# global variable
filehandler=None
numberoffiles=len(args)

for filename in args:
	encodings_left_to_try = options.encoding_to_try
	if options.only_encoding != None:
		desired_encoding = options.only_encoding
	else:
		desired_encoding = sys.getdefaultencoding()
	try:
		checkfile(desired_encoding)
	except UnicodeDecodeError:
		treat_decoding_error(desired_encoding)
	encodings_left_to_try = options.encoding_to_try # resetting encodings to try for next file

if warnings_encountered:
	sys.exit(2)
else:
	sys.exit(0)
