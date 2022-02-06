Boost Note Next Local
=====================

File Heirarchy
--------------

The Boost Note directory will have one metadata file called "boostnote.json".

The Boost Note directory will have two subdirectories named "attachments" and "notes".

The "notes" directory will contain one JSON file for each note in your collection.


For example, your Boost Note directory may look like this::

    .
    ├── attachments
    │   └── image-kzaa7q90.png
    ├── boostnote.json
    └── notes
        ├── BBJGwkU_K.json
        ├── -bTIjMLFQZ.json
        └── LP4IVuuEL.json

Boostnote.json Specification
----------------------------

.. jsonschema:: next-local-metadata-schema.json
    :lift_definitions:
    :auto_reference:
    :auto_target:


Note Specification
------------------

.. jsonschema:: next-local-note-schema.json
    :lift_definitions:
    :auto_reference:
    :auto_target:

