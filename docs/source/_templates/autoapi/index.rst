API Reference
=============

The API reference is auto-generated from docstrings using
`sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_. Each
submodule is listed below.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   /autoapi/lucy/index
   {% for page in pages %}
   {% if page.type == "module" and page.display %}
   {{ page.include_path }}
   {% endif %}
   {% endfor %}

