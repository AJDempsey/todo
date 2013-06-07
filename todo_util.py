#! /usr/bin/python

# Purpose
#   This file contains all the common functions needed to operate the todo command line program.
#   The structure of the program is split into two the tasks that are in the list and tasks that have been finished, the functions found here are used in the other files that make up this program.

import re
import os
import codecs
import time

# Command line character sequences for different types of highlighting
BOLD="\033[1m"
DARKEN="\033[2m"
LIGHTEN="\033[3m"
UNDERLINE="\033[4m"
INVERSE="\033[7m"
CONSEAL="\033[8m"
STRIKE_THROUGH="\033[9m"

# Command line character sequences for different types of colouring.
# Hex codes don't always work, these do.
BLACK="\033[0;30m"
RED="\033[0;31m"
GREEN="\033[0;32m"
BROWN="\033[0;33m"
BLUE="\033[0;34m"
PURPLE="\033[0;35m"
CYAN="\033[0;36m"
WHITE="\033[0;37m"

# Lighter colour versions of the above character sequences, they can also be made using a colour plus highlighting.
HI_BLACK="\033[0;90m"
HI_RED="\033[0;91m"
HI_GREEN="\033[0;92m"
HI_BROWN="\033[0;93m"
HI_BLUE="\033[0;94m"
HI_PURPLE="\033[0;95m"
HI_CYAN="\033[0;96m"
HI_WHITE="\033[0;97m"

# To return the terminal to it's normal colour an escape sequences is needed to show the end of the highlighting and colour changes.
ESCP="\033[0m"

###################################
# Purpose:
#   Multiple places in the code contained repeated code for highlighting, this function 
#   reduces the amount of repeated code and is used to display the program's menu.
# Inputs:
#   string  -   The text that is to be used for the menu, highlighting is added and the text is printed straight away.
# Output:
#   N/A
###################################
def program_menu_print(string):
    print WHITE+DARKEN+string+ESCP


###################################
# Purpose:
#   Certain parts of the menu need to be highlighted to show the user what the program expects as input in the next section of the menu.
# Inputs:
#   string  -   The string which the highlighting should be applied to.
# Outputs:
#   The string that has had highlighting applied to it. 
# Comments:
#   Note that this function returns the string rather than printing it as the input provided to this function
#   is often used in the middle of strings which are printed.
###################################
def menu_highlight(string):
    return HI_BROWN+string+WHITE+DARKEN

###################################
# Purpose:
#   This function builds the sequence of codes that are need to provide the various 
#   colours and highlighting for a string that is to be displayed.
# Inputs:
#   pri -   The number priority that this task has been given
#   lev -   The level of highlighting that this task has been given
# Outputs:
#   priority_string -   The string that is a combination of character sequesnces
#                       to provide the required colouring and highlighting
###################################
def build_priority_string (pri, lev):
    priority_string = ""

    # Make sure the inputs are integers
    pri = int(pri)
    lev = int(lev)

    # Cap the priority at 8 no matter how large.
    if pri > 7 :
        pri = 8

    # Add the correct colouring to the string based on the pri variable
    if pri <= 0:
        priority_string += WHITE
    elif pri == 1:
        priority_string += HI_GREEN
    elif pri == 2:
        priority_string += GREEN
    elif pri == 3:
        priority_string += CYAN
    elif pri == 4:
        priority_string += HI_BLUE
    elif pri == 5:
        priority_string += BLUE
    elif pri == 6:
        priority_string += PURPLE
    elif pri == 7:
        priority_string += RED
    elif pri > 7:
        priority_string += RED+DARKEN

    # Add the correct highlighting to the string based on the lev variable
    if lev == 1:
        priority_string += UNDERLINE
    elif lev == 2:
        priority_string += BOLD
    elif lev == 3:
        priority_string += INVERSE
    elif lev == 5:
        priority_string += STRIKE_THROUGH
    elif lev == 10:
	   priority_string += DARKEN
    # return the string with colouring and highlighting.
    return priority_string

