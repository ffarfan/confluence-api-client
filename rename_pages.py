from ConfluencePageManager import ConfluencePageManager

CONFLUENCE_CONFIG = {
    "DEV": {
        "confluence_space_key": "~ffarfan@gmail.com",
        "confluence_page_id": 271520440
    },
    "PROD": {
        "confluence_space_key": "OI",
        "confluence_page_id": 215744674
    }
}


def rename_to_to_oct(username, password, configuration):
    creds = {
        'confluence_username': username,
        'confluence_password': password,
    }

    confluence_page_manager = ConfluencePageManager(creds, configuration)
    confluence_page_manager.version_message = 'Rename from TO to OCT'
    child_pages = confluence_page_manager.get_child_pages()

    for page in child_pages['results']:
        child_page = confluence_page_manager.get_page_by_id(page['id'])
        old_title = child_page['title']
        new_title = old_title.replace('ANN - TO', 'ANN - OCT')
        confluence_page_manager.update_page_title(child_page, new_title)


def rename_sw_pages(username, password, configuration):
    creds = {
        'confluence_username': username,
        'confluence_password': password,
    }

    confluence_page_manager = ConfluencePageManager(creds, configuration)

    # Data to update before running
    confluence_page_manager.version_message = 'Rename Software (SW) Team Pages'
    parent_pages = {
        127349741: {
            'from': 'DRA - ',
            'to': 'SW - DRA - '
        },
        108945980: {
            'from': 'LIF - ',
            'to': 'SW - LIF - '
        },
        215768131: {
            'from': 'OA - ',
            'to': 'SW - OA - '
        },
        111082715: {
            'from': 'Panel Catch Rate - ',
            'to': 'SW - Panel Catch Rate - '
        },
        215768079: {
            'from': 'OST - ',
            'to': 'SW - OST - '
        },
    }

    for parent_page in parent_pages:
        confluence_page_manager._confluence_page_id = parent_page

        child_pages = confluence_page_manager.get_child_pages()

        for page in child_pages['results']:
            child_page = confluence_page_manager.get_page_by_id(page['id'])
            old_title = child_page['title']
            new_title = old_title.replace(parent_pages[parent_page]['from'], parent_pages[parent_page]['to'])
            confluence_page_manager.update_page_title(child_page, new_title)


if __name__ == '__main__':
    username, password = ('ffarfan@gmail.com', 'hunter2')

    rename_to_to_oct(username, password, CONFLUENCE_CONFIG['PROD'])
    rename_sw_pages(username, password, CONFLUENCE_CONFIG['PROD'])
