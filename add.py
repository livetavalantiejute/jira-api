import shutil
import os
import pandas as pd
import sys

from helpers import bold, get_available_types, check_exists

from Project import Projects
from Issue import Issue


def add(request, user_id):
    projects = Projects()
    projects.get_projects(request)

    while True:
        add_mode = (
            input(
                bold("How would you like to add a task? Choose either Input or File: ")
            )
            .strip()
            .lower()
        )

        if add_mode == "input":
            add_input(request, user_id, projects)
        elif add_mode == "file":
            add_file(request, user_id)
        else:
            print("Try again")
            continue
        break

    issue = Issue(
        summary=summary,
        description=description,
        assignee=assignee,
        priority=priority,
        reporter=user_id,
        issue_type=issue_type,
        parent=parent,
    )
    issue.add_issue(request=request, project_id=project_id)


def add_input(request, user_id, projects):
    project_id = projects.get_project_id()

    all_priorities = Issue.get_priorities(request=request, project_id=project_id)
    all_types = Issue.get_issue_types(request=request, project_id=project_id)

    priority = get_available_types("Available priorities:", all_priorities, "Priority")
    issue_type = get_available_types("Available issue types:", all_types, "Issue")

    if issue_type == "sub-task":
        parent = input(bold("Parent task key: ")).strip().upper()

    while True:
        summary = input(bold("Summary: ")).strip()
        if not summary:
            print("Provide a summary")
            continue
        else:
            break

    description = input(bold("Description: ")).strip()
    assignee = input(bold("Assignee email: ")).strip().lower()

    issue = Issue(
        summary=summary,
        description=description,
        assignee=assignee,
        priority=priority,
        reporter=user_id,
        issue_type=issue_type,
        parent=parent,
    )
    issue.add_issue(request=request, project_id=project_id)


def add_file(request, user_id):
    filename = "tasks.xlsx"
    shutil.copyfile("task_template.xlsx", filename)
    print(bold(f"Change {filename} file with information"))
    while True:
        is_done = input(("Input 'done' when done. ")).strip().lower()
        if is_done == "done":
            break

    df = pd.read_excel(filename, keep_default_na=False).dropna()

    for index, row in df.iterrows():
        project_id = str(row["project_id"])
        priority = str(row["priority"])
        issue_type = str(row["issue_type"])
        summary=str(row["summary"])
        description=str(row["description"])
        assignee=str(row["assignee"])
        parent=str(row["parent"])

        all_priorities = Issue.get_priorities(request=request, project_id=project_id)
        if not check_exists(priority, all_priorities):
            sys.exit("Wrong priority")

        all_types = Issue.get_issue_types(request=request, project_id=project_id)
        if not check_exists(issue_type, all_types):
            sys.exit("Wrong issue type")

        if issue_type == "sub-task" and not parent:
            sys.exit("No parent specified for sub-task")

        issue = Issue(
            summary=summary,
            description=description,
            assignee=assignee,
            priority=priority,
            reporter=user_id,
            issue_type=issue_type,
            parent=parent,
        )
        issue.add_issue(request=request, project_id=project_id)


    if os.path.isfile(filename):
        os.remove(filename)
