# encoding: utf-8

from workflow import web, Workflow, PasswordNotFound

def get_projects(api_key, url):
    """
    Parse all pages of projects
    :return: list
    """
    return get_project_page(api_key, url, 1, [])

def get_project_page(api_key, url, page, list):
    log.info("Calling API page {page}".format(page=page))
    params = dict(type='search', per_page=100, page=page, search_fields='title')
    headers = {'accept-encoding':'gzip'}
    r = web.get(url + '/api/saved_objects/', params, headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by Kibana and extract the saved objects
    result = list + r.json()['saved_objects']

    nextpage = r.headers.get('X-Next-Page')
    if nextpage:
        result = get_project_page(api_key, url, nextpage, result)

    return result

def main(wf):
    try:
        api_url = wf.settings.get('api_url')

        # Retrieve projects from cache if available and no more than 600
        # seconds old
        def wrapper():
            return get_projects('', api_url)

        projects = wf.cached_data('projects', wrapper, max_age=3600)

        # Record our progress in the log file
        log.debug('{} kibana projects cached'.format(len(projects)))

    except PasswordNotFound:  # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error('No API key saved')

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    wf.run(main)