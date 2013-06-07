#! /usr/bin/python


################################################################################
#
# Name:
#	todo_tasks.py
#
# Description:
#	This file contains the functions that are required to use the todo list
#	functionality of this project.
#
################################################################################
from todo_util import *
import re
import time

###################################
# Purpose:
#	This function converts a file containg a predefined format into an
#	internal format used through out the program. The main data strucutres
#	are dictionaries. It is entirly possible that this project could also be
#	completed with objects.
#
# Inputs:
#	file_name   -	The name of the file that contains the task list
#
# Outputs:
#	dictionary  -	The internal representation that is used through out the
#			program. This format is as follows.
# { <priority-level (0 - 8):
#   { <task-number>:{
#	    "line":<text>
#	    "pri":<number>
#	    "lev":<number>
#	    "sub":{} or {
#		    <subtask-number>:{
#			    "task":<text>
#			    ?"completed":<number>?}
#	    }
#	    ?"completed":<number>?
#	}
#	(More tasks at this priority)
#    }
#   (The rest of the priority levels)
# }
#
###################################
def generate_todo_dict (file_name):
    #read file
    contents = read_file(file_name)
    dictionary = {0 : {}, 1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}, 6 : {}, 7 : {},\
        8 : {}}

    # Set up the conditions for the while loop
    l = len(contents)
    count = 0
    while count < l:
	# Find the line, clean it up and remove any non letters from the front.
        line = contents[count]
        line = re.sub("#.*$", "", line) # Remove comments from the file
        line = line[:-1]
        line = re.sub("^[^a-zA-Z]+", "", line)
        # If there's anything left of the line process it.
	if line != "":
	    # Match the task's priority and add it to the dictionary,
	    # default to 4
	    match = re.search("--pri=((-)?\d+)", line)
	    if match != None:
		pri = match.group(1)
	    else:
		pri = 4
	    # Match the task's level of highlighting and add it to the
	    # dictionary, default to 4.
	    match = re.search("--lev=(\d+)", line)
	    if match != None:
		lev = match.group(1)
	    else:
		lev = 0
	    # If the task has been completed the --comp flag will exist, match
	    # it and add it to the dictionary.
	    match = re.search("--comp=(\d+\.\d+)", line)
	    if None != match:
		comp = match.group(1)
	    else:
		comp = 0
	    # Get the date a task was added if it exists
	    match = re.search("--add=(\d+\.\d+)", line)
	    if None != match:
		add = match.group(1)
	    else:
		add = 0
	    # Get the due date of the task if it exists
	    match = re.search("--due=(\d+\.\d+)", line)
	    if None != match:
		due = match.group(1)
	    else:
		due = 0
	    # Get rid of the stored metadata of the file
	    sanitize = strip_internal_format(line)
	    # Create a new entry in the dictionary at the right priority level.
	    entry = dictionary[int(pri)]
	    keys = entry.keys()
	    # Find out if there are any exisiting tasks at this priortiy level.
	    # Assign the task number that this task will use.
            if [] != keys:
                highest = keys[-1]
                next = highest + 1
            else:
                next = 0
	    # Add the info to the entry
            entry[next] = {"line" : sanitize, "pri" : pri, "lev" : lev,\
                "sub" : {}}
            if comp > 0:
                entry[next]["completed"] = comp
	    if add > 0:
		entry[next]["add"] = add
	    if due > 0:
		entry[next]["due"] = due
            # Check for sublevels
	    count = check_for_sublevels(entry[next], count, contents)
        # Increment the count.
	count += 1
    # Return the dictionary.
    return dictionary

###################################
# Purpose:
#	This function takes a dictionary and returns it to a formatted stirng to
#	be printed to a file.
# Inputs:
#	dictionary  -	The too task list that is to be written to a file.
# Outputs:
#	file_string	-   The string that can then be written to a file.
###################################
def generate_todo_string(dictionary):
    # Set up variables for looping over.
    keys = dictionary.keys()
    keys.sort(reverse=True)
    task_number = 1
    file_string = ""
    for key in keys:
	# Get each priority level.
        priority_level = dictionary[key]
        entries = priority_level.keys()
	# Loop through each priority level, using the keys.
        for entry in entries:
	    # Grab each value for the key
            an_entry = priority_level[entry]

	    # Add the line and the metadata to a string.
            task_string = str(task_number)+") "+an_entry["line"]
            if "pri" in an_entry:
                task_string += " --pri="+str(an_entry["pri"])
            if "lev" in an_entry:
                task_string += " --lev="+str(an_entry["lev"])
            if "completed" in an_entry:
                task_string += " --comp="+str(an_entry["completed"])
	    if "add" in an_entry:
		task_string += " --add="+str(an_entry["add"])
	    if "due" in an_entry:
		task_string += " --due="+str(an_entry["due"])
            task_string += "\n"
	    # Add the substring to the string.
	    # This if statement can be put in a function and reused
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
	    # Add the task to the whole file string.
            file_string += task_string
            task_number += 1
    # Return the file string.
    return file_string


