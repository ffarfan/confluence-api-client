# confluence-api-client

An experimental Confluence API Client.

This repo contains some code to use the Confluence API to make automatic updates to pages.

Currently, the main class is `ConfluencePageManager`, which handles the operations necessary to manipulate the content of a specific Confluence page.

The `rename_pages.py` script uses the `ConfluencePageManager` to obtain the child pages of a target page, and rename them accordingly.

## Connecting to Confluence

You need to modify the `ConfluencePageManager` and change the `_CONFLUENCE_API_URL` constant to point it to the real Confluence installation.

The main script passes the user credentials to the `ConfluencePageManager`. These must be updated accordingly.
