#! /usr/bin/python

################################################################################
#
# Name:
#	todo_fin.py
# Desctiption:
#	This file contains functions that are required to manipulate the
#	completed task list.
################################################################################

from todo_util import *
import re
import time

###################################
# Purpose:
#	This function generates the completed dictionary from the file provided.
#	Meta data is picked up from flags to be stored.
# Inputs:
#	file_name   -	The name of the file that contains the task list.
# Outputs:
#	dictionary  -	The task list represented in the following structure.
#
#	{completed:{
#	    task_number: {
#			    "line":<text>
#			    "pri":4
#			    "lev":0
#		    	    "sub":{ <empty> or
#				    task_numer:{"line":<text>
#					"comp":<number>}
#				  }
#			 }
#		    }
#	}
#
###################################
def generate_done_dictionary (file_name):
    # Read the file into a list
    contents = read_file(file_name)
    dictionary = {}
    l = len(contents)
    count = 0

    # Do the following until count equals the number of lines
    while count < l:
	# Choose the line, strip comments, remove last character
        line = contents[count]
        line = re.sub("#.*$", "", line)
        line = line[:-1]
	# Remove all the non-letter characters at the beginning of the line.
        line = re.sub("^[^a-zA-Z]+", "", line)

	# If there is anything left on the line process it.
        if line != "":
	    # Get the date of completion (this should always exist
            match = re.search("--comp=(\d+\.\d+)", line)
            if None != match:
                comp = match.group(1)
            else:
                comp = 0
	    match = re.search("--add=(\d+\.\d+)", line)
	    if None != match:
		added = match.group(1)
	    else:
		added = 0
	    match = re.search("--due=(\d+\.\d+)", line)
	    if None != match:
		due = match.group(1)
	    else:
		due = 0
	    # Get rid of any remaining meta data
            sanitize = strip_internal_format(line)
	    # Check if any other tasks were completed at the same time.
	    # Time of completion is the identifier for this dictionary.
            if comp in dictionary:
                task_num = len(dictionary[comp])
            else:
		dictionary[comp] = {}
		task_num = 0
	    dictionary[comp][task_num] = {"line": sanitize, "pri": 0, "lev":10,\
			"sub":{}}
	    if added > 0:
		dictionary[comp][task_num]["add"] = added
	    if due > 0:
		dictionary[comp][task_num]["due"] = due
            # If there is one element len = 1 but to access this element it's 0
	    # so subtract one to access elements
	    task_num = len(dictionary[comp]) - 1
	    entry = dictionary[comp][task_num]
	    # Check for subtasks as well
            count = check_for_sublevels(entry, count, contents)
        count += 1
    return dictionary

###################################
# Purpose:
#	Turn a dictionary back into a string that can be printed to a file.
#
# Inputs:
#	dictionary  -	The dictionary that is to be made into a sting again.
#
# Outputs:
#	task_string -	The string representation of the dictionary that is to
#			be printed to a file.
###################################
def generate_done_string(dictionary):
    # Get the ditionaries keys and sort them in order.
    keys = dictionary.keys()
    keys.sort()

    # Depending on the way sort works either the newest or the oldest task will
    # be written to the file first.
    task_number = 1
    file_string = ""

    # Loop through all the keys and convert them to the file format that has
    # been predetermined.
    for key in keys:
        day = dictionary[key]
        # Get all the tasks that were completed at a particular time.
	tasks = day.keys()
        for task in tasks:
	    # Get the value for each key.
            an_entry = day[task]
	    # Add the task and completion time to the string.
            task_string = str(task_number)+") "+an_entry["line"]
            task_string += " --comp="+str(str(key))
	    if "add" in an_entry:
		task_string += " --add="+str(an_entry["add"])
	    if "due" in an_entry:
		task_string += " --due="+str(an_entry["due"])
            task_string += "\n"
	    # Add any and all subtasks to the file string as well.
            if an_entry["sub"] != {}:
                sublevels = an_entry["sub"]
                alpha = "abcdefghijklmnopqrstuvwxyz"
                subkeys = sublevels.keys()
                for key in subkeys:
                    task_string += "\t"+alpha[key]+") "+sublevels[key]["task"]
                    if "completed" in sublevels[key]:
                        task_string += " --comp="+str(sublevels[key]\
                            ["completed"])
                    task_string+="\n"
	    # Add each task to the file string that will be returned to the
	    # caller.
            file_string += task_string
            task_number += 1
    return file_string

###################################
# Purpose:
#	This function is used to print the tasks that have been completed to the
#	command line. This function prints out the tasks that have been
#	completed in the past 7 days but only prints days where a task was
#	completed.
#
# Inputs:
#	dictionary  -	The dictionary that is to be printed to the command
#			line.
# Outputs:
#	display_string	-   The string that is to be displayed.
###################################
def display_done(dictionary, weeks):
# Sort dictionary based on date from this date to seven days previously
#   Get today's date time.localtime()
#   Normalise to be a full day (year, month, day, 23, 59, 59, ?, ?, ?)
#   Get seven days previously millisecond time of this ^ - 7 * millisecond day
#   dictionaryionary has the time of completion as the keys.
    display_string = ""
    keys = dictionary.keys()
    today = time.localtime()
    new_time = (today[0], today[1], today[2], 23, 59, 59, -1, -1, -1)
    s_in_a_day = 86400.0
    day_of_the_week = time.mktime(new_time)
    menu_pri = WHITE+DARKEN
    while day_of_the_week > (time.mktime(new_time) - (s_in_a_day *(8 * weeks))):
    # Print date
    # Day of the week is currently the max of the day
    # Get the start of the day
    # If any tasks fall between these times print the date and the task
	tmp_list = []
	for key in keys:
	    number_key = float(key)
	    if number_key < day_of_the_week and\
		    number_key > (day_of_the_week - s_in_a_day):
		tmp_list += [key]
	if [] != tmp_list:
	    display_string += menu_highlight ("Tasks completed on " +\
		time.strftime("%a, %d %b %Y", time.localtime(day_of_the_week))\
		+ "\n"+ESCP)
	    for days in tmp_list:
		count =1
		tasks = dictionary[days]
		for task in tasks:
		    an_entry = tasks[task]
		    task_string = display_tasks({count: {count : an_entry}})\
			    +"\n"
		    display_string += re.sub("1\) ", str(count)+") ",\
			    task_string)
		    count += 1

    # Print all the tasks that were completed on this day
    # Advance date, repeat until the week has completed
        day_of_the_week = day_of_the_week - s_in_a_day

# Any items that are passed this last date move to the archive.
#   (Some how)
    return display_string
