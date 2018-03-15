=================================
Core Explore Federated Search App
=================================

Federation exploration functions for curator core project.

Quick start
===========

1. Add "core_explore_federated_search_app" to your INSTALLED_APPS setting
-------------------------------------------------------------------------

.. code:: python

    INSTALLED_APPS = [
      'core_explore_federated_search_app',
    ]

2. Add "core_explore_federated_search_app" to your DATA_SOURCES_EXPLORE_APPS setting
------------------------------------------------------------------------------------

.. code:: python

    DATA_SOURCES_EXPLORE_APPS = [
        'core_explore_federated_search_app',
    ]

3. Include the core_explore_federated_search_app URLconf in your project urls.py
--------------------------------------------------------------------------------

.. code:: python

    url(r'^federated_search/', include("core_explore_federated_search_app.urls")),
