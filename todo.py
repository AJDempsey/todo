#! /usr/bin/python
##! /router/bin/python-2.7.1
# This is a command line tool to display, add, modify, and delete tasks.
# This script works on a file structure as follows
#   ~/tasks
#    |-todo
#    |-done
#    |-archive/
#        |-1970/
#        |-Jan
#        |-Feb
#        |-2012/
#        |-Aug
#        |-etc

###############################################################################
# Purpose:
#   This is the main progran that is used from the command line to display the todo list.
# Usage:
#   todo.py [flags | values]
#   for detailed usage do todo.py -h
###############################################################################

from todo_util import *
from todo_tasks import *
from todo_fin import *
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--finish", type=int,\
        help="Finish a task to have it crossed off the list.")
    parser.add_argument("-r", "--remove", type=int,\
        help="Remove a task from the list.")
    parser.add_argument("-p", "--previous", type=int,\
        help="Review the past week's tasks.")
    parser.add_argument("-m", "--modify", type=int,\
        help="Modify a task.")
    parser.add_argument("-a", "--add", action="store_true",\
        help="Add a new task to the task list.")
    parser.add_argument("-c", "--clean", action="store_true",\
        help="Clean up the list moving finished tasks to an archive.")
    args = parser.parse_args()
    home = os.getenv("HOME")
    path = home+"/tasks"
    task_dict = {}
    if args.previous:
        file_name = path+"/done"
        task_dict = generate_done_dictionary(file_name)
    else:
        file_name = path+"/todo"
        task_dict = generate_todo_dict(file_name)
    if args.finish:
        task_dict = modify_task(task_dict, args.finish)
    elif args.add:
        (line, pri, lev, due, success) = add_task_menu()
        if success:
            (task_dict, new_task) = add_task(task_dict, line, pri, lev, due)
            program_menu_print("Would you like to add subtasks [y/N]")
            ui = raw_input()
            if "y" == ui.lower():
                subtasks = add_subtasks_menu(task_dict, new_task)
            else:
                program_menu_print("No subtasks added.")
    elif args.remove:
        task_dict = remove_task(task_dict, args.remove)
    elif args.modify:
        task_dict = modify_task(task_dict, args.modify, False)
    elif args.previous:
        print "Displaying "+str(args.previous)+" previous week(s)."
    elif args.clean:
        task_dict = clean_up(task_dict)
    if args.previous:
        print display_done(task_dict, args.previous).encode('UTF-8')
        file_string = generate_done_string(task_dict)
    else:
        print display_tasks(task_dict).encode('UTF-8')
        file_string = generate_todo_string(task_dict)
    write_tasks(file_string, file_name, "w")
main()

#bkup_done = {u'1352295479.219': {0: {'line': u'Triage FHRP 56, problem with the state (delay remaining timer is ignored)', 'pri': 4, 'sub': {}, 'lev': 0},1: {'line': u'Triage FHRP 6 failure, problem with the state', 'pri': 4,'sub': {}, 'lev': 0}, 2: {'line': u'PAS/cAAs VRF tests, cat4ks can not do ipv6 VRF', 'pri': 4, 'sub': {}, 'lev': 0}, 3: {'line': u'Get a complete run of the automation on hardware', 'pri': 4, 'sub': {0:{'task': u'Get a complete run of the vrrpv3 automation\u2714'}}, 'lev': 0}, 4: {'line': u'Find out why vrrs_10 test case fails sometimes', 'pri': 4, 'sub': {}, 'lev': 0}, 5: {'line': u'Try to get h/w working for indus', 'pri': 4, 'sub': {0: {'task': u'Kind of working, find out why verifying IPv6 makes it freak out and fail. (Possible parallel call problem)'}}, 'lev': 0}, 6: {'line': u'Add CPC goals by the end of the week (5th of Oct)', 'pri': 4, 'sub': {},'lev': 0}, 7: {'line': u'Upload new FHRP indus results to tims','pri': 4, 'sub': {}, 'lev': 0}}}

#done = generate_done_string(bkup_done)
#write_tasks(done, "/users/andempse/tasks/done", "w")
