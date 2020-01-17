# Implementation design

If you haven't done this before then please read the [features design](FEATURES_DESIGN.md) article first.

It explains the "why"s of the 2 key design concepts of this app:
* hierarchical configuration with inheritance, merging/overwriting and addivity,
* raw parameters passing

Please also read the usual [contributing guide](CONTRIBUTION.md) for the basics of how to create PRs,
the expected style of your code etc - the "general how"s.

This article purpose is to explain "specific how"s - explain what is where in the code and how to add features
by example.


## Structure

Packages:
  
* `gitlabform.gitlabform` - contains the main app logic that provides the cli, parsing of the parameters,
  uses below two packages (reads the config file, initializes connection to GitLab) to apply the config
  defined in `config.yml` to the requested set of projects.

* `gitlabform.gitlab` - contains the GitLab API client code, grouped mostly by the GitLab API 
  [as documented at docs.gitlab.com](https://docs.gitlab.com/ee/api/api_resources.html).

* `gitlabform.configuration` - contains the logic for reading the config from YAML file or a string
  (the latter is used for testing only) and getting an effective config per GitLab project by merging
  the config on these levels: common, group and project settings.

...and a trivial `bin/gitlabform` file that just runs the `gitlabform.gitlabform.GitLabForm.main()`.


## Common pattern - multiple inheritance

In all of the above packages (except `gitlabform.gitlabform`, but it's an exception that will be refactored soon)
we are using the _multiple inheritance_.
 
The basic features are implemented in the "core" class defined in `core.py`. Extensions to it are defined in all other 
files as "feature" classes that inherits the "core". Finally there is an "everything" class that groups them all - it is
defined in `__init__.py` file.


### gitlabform.gitlabform

All of the code here is in a single `GitLabFormCore` class.

This code boils down to the `process_all()` method which for each project that according to the app parameters 
and config should be taken into account, applies the effective config.

The effective config contains what is called the "config sections", which are the YAML keys that can exist under projects
in the config YAML, for example: `deploy_keys`, `secret_variables`, `group_secret_variables` and so on.

Those config section are processed by the code in the methods with the `process_*` naming pattern.

**This is where the key logic of the app is - how to translate YAML config parts into appropriate calls to the GitLab API.**

#### How-tos

If you want to **add/change/fix things under an existing config section** then you need to update the code in those
`process_*` methods (for example: `process_deploy_keys`, `process_secret_variables` and so on).


If you want to **add support for a new config section** (= completely new feature) then you need to:

1. add the method `process_<new_config_section_name>` method to `GitLabFormCore` class (note: this method name HAS TO
   follow this pattern!)
2. add calling the method to the `process_all()` method,


### gitlabform.gitlab

With the basics for making requests to the GitLab API covered in the `GitLabCore` class in `core.py`, all other code
is simple (most of the times).

Almost all methods in other classes end up calling `self._make_requests_to_api` which takes care of making the HTTP
requests to GitLab API with proper authentication, sometimes pagination, if needed retries & timeouts support and more.

Sometimes there is some logic in these methods if:
* we need only specific part of the response from GitLab API - see `GitLabProjects.get_all_projects()` as an example,
* some GitLab APIs need some workarounds for their bugs or documentation inconsistencies, like:
  * some APIs declare in the docs that they accept both "group/project" string OR a project id while in fact only
the latter works - see `GitLabProjects.post_approvals()` as an example,
  * one API does not accept a proper JSON that in case of a field set to a null-value can be omitted, but GitLab 
  requires it to explicitly included and set to an empty array - see `GitLabProjects.put_approvers()` as an example
  (**TODO**: check if this hack is still needed with the current versions of GitLab!)

Note that quite a lot of the code here is **NOT used by the GitLabForm app** - it is only use by some internal Egnyte
apps are still using this project as a library and have not yet switched to the more standard `python-gitlab`.

#### How-tos

If you want to **add/change/fix code that operates on an existing GitLab API** you should look around 
the "feature" classes in this package (for example `GitLabMergeRequests` in `merge_requests.py`).


If you want to **add code that operates on new GitLab API** you should:
 
1. create a new `new_gitlab_api_name.py` file in `gitlabform.gitlab` and define a "feature" class there
   that inherits `GitLabCore` (for example: `GitLabApiName`).
2. add the new feature class to the list of classes inherited by the "everything" `GitLab` class
   defined in `__init__.py`. 


### gitlabform.configuration

**TODO**: describe this part. Especially what an "effective project config" is, because that may not be clear.
