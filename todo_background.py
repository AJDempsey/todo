#! /usr/bin/python


################################################################################
#
# Name:
#	todo_background.py
#
# Description:
#	This file contains the functions that operate in the background of the
#	todo list. Ones that can not be explicitly called but which perform some
#	tasks, such as cleaning the list up on a Monday morning, ageing tasks
#	that have a due date, and maybe more (if I can think of any).
#
# Things it would be nice to have:
#	Automatic addition of meetings that you might might have.
#	At the time the meeting is supposed to happen a wee reminder and if it's
#	webex open a new tab with the address.
################################################################################
from todo_util import *
import re
import time

################################################################################
#
# Name:
#	background
#
# Description:
#	This function is what external functions call to perform the batch
#	background activities. Testing the conditions that need to be met for
#	the automated background tasks to be performed.
#
# Inputs:
#
# Outputs:
#
#
################################################################################
def background(dictionary):
    day = time.localtime(time.time())
    day_of_the_week = day[5]
    completed_tasks = dictionary[0].keys()
    # Get the completed tasks, if any of the tasks were completed before the
    # beginning of the current week then clean up the dictionary.
    if "1" == day_of_the_week and len(completed_tasks) > 0:
	# I need some kind of event to trigger this, set an environment variable
	# so that if it is one we clean if it's zero we don't
	# Clean up the list, need to make this happen only once.
	pass
    # Look through all the tasks, if any have due dates then work out if a new
    # priority should be assigned to it.

    # Today's date, due date, date_added, current priority.
    # date_diff = due_date - todays_date, the smaller this number is the
    # higher the priority. pri_diff = top_priority - current_priority.
    # Difference in date divided by the difference in priority
    # Some kind of slider between when the task was added and when it's due, the
    # current date would be the slider. The closer to the due date the higher
    # the priority. If it's passed the due date top priority and highlighting
    # changes. Priority changes happen more often the closer to the due date,
    # less time is spent in each successive priority.

    return dictionary
