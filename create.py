import requests
import json


def create(request, user_id):
    key = input("Provide project key (e.g. 'SFT'): ").strip().upper()
    name = input("Provide project name (e.g. 'Software board'): ").strip().lower()
    type = input("Provide type (Scrum or Kanban): ").strip().lower()
    description = input("Provide description: ").strip()

    payload = json.dumps(
        {
            "assigneeType": "PROJECT_LEAD",
            "description": description,
            "key": key,
            "leadAccountId": user_id,
            "name": name,
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-"
            + type
            + "-classic",
            "projectTypeKey": "software",
        }
    )

    response = requests.request(
        "POST",
        request.url + "rest/api/2/project",
        data=payload,
        headers=request.headers,
        auth=request.auth,
    )

    print(f"Project {response.json()['key']} inserted successfully!")
