from github import Github
g = Github("access_token")
g = Github(login_or_token="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")
repo = g.get_repo("CheckInChallenge/CheckInTest")
print(repo)
repo.create_issue(title="This is a new issue", body="This is the issue body")