###################################
# Purpose:
#	Move a task from one priority to another, useful when completing a task
#	and when reducing or increasing the priority of a task.
#
# Inputs:
#	dictionary	-   The data structure containing the item to be
#			    moved.
#	an_entry	-   The task that is to be moved.
#	from_pri	-   The priority that the task is currently in.
#	to_pri		-   The priority the task is being moved to.
#	item_number	-   The position the task is at in it's current prioirty
#			    level
# Outputs:
#	dictionary	-   The rearanged dictionary with the prioirties sorted
#			    out.
###################################
def move_entry(dictionary, an_entry, from_pri, to_pri, item_number):
    # This is terrible form but, why have I done this if statement?
    # I remember now, level zero elements have highlights that are strike
    # through, to reopen the task we need to get rid of this highlighting.
    # And things like this are the reason why we comment as we code kids.
    if from_pri == 0:
        an_entry["lev"] = 0
    # Get all the task in the priority level
    items = dictionary[from_pri].keys()

    # Loop from the task we are moving to the end of the tasks
    while item_number < len(items)-1:
	# Set item N to be the same as N + 1, getting rid of the element that we
	# are moving.
        dictionary[from_pri][item_number] = dictionary[from_pri][item_number+1]
        item_number += 1
    # The last item will be repeated so delete this last item.
    del dictionary[from_pri][item_number]
    new_lev = dictionary[to_pri]
    key_list = new_lev.keys()
    # Find what the new task number is for this element. Either the first
    # element in the level or the highest + 1
    if [] != key_list:
        highest = key_list[-1]
        next = highest + 1
    else:
        next = 0
    # Move the entry to it's new priority level and task number
    dictionary[to_pri][next] = an_entry
    return dictionary

###################################
# Purpose:
#	Print the highlight options menu for the user. A task has already been
#	chosen at this point.
# Inputs:
#	key	-   The priority level of the task that the user wants to
#		    modify.
# Outputs:
#	ui	-   The new level of highlighting the user wants.
###################################
def change_highlighting_menu(key):
    if 0 == key:
        program_menu_print("Can't change the highlighting of"\
            "a completed task. Reopen the task by" + \
            " changing the priority first.")
        return dictionary
    message = "Enter highlighting level: "\
            + menu_highlight("0") + " (REMOVE), "\
            + menu_highlight("1") + " (UNDERLINED), "\
            + menu_highlight("2") + " (BOLD), "\
            + menu_highlight("3") + " (INVERSE)."
    program_menu_print(message)
    # Get the user's new highlighting for this entry.
    ui = raw_input()
    return ui

###################################
# Purpose:
#	Change the highlighting of the given task.
# Inputs:
#	dictionary  -	The data structure that contains the task to be
#			modified.
#	an_entry    -	The entry who's highlighting is to be changed.
#	ui	    -	The user defined new highlighting level.
# Outputs:
#	dictionary  -	The dictionary with the new highlighting for the task.
###################################
def change_highlighting(dictionary, an_entry, ui):
    # Check the value given by the user makes sense. Report if it is not and
    # don't use it to change the hiughlighting.
    try:
        ui = int(ui)
        if ui < 0 or ui > 3:
            raise ValueError
    except ValueError:
        program_menu_print("Invalid value, make sure you"\
            +" use one of the highlighted numbers.\n")
        return dictionary
    # Change the highlighting level and return the dictionary.
    an_entry["lev"] = ui
    return dictionary

###################################
# Purpose:
#	Display options to the user and gather user input to change the priority
#	of a task.
# Inputs:
#	key	-   The level that this task is currently at.
# Outputs:
#	ui	-   The input obtained from the user.
###################################
def change_priority_menu(key):
    # Display the menu to the user
    if 0 == key:
        program_menu_print(INVERSE+"Reopening completed task.")
    message = "Priority levels range from " + menu_highlight("1") + \
        " (low) to " + menu_highlight("8") + " (high).\n" + \
        "Enter new priority for task: "
    program_menu_print(message)
    # Get the user's choice and return it to the calling function.
    ui = raw_input()
    return ui