###################################
# Purpose:
#   The text files which the task are loaded from contain some flags
#   to say how the tasks should be displayed. These flags should not be displayed
#   on the command line so they are removed by regex in this function.
#   If any new flags are added to the format they should be removed here.
# Inputs:
#   sanitize    -   The line from the text file that is to have flags removed
# Outputs:
#   sanitize    -   The freshly sanitized line which should contain only the
#                   task that is to be displayed.
# Comments:
#   Current flags that need to be sanitized:
#       --lev   -   Level of highlighting
#       --pri   -   Number reflecting the colour that should be applied
#       --comp  -   This may not always exist, if it does the task has been
#                   completed and this is when it was completed in seconds
#                   since the epoch
###################################
def strip_internal_format (sanitize):
    sanitize = re.sub("--lev=[0-9]+", "", sanitize)
    sanitize = re.sub("--pri=(-)?[0-9]+", "", sanitize)
    sanitize = re.sub("--comp=[0-9]+\.[0-9]+", "", sanitize)
    sanitize = re.sub("--add=[0-9]+\.[0-9]+", "", sanitize)
    sanitize = re.sub("--due=[0-9]+\.[0-9]+", "", sanitize)
    sanitize = re.sub("\s+$", "", sanitize)
    return sanitize

###################################
# Purpose:
#   It is possible for each task to have sub-levels this function looks to see
#   if there are any. If any are found they are added to the dictionary entry
#   under the sublevel key.
# Inputs:
#   dictionary  -   The dictionary to add to
#   index       -   The current index of where we are in the list that is passed
#   lines       -   The text file in a list form where one entry is one line from
#                   file.
# Outputs:
#   index + delta - 1   -   This is where we should continue processing the
#                           list from when we return to the caller.
###################################
def check_for_sublevels(dictionary, index, lines):
    # delta is the temporary index that we will be using.
    delta = 1

    # Check to make sure index we are using is within the length of the list
    if index+delta < len(lines):
        line = lines[(index+delta)] # Get the line the valid index relates to
    else:
        return index # Index + delta is invalid return the last known good index
    # Sub-levels take the form "\s+<letter>)" if this isn't the first thing on
    # the line then this isn't a sublevel.
    match = re.match("^\s+[a-zA-Z]+\)", line)
    if None == match: # Regex didn't match
        return index # Return last known good index.

    # Assign the sub key value to sublevels for easy access
    sublevels = dictionary["sub"]
    count = 0

    # While there are still sublevels loop
    while None != match:
        # Sanitize line
        line = re.sub("#.*$", "", line)
        line = line[:-1]
        line = re.sub("^\s+[a-zA-Z]\)\s+", "", line)

        # If line contains content
        if line != "":
            # Record completion date if it exists.
            match = re.search("--comp=(\d+\.\d+)", line)
            if None != match:
                comp = match.group(1)
            else:
                comp = 0
            line = strip_internal_format(line) # Remove flags
            sublevels[count] = {"task": line} # Store each subtask as it's own dictionary
            if comp > 0:
                sublevels[count]["completed"] = comp # Add completion to the subtask if it exists
            count += 1
            delta += 1
            if index + delta > len(lines)-1: # If there are no more entries in the list return last index
                return (index + delta - 1)
            line = lines[(index+delta)] # Move to the next line
            match = re.match("^\s+[a-zA-Z]+\)", line) # Complete the condition that we check for the loop
    return (index + delta - 1) # We advance one too far so add the delta minus one to the original index

###################################
# Purpose:
#       Read files into a list in a safe manner, reduce code duplication
# Inputs:
#       file_name   -   Name of the file to load (full qualified path in all the code here)
# Outputs:
#       contents    -   A list of all the lines contained in the file file_name
###################################
def read_file(file_name):
    try:
    # Open file
        file_handle = codecs.open(file_name, mode="r", encoding="utf-8")
    # Read contents
        contents = file_handle.readlines()
    # Close file
        file_handle.close()
    # Deal with exceptions
    except IOError as e:
        print "Problem with the file\nError message ({0}): {1}".format(e.errno,\
            e.strerror)
        exit(e.errno)
    # TODO: Mod this so it fails gracefully but displays what the actual error was
    except Exception as e:
        print "Something went wrong while reading the file. Encoding maybe."
        exit(0)
    return contents

