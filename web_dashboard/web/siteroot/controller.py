import flask
import github3
import injector
import json
import datetime

# For pyCharm auto-complete
from flask import Config
from github3.repos import Repository
from github3.repos.tag import RepoTag
from github3.pulls import PullRequest


mod = flask.Blueprint('siteroot', __name__, url_prefix='')


@mod.route('/')
def home():
    return flask.render_template('siteroot/home.html')


@mod.route('/list_repos/')
@injector.inject(config=flask.Config)
def list_repos(config):
    repos = []

    # Map the available repos so we don't accidentally expose
    # something sensitive.
    for d in config['REPOSITORIES']:
        repos.append({'Owner': d['Owner'],
                      'Name': d['Name']})

    return json.dumps(repos)


@mod.route('/get_tags/<owner>/<name>/')
@injector.inject(config=flask.Config)
def get_tags(config, owner, name):
    tags = []
    repo_data = _get_repo_data(config, owner, name)

    if repo_data is not None:
        gh = github3.login(
            token=repo_data['ApiKey'],
            url=repo_data['EnterpriseUrl'])
        repo = gh.repository(owner, name)
        for t in repo.iter_tags():  # type: RepoTag
            tags.append(t.name)

    return json.dumps(tags)


@mod.route('/generate_report/', methods=['POST'])
@injector.inject(config=flask.Config)
def generate_report(config):
    form_data = json.loads(flask.request.data.decode('utf-8'))
    repos = []

    for item in form_data:
        owner = item['Owner']
        name = item['Name']
        from_tag = item['FromTag']
        to_tag = item['ToTag']

        pull_requests = []
        commit_groups = []

        repo_data = _get_repo_data(config, owner, name)
        gh = github3.login(
            token=repo_data['ApiKey'],
            url=repo_data['EnterpriseUrl'])
        repo = gh.repository(owner, name)
        comp = repo.compare_commits(from_tag, to_tag)

        # Search the commits for PRs we want to work with.
        for commit in comp.commits:
            msg = commit.commit.message  # type: str
            if msg.startswith("Merge pull request #"):
                idx_first_space = msg.index(' ', 20)
                pull_requests.append(int(msg[20:idx_first_space]))

        # Get the details for each PR
        groups = {}
        for pr_id in pull_requests:
            pr = repo.pull_request(pr_id)
            if pr.user.login not in groups:
                groups[pr.user.login] = []
            group = groups[pr.user.login]  # type: list
            group.append(pr)

        for group_key in groups.keys():
            group = groups[group_key]
            pull_requests = []
            for pr in group:  # type: PullRequest
                pull_requests.append({'title': pr.title,
                                      'url': pr.html_url})

            commit_groups.append({
                'Author': group_key,
                'PullRequests': pull_requests
            })

        repos.append({
                "Owner": owner,
                "Name": name,
                "FromTag": item['FromTag'],
                "ToTag": item['ToTag'],
                "CommitGroups": commit_groups
        })

    return_data = {'GeneratedAt': datetime.datetime.now().strftime("%c"),
                   'Repos': repos}

    return json.dumps(return_data)


def _get_repo_data(config, owner, name):
    """
    :type config: Config
    :type owner: str
    :type name: str
    :rtype: dict
    """
    for d in config['REPOSITORIES']:
        if d['Owner'] == owner and d['Name'] == name:
            return d

    return None
