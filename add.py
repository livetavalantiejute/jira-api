import json

from helpers import bold

import copy
from Project import Projects
from Issue import Issue


def add(request):
    user_id = request.get_user_id()

    projects = Projects(request.url, request.headers, request.auth)
    projects.get_projects()
    all_projects = projects.projects

    while True:
        print(projects)
        project_id = input(bold("Project id: ")).strip().lower()
        if next((p.id == project_id for p in all_projects), None):
            break
        else:
            print("Wrong project id\n")
            continue

    all_priorities = Issue.get_priorities(request=request, project_id=project_id)
    all_types = Issue.get_issue_types(request=request, project_id=project_id)

    while True:
        print(bold("Available priorities:"))
        for p in all_priorities:
            print(p["name"])
        priority = input(bold("Priority: ")).strip().lower()
        print(next(prio["name"].lower() == priority for prio in all_priorities), None)
        if next((prio["name"].lower() == priority for prio in all_priorities), None):
            break
        else:
            print("Wrong priority\n")
            continue

    while True:
        print(bold("Available issue types:"))
        for t in all_types:
            print(t["name"])
        issue_type = input(bold("Issue type: ")).strip().lower()
        if issue_type in (t["name"].lower() == issue_type for t in all_types):
            break
        else:
            print("Wrong issue type\n")
            continue

    summary = input(bold("Summary: ")).strip()
    description = input(bold("Description: ")).strip()
    assignee = input(bold("Assignee email: ")).strip().lower()

    issue = Issue(
        summary=summary,
        description=description,
        assignee=assignee,
        priority=priority,
        reporter=user_id,
        issue_type=issue_type,
    )
    issue.add_issue(request=request, project_id=project_id)

    # payload = json.dumps(
    #     {
    #         "fields": {
    #             "assignee": {
    #                 "id": assignee_id
    #             },
    #             "description": "Order entry fails when selecting supplier.",
    #             "priority": {"id": "20000"},
    #             "project": {"id": id},
    #             "reporter": {"id": user_id},
    #             "summary": "Main order flow broken",
    #         },
    #     }
    # )
    # response = requests.request("POST", url, data=payload, headers=headers, auth=auth)