###################################
# Purpose:
#	This is the function that changes the priority of the task.
# Inputs:
#	dictionary  -	The dictionary that the task is in
#	an_entry    -	The task we want to move
#	ui	    -	Where we want to move the task to
#	number	    -	The task number the task was in the original priority
# Outputs:
#       Same as the move_entry function (dictionary)
###################################
def change_priority(dictionary, an_entry, ui, number):
    # Error check the user input value.
    try:
        ui = int(ui)
        if ui < 1 or ui >= 9:
            raise ValueError
    except ValueError:
        program_menu_print("Invalid value, "+ui+" make sure you"\
            +" use a value in the highlighted range above.\n")
        return dictionary
    # Modify the priority level then pass to the move_entry function which
    # already does what we want.
    an_entry["pri"] = ui
    return move_entry(dictionary, an_entry, key, ui, number)

###################################
# Purpose:
#	Menu and function caller to modify subtasks in a todo list.
# Inputs:
#	dictionary  -	The dictionary the task is in
#	an_entry    -	The entry for which we want to modify subtasks.
#	key	    -	The level this task is at
#	number	    -	Where in the task list this task appears
# Outputs:
#	dictionary  -	The now modified dictionary
###################################
def modify_subtask(dictionary, an_entry, key, number):
    if 0 == key:
        program_menu_print("Can't add subtasks to a completed task."\
            +" Change the priority of the task first.")
	return dictionary
    # Pretty print the task we want to modify, the user has had to get through
    # several layers of menus to get here so they may need reminded of what they
    # wanted to change.
    task_string = display_tasks({key : {key : an_entry}})
    # The number to display will always be one, replace this with the actual
    # task number
    task_string = re.sub("1\) ", str(number)+") ",task_string)
    print task_string.encode('UTF-8')
    # If the task has no subtask we need to add some before we can modify them.
    if {} == an_entry["sub"]:
        dictionary, success = add_subtask_util(dictionary, an_entry, 0)
        return dictionary
    # Print the menu for the user
    message = "To add a new subtask enter "+ menu_highlight("a") + \
            "; to complete subtask enter " + menu_highlight("c") + \
            "; to remove subtask enter " + menu_highlight("r") +\
            "; enter anything else to cancel"
    program_menu_print(message)
    # Get the user input, based on this call different functions.
    ui = raw_input()
    # a = add new subtask, find what the next subtask should be and pass it to
    # the add subtask function
    if "a" == ui.lower():
        next = int(an_entry["sub"].keys()[-1]) + 1
        dictionary, success = add_subtask(dictionary, an_entry, next)
    # Complete a subtask
    elif "c" == ui.lower():
        alpha = "abcdefghijklmnopqrstuvwxyz"
        program_menu_print("Which subtask has been completed:")
        i = 0
	# Print what subtasks exist for the user to choose from
        while i < len(an_entry["sub"].keys())-1:
            print menu_highlight(alpha[i])+" ",
            i += 1
        print menu_highlight(alpha[i])+""+ESCP
        ui = raw_input()
        ui.lower()
	# Need to add error checking for what the user has entered
	# Find the task the user wanted to complete
        if "" == ui:
            program_menu_print("No input, no changes made")
            return dictionary
        u = u"\u2714"
        string = an_entry["sub"][ord(ui)-97]["task"]
        match = re.search(ur'\u2714', string)
	# If this subtask hasn't already been completed add a tick and
	# completion date to the subtask.
        if None == match:
            subtask=ord(ui)-97
            an_entry["sub"][subtask]["task"] =\
                an_entry["sub"][subtask]["task"]+" "+u
            an_entry["sub"][subtask]["completed"] = str(time.time())
    # Completely remove a subtask from the list.
    elif "r" == ui.lower():
        alpha = "abcdefghijklmnopqrstuvwxyz"
        program_menu_print("Which subtask is to be removed:")
        i = 0
	# Print the subtask choices
        while i < len(an_entry["sub"].keys())-1:
            print menu_highlight(alpha[i])+" ",
            i += 1
        print menu_highlight(alpha[i])+""+ESCP
        ui = raw_input()
        ui.lower()
	# Need to add some error checking here
        if "" == ui:
            program_menu_print("No input, no changes made.")
            return dictionary
        # Remove the task by copying everything over and then deleting the last
	# subtask which will show up twice.
	start = ord(ui)-97
        while start < len(an_entry["sub"].keys())-1:
            an_entry["sub"][start] = an_entry["sub"][start+1]
            start += 1
        del an_entry["sub"][start]
    # Unknown command just exit
    else:
        program_menu_print("Unknown command, doing nothing.")
    return dictionary