###################################
# Purpose:
#       Generate the string that is to be displayed on the command line for the tasks
#       that have yet to be completed. I.E. the todo list task items and subtasks.
#       This is completed one entry at a time so this function generates the string
#       for one single task, not the whole task list.
# Inputs:
#       pri_string  -   The string that will be used to provide highlighting and colour
#                       to the tasks and subtask in this entry.
#       task_num    -   The nth task that has appeared in the task list. This number is
#                       used internally when changes are made to a task.
#       an_entry    -   The data structure that represents the task that we want to
#                       display.
#               {
#                   "line": <text>
#                   "pri": <number>
#                   "lev": <number>
#                   ?"completed": <number>?
#                   ?sub:{
#                          <0>:{"task":<text>
#                                    ?"completed":<number>?}
#                           .
#                           .
#                           <n>:{"task":<text>
#                                    ?"completed":<number>?}
#                       }?
#               }
# Outputs:
#       display_string  -   The combination of the priority string and all 
#                           "line" values and sublevel "task" values
###################################
def generate_output_string(pri_str, task_num, an_entry):
    # Add highlighting and the number for this task and then content
    display_string = pri_str+str(task_num)+") " + an_entry["line"]
    display_string += ESCP
    if "due" in an_entry:
	display_string += menu_highlight(" (Due: "+time.asctime
		(time.localtime(float(an_entry["due"])))+")")+ESCP

    # If the task has been completed add the completion date and time
    if "completed" in an_entry:
        display_string += menu_highlight("\tCompleted "+time.asctime(\
            time.localtime(float(an_entry["completed"]))))+ESCP
    display_string += "\n"

    # If the sub level value is not empty add the sub tasks to the string
    if an_entry["sub"] != {}:
        sublevels = an_entry["sub"]
        # Subtask identifier uses letters instead of numbers.
        # The below string is indexed by the subtask number and used
        # for the identifier.
        alpha = "abcdefghijklmnopqrstuvwxyz"
        subkeys = sublevels.keys()
        for key in subkeys:
            # Add the subtask text to the string with an identifier
            display_string += pri_str+"\t"+alpha[key]+") "\
                +sublevels[key]["task"]+ESCP
            # If the subtask has been completed add the completion date to the string
            if "completed" in sublevels[key]:
                display_string += menu_highlight("\tCompleted "+time.asctime(\
                    time.localtime(float(sublevels[key]["completed"]))))+ESCP
            display_string+="\n"
    # Return the assembled task for printing.
    return display_string

###################################
# Purpose:
#       Write tasks to a file in a safe manner, reduce code duplication
# Inputs:
#       file_string -   The string that is to be written to the file
#       file_name   -   The name of the file that we want to write to
#       mode        -   The mode to open the file in (write, or append)
# Outputs:
#
###################################
def write_tasks(file_string, file_name, file_mode):
    try:
    # Open file
        file_handle = codecs.open(file_name, mode=file_mode, encoding="utf-8")
    # Read contents
        file_handle.write(file_string)
    # Close file
        file_handle.close()
    # Deal with I/O errors
    except IOError as e:
        print "Problem with the file\nError message ({0}): {1}".format(e.errno,\
            e.strerror)
        exit(e.errno)
    # Deal with any other errors
    # TODO: modify this to display the actual error that was encountered.
    except:
        print "Something went wrong with writing the file, encoding maybe."
        exit(0)

###################################
# Purpose:
#       This function builds the string that will be written to the done file
#       when clean up is performed. As the tasks have already been completed no
#       priority or highlight information is carried over, only the completion
#       date.
# Inputs:
#       dictionary  -   The dictionary that is to be converted to a string.
# Outputs:
#       file_string -   The string representing the dictionary.
###################################
def generate_cleanup_string(dictionary):
    # Get the keys in the dictionary and sort them in reverse.
    keys = dictionary.keys()
    keys.sort(reverse=True)

    # Identifier for the task.
    task_number = 1

    # String to store the text in.
    file_string = ""

    # Get each entry in the dictionary add the text, completion date, and
    # subtasks to the string. Increment the counter by one each time
    for entry in keys:
        an_entry = dictionary[entry]
        task_string = str(task_number)+") "+an_entry["line"]
        if "completed" in an_entry:
            task_string += " --comp="+str(an_entry["completed"])
	if "add" in an_entry:
	    task_string += " --add="+str(an_entry["add"])
	if "due" in an_entry:
	    task_string += " --due="+str(an_entry["due"])
        task_string += "\n"
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
        file_string += task_string
        task_number += 1
    # Return the string representing the dictionary ready for writing to
    # a file
    return file_string

###################################
# Purpose:
#       This function is used to clean up the todo dictionary, removing the
#       completed tasks. At the same time the completed tasks are written to
#       a file so they can be reviewed in the future.
# Inputs:
#       dictionary  -   The todo dictionary that contains all the tasks.
#                       Completed and in progress
# Outputs:
#       dictionary  -   The todo dictionary that now contains only the in
#                       progress tasks.
###################################
def clean_up(dictionary):
    # Completed tasks are the value for the key "0" in the data structure.
    cleanup_dict = dictionary[0]
    # Clear out the completed tasks in the dictionary
    dictionary[0] = {}
    # Remove level and priority meta data from the dictionary
    for entry in cleanup_dict:
        an_entry = cleanup_dict[entry]
        del an_entry["lev"]
        del an_entry["pri"]
    # Set the path to the usual file
    home = os.getenv("HOME")
    path = home+"/tasks"
    file_handle = path+"/done"
    # Create the string that is to be written to the file
    file_string = generate_cleanup_string(cleanup_dict)
    # Write to the file
    write_tasks(file_string, file_handle, "a")
    # Return the dictionary that was passed in
    return dictionary

