import json

from helpers import bold, red, get_available_types

import copy
from Project import Projects
from Issue import Issue
from view import view


def edit(request, user_id):
    projects, project_id, issues = view(request, user_id)

    issue_id = input(bold("\nInput issue key: ")).strip().upper()

    issue = next((i for i in issues.issues if i.key == issue_id), None)
    if not issue:
        print("Issue not found")
    
    print("Which fields do you want to change? After each field, press Enter, if done, input 'done'")
    fields = []

    while True:
        field = input().strip().lower()

        if field == "done":
            break
        elif field == "key":
            print(red("Try again. Field is unchangeable"))
        elif any(issue_field for issue_field in dir(issue) if issue_field == field and not callable(getattr(issue, issue_field)) and not issue_field.startswith("__")):
            fields.append(field)
        else:
            print(red("Try again. Field does not exist"))

    changed = []
    # edited_issue = copy.deepcopy(issue)
    for change_field in fields:
        match change_field:
            case "priority":
                all_priorities = Issue.get_priorities(request=request, project_id=project_id)
                change_value = get_available_types("Available priorities:", all_priorities, "Priority")
            case "issue_type":
                all_types = Issue.get_issue_types(request=request, project_id=project_id)
                change_value = get_available_types("Available issue types:", all_types, "Issue")
            case _:
                change_value = input(f"{bold(change_field.title())}: ").strip()
        changed.append({
            change_field: change_value
        })

    try:
        issue.patch_edit(request, changed, project_id)
    except Exception as e:
        print(str(e))
    
    

    # all_priorities = Issue.get_priorities(request=request, project_id=project_id)
    # all_types = Issue.get_issue_types(request=request, project_id=project_id)

    # priority = get_available_types("Available priorities:", all_priorities, "Priority")
    # issue_type = get_available_types("Available issue types:", all_types, "Issue")

    # summary = input(bold("Summary: ")).strip()
    # description = input(bold("Description: ")).strip()
    # assignee = input(bold("Assignee email: ")).strip().lower()

    # issue = Issue(
    #     summary=summary,
    #     description=description,
    #     assignee=assignee,
    #     priority=priority,
    #     reporter=user_id,
    #     issue_type=issue_type,
    # )
    # issue.add_issue(request=request, project_id=project_id)