###################################
# Purpose:
#	Menu and function caller for modifying tasks.
# Inputs:
#	dictionary  -	The data structure to be modified
#	number	    -	The task we want to modify
#	complete    -	Flag to reduce code duplication, completing a task is
#			just modifying it so add some extra code instead of
#			duplicating a large chunk of code.
# Outputs:
#	dictionary  -	The newly modified data structure.
###################################
def modify_task(dictionary, number, complete=True):
    # Get all the keys and set up for looping
    keys = dictionary.keys()
    keys.sort(reverse=True)
    task_number = 1
    file_string = ""
    for key in keys:
	# Get each priority dictionary
        priority_level = dictionary[key]
        entries = priority_level.keys()
	# Get all the task keys
        for selection in entries:
	    # Loop through the tasks until the task number equals the number
	    # passed to the function.
            an_entry = priority_level[selection]
            if number == task_number:
                # If completed is true do the required updates else display
		# menus
		if complete:
                    an_entry["lev"] = 5
                    an_entry["pri"] = 0
                    an_entry["completed"] = time.time()
                    temp = an_entry
                    dictionary = move_entry(dictionary, an_entry, key, 0, selection)
                else:
		    # Menu to display to the user
                    message = "Enter " + menu_highlight("P") + " to change "\
                        + "priority, "+ menu_highlight("H") + " to change "\
                        + "highlighting, or " + menu_highlight("S") + \
                        " to modify subtasks for task " + \
                        menu_highlight(str(number)) + \
                        ". Enter anything else to cancel."
                    program_menu_print(message)
		    # Get user input
                    ui = raw_input()
		    # p means change the priority
                    if "p" == ui.lower():
                        new_pri =  change_priority_menu(key)
			return change_priority(dictionary, an_entry, new_pri,\
				    selection)
		    # h means change the highlighting
                    elif "h" == ui.lower():
                        new_highlight = change_highlighting_menu(key)
			return change_highlighting(dictionary, an_entry,\
				    new_highlight)
		    # s means modify subtasks
                    elif "s" == ui.lower():
                        return modify_subtask(dictionary, an_entry, key, task_number)
                    # Anything else do nothing
		    else:
                        program_menu_print("Unkown command, doing nothing.")
                # Return the dictionary
		return dictionary
	    # Increment the task number
            task_number += 1
    # Return the dictionary
    return dictionary

###################################
# Purpose:
#	Remove tasks that are no longer relevant but have not been completed.
# Inputs:
#	dictionary  -	The dictionary that is to be modified
#	number	    -	The task number for the task to be modified
# Outputs:
#	dictionary  -	The newely modified dictionary
###################################
def remove_task(dictionary, number):
    # Get all the keys for the dictionary and sort them, set up everything for
    # looping.
    keys = dictionary.keys()
    keys.sort(reverse=True)
    task_number = 1
    for key in keys:
	# Get each priority level dictionary
        priority_level = dictionary[key]
        entries = priority_level.keys()
        # Loop thoguth each task
	for selection in entries:
            an_entry = priority_level[selection]
	    # Once the task we want to remove has been found do the following.
	    if number == task_number:
                task_string = display_tasks({key : {key : an_entry}})
                task_string = re.sub("1\) ", str(number)+") ",task_string)
                # Print the task
		program_menu_print("Task to be removed (there will be no "\
                    +"record of this): ")
                print task_string.encode('utf-8')
		# Make sure the user really wants to delete the task, assume
		# they don't really.
                program_menu_print("Are you sure you wish to delete this task?"\
                    +" [y/N]:")
                ui = raw_input()
                if "y" == ui.lower():
                    # Delete the task
                    items = dictionary[key].keys()
                    while selection < len(items)-1:
                        dictionary[key][selection] = dictionary[key][selection+1]
                        selection += 1
                    del dictionary[key][selection]
                    program_menu_print("Task deleted.")
                else:
                    program_menu_print("Task was not deleted.")
		# Return the dictionary
                return dictionary
	    # Increment the task number.
            task_number += 1
    # Return the dictionary
    return dictionary
