import flask
import github3
import json
import datetime
import pymongo
import uuid

# For pyCharm auto-complete
from flask import Config
from github3.repos.tag import RepoTag
from github3.pulls import PullRequest


mod = flask.Blueprint('siteroot', __name__, url_prefix='')


@mod.route('/')
def home():
    return flask.render_template('siteroot/home.html')


@mod.route('/list_repos/')
def list_repos():
    config = flask.current_app.config
    repos = []

    # Map the available repos so we don't accidentally expose
    # something sensitive.
    for d in config['REPOSITORIES']:
        repos.append({'Owner': d['Owner'],
                      'Name': d['Name']})

    return json.dumps(repos)


@mod.route('/get_tags/<owner>/<name>/')
def get_tags(owner, name):
    config = flask.current_app.config
    tags = []
    repo_data = _get_repo_data(config, owner, name)

    if repo_data is not None:
        gh = github3.login(
            token=repo_data['ApiKey'],
            url=repo_data.get('EnterpriseUrl'))
        repo = gh.repository(owner, name)
        for t in repo.iter_tags():  # type: RepoTag
            tags.append(t.name)

    return json.dumps(tags)


@mod.route('/generate_report/', methods=['POST'])
def generate_report():
    config = flask.current_app.config
    form_data = json.loads(flask.request.data.decode('utf-8'))
    return_data = _build_and_save_report(config, form_data)

    return json.dumps(return_data)


@mod.route('/export_report/')
def export_report():
    config = flask.current_app.config
    export_id = flask.request.args['ExportId']
    data = _load_saved_report(config, export_id)['data']

    # TODO: Format the report for export.
    # Header block
    export_lines = ['Generated: {generated}\r\n'
                    '\r\n'.format(generated=data['GeneratedAt'])
                    ]

    for repo in data['Repos']:
        repo_name = '{owner}/{name}'.format(
                    owner=repo['Owner'],
                    name=repo['Name'])
        export_lines.append(
            'Repository: {repository}\r\n'
            'From: {from_tag}\r\n'
            'To: {to_tag}\r\n'
            '\r\n'.format(repository=repo_name, from_tag=repo['FromTag'], to_tag=repo['ToTag'])
        )

        for commit_group in repo['CommitGroups']:
            export_lines.append('    {author}\r\n'
                                '\r\n'.format(author=commit_group['Author']))
            for pr in commit_group['PullRequests']:
                export_lines.append(
                    '        {title} -- {url}\r\n'.format(
                        title=pr['title'],
                        url=pr['url'])
                )

            export_lines.append('\r\n')

    response = flask.make_response(''.join(export_lines))
    response.headers['Content-Disposition'] = 'attachment; filename=' + export_id + '.txt'

    return response


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


def _build_and_save_report(config, form_data):
    repos = []
    mongo_client = pymongo.MongoClient(config['MONGO_CONNECTION'])
    db = mongo_client['pyReleaseUtil']

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
            url=repo_data.get('EnterpriseUrl'))
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

    report_key = str(uuid.uuid1())
    db['reports'].insert_one({
        'key': report_key,
        'createdAt': datetime.datetime.utcnow(),
        'data': return_data
    })

    return_data['ExportId'] = report_key

    return return_data


def _load_saved_report(config, report_key):
    mongo_client = pymongo.MongoClient(config['MONGO_CONNECTION'])
    db = mongo_client['pyReleaseUtil']
    return_data = db['reports'].find_one({'key': report_key})
    return_data['ExportId'] = str(report_key)
    return return_data
