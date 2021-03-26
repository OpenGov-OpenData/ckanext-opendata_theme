
=============
ckanext-opendata_theme
=============

This package contains several ckan plugins:
   - opengov_custom_css
   - opengov_custom_homepage
   - opengov_custom_header
   - opengov_custom_footer

------------
Requirements
------------

Supported CKAN 2.7 and CKAN 2.9
This plugin is compatible with Python 2.8 and Python 3.6.

------------------------
Development Installation
------------------------

To install ckanext-opendata_theme for development, use opendata-ops/vagrant_local_env scripts to setup local env
according to instructions in that folder.

-----------------
Running the Tests
-----------------

To run the tests, do::

    pytest --disable-warnings ckanext.opendata_theme

To run the tests and produce a coverage, pylint and bandit reports, first make sure you have
tox installed in your virtualenv (``pip install tox``) then run::

    tox --parallel 4

Then check `reports` folder for generated reports.