###################################
# Purpose:
#       Utility function was created so the same code could be used
#       for creation of tasks and modification of existing tasks.
#       This is why when a task is created you see the "Task has no subtasks."
#       message.
# Inputs:
#       dictionary  -   The parent dictionary that is being modified
#                       (Do I need this? Pass by reference of pass by value?)
#       entry       -   The entry that is to be modified with a new subtask
#       subtask_num -   The number that this subtask should take. This should
#                       be current number of subtasks + 1
# Outputs:
#       dictionary  -   The dictionary that should now be modified with a new
#                       subtask in entry
#       0/1         -   Boolean really showing if the addition was successful
#                       or not.
###################################
def add_subtask(dictionary, entry, subtask_num):
    # Create message to be shown to the user, then print it
    message = ""
    if 0 == subtask_num:
        message = "Task has no subtasks. "
    message += "Enter text for new subtask (an identifier will be added by "\
        +"the program):"
    program_menu_print(message)
    # Get users response
    ui = raw_input()
    if "" == ui:
        program_menu_print("No text entered, no subtask created")
        return (dictionary, 0)
    # Add the new subtask to the dictionary
    entry["sub"][subtask_num] = {"task": ui}
    return (dictionary, 1)

###################################
# Purpose:
#       Allow multiple subtasks to be added to a task at the one time.
#       (Add subtasks until the user explicitly says no more.)
# Inputs:
#       dictionary  -   The dictionary containing the entry
#       entry       -   The entry we're going to add the subtask to.
# Outputs:
#       dictionary  -   The dictionary which should now contain extra subtasks
#                       in the entry.
# Comment:
#       Dictionaries must be pass by reference, look this up.
###################################
def add_subtasks_menu(dictionary, entry):
    condition = True
    count = 0
    # Set to true to loop indefinitely
    while condition:
        # Call the utility function to actually add the subtask
        dictionary, success = add_subtask(dictionary, entry, count)
        count += success # Only increment count when tasks are actually added.
        # Find out if the user wants to add more tasks
        program_menu_print("Any more subtasks? [Y/n]")
        ui = raw_input()
        if "n" == ui.lower():
            condition = False
    # Return the dictionary
    return dictionary

def number_to_month(month):
	"""docstring for number_to_month"""
	if 1 == month:
	    return "Jan"
	elif 2 == month:
	    return "Feb"
	elif 3 == month:
	    return "Mar"
	elif 4 == month:
	    return "Apr"
	elif 5 == month:
	    return "May"
	elif 6 == month:
	    return "Jun"
	elif 7 == month:
	    return "Jul"
	elif 8 == month:
	    return "Aug"
	elif 9 == month:
	    return "Sep"
	elif 10 == month:
	    return "Oct"
	elif 11 == month:
	    return "Nov"
	elif 12 == month:
	    return "Dec"
	else:
	    raise ValueError
###################################
# Purpose:
#	This function gets the due date for task from the user.
#
# Inputs:
#	N/A everything is picked up from the user inside the function
#
# Outputs:
#	due_date    -	A floating point number representing the due date for
#			the task.
###################################
def get_due_date():
    today = time.time()
    today_tuple = time.localtime(today)
    day = today
    month = ""
    year = ""
    hour = 23
    minute = 59
    seconds = 59
    # Get the day from the user default to today

    msg = "Enter the day of completion: [ Defaults to today: "+\
	    str(today_tuple[2])+" ]"
    program_menu_print(msg)
    ui = raw_input()
    if "" == ui:
	day = today_tuple[2]
    elif int(ui) < 1 or int(ui) > 31:
	program_menu_print("That is not a real date, using the default")
	day = today_tuple[2]
    else:
	day = int(ui)
    # Get the month from the user. Default to the current month or if the day is
    # less than today the next month.
    default_month = today_tuple[1]
    if day < today_tuple[2]:
	default_month += 1
    if default_month > 12:
	default_month = 1
    msg = "Enter the month of completion: "+menu_highlight("1 - 12")+" [Default:"\
	    +" "+str(default_month)+" ("+ number_to_month(default_month) +") ]"
    program_menu_print(msg)
    ui = raw_input()
    if "" == ui:
	month = default_month
    elif int(ui) < 1 or int(ui) > 12:
	program_menu_print("That is not a real month, using the default")
	month = default_month
    else:
	month = int(ui)

    # Get the year from the user. Default to the current year unless the month
    # is less than today's month
    default_year = today_tuple[0]
    if month < today_tuple[1]:
	default_year += 1
    msg = "Enter the year of completion: "+menu_highlight("YYYY format")+\
	   "[Default: "+str(default_year)+" ]"
    program_menu_print(msg)
    ui = raw_input()
    if "" == ui:
	year = default_year
    elif int(ui) < default_year:
	program_menu_print("I can't let you set a task in the past. Using the \
		default")
	year = default_year
    else:
	year = int(ui)
    program_menu_print("Due date for this task is the end of: "+\
	    menu_highlight(str(day) +" "+ number_to_month(month)+" "+str(year)))
    new_date = (year, month, day, hour, minute, seconds, -1, -1 ,-1)
    due_date = time.mktime(new_date)
    return due_date
    # Convert the user input to a floating point number representing the date
    # and return it to the caller.

