import json

from helpers import bold, red, get_available_types

import copy
from Project import Projects
from Issue import Issue
from view import view


def edit(request, user_id):
    """
    Edit an issue from a project.
    Gets API request object and user id from main()
    """
    #Call view function to show all projects, select one and show its issues
    #Extract project id and issues from view function
    project_id, issues = view(request, user_id)

    while True:
        #look through issue ids
        issue_id = input(bold("\nInput issue key: ")).strip().upper()

        issue = next((i for i in issues.issues if i.key == issue_id), None)
        if not issue:
            print("Issue not found")
            continue
        else:
            break
    
    print("Which fields do you want to change? After each field, press Enter, if done, input 'done'")
    fields = []

    while True:
        field = input().strip().lower()

        #Check if field is available.
        if field == "done":
            break
        elif field in ["key", "created"]:
            print(red("Try again. Field is unchangeable"))
        #All available fields are in issue object. So dir(issue) is called
        elif any(issue_field for issue_field in dir(issue) if issue_field == field and not callable(getattr(issue, issue_field)) and not issue_field.startswith("__")):
            fields.append(field)
        else:
            print(red("Try again. Field does not exist"))

    changed = []
    
    #ask for each field input
    for change_field in fields:
        match change_field:
            case "priority":
                #Show all priorities, get input and validate
                all_priorities = Issue.get_priorities(request=request, project_id=project_id)
                change_value = get_available_types("Available priorities:", all_priorities, "Priority")
            case "issue_type":
                #Show all issue types, get input and validate
                all_types = Issue.get_issue_types(request=request, project_id=project_id)
                change_value = get_available_types("Available issue types:", all_types, "Issue")
            case "assignee":
                change_value = input(f"{bold(change_field.title())}: ").strip()
                #pass None if assignee is empty - otherwise it will default to a different assignee
                if not change_value:
                    change_value = None
            #Mandatory field
            case "reporter":
                while True:
                    change_value = input(f"{bold(change_field.title())}: ").strip()
                    if not change_value:
                        print("Issues need a reporter")
                    else:
                        break
            #Default
            case _:
                change_value = input(f"{bold(change_field.title())}: ").strip()
        changed.append({
            change_field: change_value
        })

    try:
        issue.patch_edit(request, changed, project_id)
    except Exception as e:
        print(str(e))
