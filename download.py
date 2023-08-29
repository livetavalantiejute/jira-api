import pandas as pd

from view import view_project


def download(request, user_id):
    """Download the project issues from dataframe. The filename is project id"""
    project_id, issues = view_project(request)

    df = pd.DataFrame(issues.issues)

    df.to_excel(f"{project_id}.xlsx", index=False)
