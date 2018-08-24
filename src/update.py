# encoding: utf-8

from workflow import web, Workflow, PasswordNotFound

def get_saved_searches(api_key, url):
    """
    Parse all pages of projects
    :return: list
    """
    return get_saved_searches_page(api_key, url, 1, [])

def get_saved_searches_page(api_key, url, page, list):
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
        result = get_saved_searches_page(api_key, url, nextpage, result)

    return result

def main(wf):
    try:
        api_url = wf.settings.get('api_url')

        # A wrapper function for the cached call below
        def wrapper():
            return get_saved_searches('', api_url)

        saved_searches = wf.cached_data('saved_searches', wrapper, max_age=3600)

        # Record our progress in the log file
        log.debug('{} kibana searches cached'.format(len(saved_searches)))

    except PasswordNotFound:  # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error('No API key saved')

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    wf.run(main)