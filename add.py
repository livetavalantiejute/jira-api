import json

from helpers import bold, get_available_types

import copy
from Project import Projects
from Issue import Issue


def add(request, user_id):
    projects = Projects()
    projects.get_projects(request)

    project_id = projects.get_project_id()

    all_priorities = Issue.get_priorities(request=request, project_id=project_id)
    all_types = Issue.get_issue_types(request=request, project_id=project_id)

    priority = get_available_types("Available priorities:", all_priorities, "Priority")
    issue_type = get_available_types("Available issue types:", all_types, "Issue")

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
