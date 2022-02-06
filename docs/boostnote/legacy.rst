Boost Note Legacy
=================

Abstract
-------

This document describes the structure of a legacy Boostnote collection.

Definitions
-----------

- Legacy Boostnote: Boostnote version v0.16.1 and lower, corresponding to [this repo](https://github.com/BoostIO/BoostNote-Legacy)
- Boostnote collection: The directory containing boostnote.json, notes, and attachments. Abstractly, this is all data associated with a single boostnote.json metadata file.
- Base directory: The direct parent directory of boostnote.json.

File Hierarchy
--------------

The Boost Note directory will have one metadata file called "boostnote.json".

The Boost Note directory will have two subdirectories named "attachments" and "notes".

The "notes" directory will contain one **CSON** file for each note in your collection.

For example, your Boost Note directory may look like this::

    .
    ├── attachments
    │   └── 9836727e-da73-4191-b4e2-81770565e494
    │       ├── 25c981e1.svg
    │       └── 6ea0d43d.png
    ├── boostnote.json
    └── notes
        ├── 9836727e-da73-4191-b4e2-81770565e494.cson
        ├── ae08726c-5343-4f59-a3d6-bd0544381a1e.cson
        └── d70facf2-3fba-46e8-a172-02a7be3742c7.cson



Boostnote.json Specification
----------------------------

.. jsonschema:: legacy-metadata-schema.json
    :lift_definitions:
    :auto_reference:
    :auto_target:


Boostnote-Flavored Markdown
---------------------------

Section Hyperlinks
^^^^^^^^^^^^^^^^^^

Boostnote automatically adds ``id`` attributes to headers generated via the ``#`` markdown syntax.

However, some characters are dropped from the ``id`` attribute (example characters: ``!@#$%^&*(-_=+``).

Hyperlinks Between Notes
^^^^^^^^^^^^^^^^^^^^^^^^

Represented by a ``[text](:/BOOSTNOTE_ID)`` markdown tag, where ``BOOSTNOTE_ID`` is replaced with the Boostnote note ID

