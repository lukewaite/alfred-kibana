# encoding: utf-8
import sys
import argparse
from workflow import Workflow3, ICON_WEB, ICON_WARNING, ICON_INFO, web, PasswordNotFound
from workflow.background import run_in_background, is_running

__version__ = '0.1.0'

log = None

def search_for_item(project):
    """Generate a string search key for a project"""
    elements = []
    elements.append(project['attributes']['title'])
    return u' '.join(elements)

def main(wf):
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    parser.add_argument('--seturl', dest='apiurl', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save the provided API key or URL
    ####################################################################

    if args.apiurl:
        log.info("Setting API URL to {url}".format(url=args.apiurl))
        wf.settings['api_url'] = args.apiurl
        return 0

    ####################################################################
    # Check that we have an API url saved
    ####################################################################

    try:
        wf.settings['api_url']
    except KeyError:  # API key has not yet been set
        wf.add_item('No Kibana URL set.',
                    'Please use logseturl to set your Kibana API url.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    ####################################################################
    # View/filter Kibana Saved Discovery Pages
    ####################################################################

    query = args.query

    saved_searches = wf.cached_data('saved_searches', None, max_age=0)
    dashboards = wf.cached_data('dashboards', None, max_age=0)

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available',
                    'Action this item to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    # Notify the user if the cache is being updated
    if is_running('update') and not saved_searches:
        wf.rerun = 0.5
        wf.add_item('Updating saved search list via Kibana...',
                    subtitle=u'This can take some time if you have a large number of objects.',
                    valid=False,
                    icon=ICON_INFO)

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('saved_searches', max_age=3600) and not is_running('update'):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    # If script was passed a query, use it to filter projects
    if query and saved_searches:
        saved_searches = wf.filter(query, saved_searches, key=search_for_item, min_score=20)

    # If script was passed a query, use it to filter projects
    if query and dashboards:
        dashboards = wf.filter(query, dashboards, key=search_for_item, min_score=20)

    if not dashboards and not saved_searches:
        wf.add_item('No saved searches or dashboards found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for search in saved_searches:
        wf.add_item(title=search['attributes']['title'],
                    # subtitle=project['path_with_namespace'],
                    arg=wf.settings['api_url'] + '/app/kibana#/discover/' + search['id'],
                    valid=True,
                    icon=None,
                    uid=search['id'])

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for dashboard in dashboards:
        wf.add_item(title=dashboard['attributes']['title'],
                    # subtitle=project['path_with_namespace'],
                    arg=wf.settings['api_url'] + '/app/kibana#/dashboard/' + dashboard['id'],
                    valid=True,
                    icon=None,
                    uid=dashboard['id'])

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow3(update_settings={
        'github_slug': 'lukewaite/alfred-kibana',
        'version': __version__,
        'frequency': 1
    })
    log = wf.logger
    sys.exit(wf.run(main))