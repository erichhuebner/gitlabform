import pytest

from gitlabform.gitlabform import GitLabForm
from gitlabform.gitlabform.test import create_group, create_project_in_group, get_gitlab, GROUP_NAME

PROJECT_NAME = 'services_project'
GROUP_AND_PROJECT_NAME = GROUP_NAME + '/' + PROJECT_NAME


@pytest.fixture(scope="module")
def gitlab(request):
    create_group(GROUP_NAME)
    create_project_in_group(GROUP_NAME, PROJECT_NAME)

    gl = get_gitlab()

    def fin():
        # disable test integrations
        gl.delete_service(GROUP_AND_PROJECT_NAME, 'mattermost')

    request.addfinalizer(fin)
    return gl  # provide fixture value


config_service_mattermost_confidential_issues_events = """
gitlab:
  api_version: 4

project_settings:
  gitlabform_tests_group/services_project:
    services:
      mattermost:
        active: true
        webhook: https://mattermost.com/hooks/xxx
        username: gitlab
        merge_requests_events: true
        merge_request_channel: "merge-requests"
        push_events: false
        issues_events: false
        confidential_issues_events: false # this was not supposed to work according to #70
        tag_push_events: false
        note_events: false
        confidential_note_events: false
        pipeline_events: false
        wiki_page_events: false
        branches_to_be_notified: "all"
"""


class TestServices:

    def test__mattermost_confidential_issues_events(self, gitlab):
        gf = GitLabForm(config_string=config_service_mattermost_confidential_issues_events,
                        project_or_group=GROUP_AND_PROJECT_NAME)
        gf.main()

        service = gitlab.get_service(GROUP_AND_PROJECT_NAME, 'mattermost')
        assert service['confidential_issues_events'] is False
