import base64
import json
import requests
from requests import codes as rc


class ConfluencePageManager(object):
    _CONFLUENCE_API_URL = 'https://myconfluenceurl.net/rest/api/content'
    _PAGE_HEADERS = {
        'Authorization': None,
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'X-Atlassian-Token': 'no-check'
    }
    _CREATE_PAGE_TEMPLATE = {
        'type': 'page',
        'title': None,
        'ancestors': [
            {
                'id': 0
            }
        ],
        'space': {
            'key': ''
        },
        'body': {
            'storage': {
                'value': None,
                'representation': 'storage'
            }
        }
    }
    _UPDATE_PAGE_TEMPLATE = {
        'id': None,
        'type': 'page',
        'title': None,
        'space': {
            'key': ''
        },
        'body': {
            'storage': {
                'value': '',
                'representation': 'storage'
            }
        },
        'version': {
            'number': None
        }
    }
    API_RESPONSE_CODES = {
        200: 'OK',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        406: 'Not Acceptable',
        500: 'Internal Server Error',
        503: 'Service Unavailable'
    }

    def __init__(self, credentials, configuration):
        super(ConfluencePageManager, self).__init__()

        user_key = credentials['confluence_username'] + ':' + credentials['confluence_password']
        encoded_user_key = base64.b64encode(user_key.encode())
        self._headers = self._PAGE_HEADERS.copy()
        self._headers['Authorization'] = 'Basic ' + encoded_user_key.decode()

        self._confluence_space_key = configuration['confluence_space_key']
        self._confluence_page_id = configuration['confluence_page_id']
        self._CREATE_PAGE_TEMPLATE['ancestors'][0]['id'] = self._confluence_page_id
        self._CREATE_PAGE_TEMPLATE['space']['key'] = self._confluence_space_key
        self._UPDATE_PAGE_TEMPLATE['space']['key'] = self._confluence_space_key

        self._narrative_summary = {
            'CREATED': [],
            'UPDATED': [],
            'ERRORED': [],
        }

    @property
    def narrative_summary(self):
        return self._narrative_summary

    @property
    def version_message(self):
        return self._version_message

    @version_message.setter
    def version_message(self, message):
        self._version_message = message

    def publish_biomarker_description_page(self, biomarker_description):
        existing_page = self._get_page_by_title(biomarker_description['name'])

        publish_operation = 'CREATED'
        if existing_page['size'] == 0:
            request_result = self._create_biomarker_description_page(biomarker_description)
        else:
            publish_operation = 'UPDATED'
            request_result = self._update_biomarker_description_page(existing_page['results'][0], biomarker_description)

        response_code = request_result.status_code
        print('\t[{sc}] {rc}'.format(sc=response_code, rc=request_result.reason))
        if response_code != 200:
            publish_operation = 'ERRORED'
            print(request_result.json()['message'])

        self._narrative_summary[publish_operation].append(biomarker_description['name'])

    def _get_page_by_title(self, page_title):
        confluence_page_url = '{url}?title={page_title}&spaceKey={space_key}&expand=version,title,space'.format(
            url=self._CONFLUENCE_API_URL, page_title=page_title, space_key=self._confluence_space_key)

        request_result = requests.get(confluence_page_url, headers=self._headers)
        self._check_requests_result_response(request_result)

        return request_result.json()

    def get_page_by_id(self, page_id):
        confluence_page_url = '{url}/{page_id}?expand=version,title,space,body.storage'.format(
            url=self._CONFLUENCE_API_URL, page_id=page_id)
        print(confluence_page_url)

        request_result = requests.get(confluence_page_url, headers=self._headers)
        self._check_requests_result_response(request_result)

        return request_result.json()

    def _create_biomarker_description_page(self, biomarker_description):
        print('Creating page for {g}'.format(g=biomarker_description['name']))

        new_page_info = self._CREATE_PAGE_TEMPLATE.copy()
        new_page_info['title'] = biomarker_description['name']
        new_page_info['body']['storage']['value'] = biomarker_description['narrative']

        str_data = json.dumps(new_page_info)
        request_result = requests.post(self._CONFLUENCE_API_URL, str_data, headers=self._headers)
        self._check_requests_result_response(request_result)

        return request_result

    def _update_biomarker_description_page(self, existing_page, biomarker_description):
        print('Updating page for {g}'.format(g=biomarker_description['name']))

        confluence_page_url = '{url}/{pageid}/'.format(url=self._CONFLUENCE_API_URL, pageid=existing_page['id'])
        updated_page_version = 1
        if existing_page['version'] and 'number' in existing_page['version']:
            updated_page_version = existing_page['version']['number'] + 1

        updated_page_info = self._UPDATE_PAGE_TEMPLATE.copy()
        updated_page_info['id'] = existing_page['id']
        updated_page_info['title'] = existing_page['title']
        updated_page_info['space']['key'] = self._confluence_space_key
        updated_page_info['version'] = {
            'number': updated_page_version,
            'minorEdit': True,
            'message': self._version_message,
        }
        updated_page_info['body']['storage']['value'] = biomarker_description['narrative']

        str_data = json.dumps(updated_page_info)
        request_result = requests.put(confluence_page_url, str_data, headers=self._headers)
        self._check_requests_result_response(request_result)

        return request_result

    def update_page_title(self, existing_page, new_title):
        print('Updating page for {g}'.format(g=new_title))

        confluence_page_url = '{url}/{pageid}/'.format(url=self._CONFLUENCE_API_URL, pageid=existing_page['id'])
        updated_page_version = 1
        if existing_page['version'] and 'number' in existing_page['version']:
            updated_page_version = existing_page['version']['number'] + 1

        updated_page_info = self._UPDATE_PAGE_TEMPLATE.copy()
        updated_page_info['id'] = existing_page['id']
        updated_page_info['title'] = new_title
        updated_page_info['space']['key'] = self._confluence_space_key
        updated_page_info['version'] = {
            'number': updated_page_version,
            'minorEdit': True,
            'message': self._version_message,
        }
        updated_page_info['body']['storage']['value'] = existing_page['body']['storage']['value']

        str_data = json.dumps(updated_page_info)
        request_result = requests.put(confluence_page_url, str_data, headers=self._headers)
        self._check_requests_result_response(request_result)

        return request_result

    def _check_requests_result_response(self, request_result):
        if request_result.status_code != rc.ok:
            raise SystemError('HTTP Request returned status code {c} - {s}'.format(
                c=request_result.status_code, s=self.API_RESPONSE_CODES[request_result.status_code]))

    def get_child_pages(self):
        confluence_page_url = '{url}/{page_id}/child/page?expand=children.page'.format(
            url=self._CONFLUENCE_API_URL, page_id=self._confluence_page_id)

        request_result = requests.get(confluence_page_url, headers=self._headers)
        self._check_requests_result_response(request_result)

        return request_result.json()