###################################
# Purpose:
#       The menu to display when adding a new task to the todo list
# Inputs:
#       N/A
# Outputs:
#       line    -   The text for the new task
#       pri     -   Priority the user wants
#       lev     -   Level of highlighting the user wants
#       success -   If the user input was collected correctly
###################################
def add_task_menu():
    # Ask user to enter test and collect it
    program_menu_print("Enter the text for the new task:")
    ui = raw_input()
    if "" == ui:
        program_menu_print("No input no new task added.")
        return ("", "", "", "",  0)
    line = ui
    program_menu_print("Is there a due date for this task? y/N")
    ui = raw_input()
    if "y" == ui.lower():
	due = get_due_date()
    else:
	due = 0
    # Ask user to enter priority and collect it
    message = "Enter priority from " + menu_highlight("1") + \
        " to " + menu_highlight("8") + " (default is 4): "
    program_menu_print(message)
    ui = raw_input()
    try:
        ui = int(ui)
        if ui < 1:
            ui = 1
        elif ui > 8:
            ui = 8
    except ValueError:
        program_menu_print("Non-interger value entered defaulting to priority"+\
            "4")
        ui = 4
    pri = ui

    # Ask user to enter level of highlighting and collect it
    message = "Enter highlight level " + menu_highlight("0") + \
          " (NO HIGHLIGHTING), " + menu_highlight("1") + \
          " (UNDERLINED), " + menu_highlight("2") + \
          " (BOLD), " + menu_highlight("3") + \
          " (INVERSE).\nDefault is 0: "
    program_menu_print(message)
    ui = raw_input()
    try:
        ui=int(ui)
        if ui < 1 or ui > 3:
            ui = 0
    except ValueError:
        program_menu_print("Non-integer value entered; defaulting to no"+\
            "highlighting.")
        ui = 0
    lev = ui

    # Return what the user has entered
    return (line, pri, lev, due, 1)

###################################
# Purpose:
#       Add a task to the task list, tasks can't be added to the done list
#       using this manner.
# Inputs:
#       dictionary  -   The dictionary the task is to be added to.
# Outputs:
#       dictionary  -   The dictionary that now has another task added to it.
###################################
def add_task(dictionary, line, pri, lev, due):
    next = len(dictionary[pri].keys())
    dictionary[pri][next] = {"line" : line, "pri" : pri, "lev" : lev, \
	    "added":time.time(), "sub" : {} }
    if 0 != due:
	dictionary[pri][next]["due"] = due
    new_entry = dictionary[pri][next]
    return (dictionary, new_entry)


###################################
# Purpose:
#	This takes every task feeds it to a function that builds the string,
#	these strings are then concatinated together and returned to the calling
#	function.
#
# Inputs:
#	dictionary  -	The structure that is to be made into a string
#
# Outputs:
#	display_string	-   The string that represents the formatted dictionary
#			    for display
###################################
def display_tasks(dictionary):
    # Get the keys from the dictionary.
    keys = dictionary.keys()
    keys.sort(reverse=True)
    task_number = 1
    display_string = ""

    # Loop through all the tasks.
    for key in keys:
        priority_level = dictionary[key]
        entries = priority_level.keys()
        for key in entries:
	    # Pick the next entry.
            an_entry = priority_level[key]

	    # Get the priority string.
            priority_string = build_priority_string(an_entry["pri"],\
                an_entry["lev"])

	    # Add the task specific string to the display string
            display_string += generate_output_string(priority_string, \
                task_number, an_entry)
            task_number += 1
    # Return the string to be displayed.
    return display_string[:-1]

