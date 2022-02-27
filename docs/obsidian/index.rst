Obsidian
========

- Webpage: `Obsidian.md <https://obsidian.md/>`_

Glossary
--------

- **Vault**: Term used by Obsidian for a collection of notes.
  - This is equivalent to a Boost Note "Space".

Obsidian Vault
--------------

An Obsidian **vault** is the term used by Obsidian for a *collection of notes*.

An Obsidian *vault* contains markdown files and attachments like images.

Unlike Boost Note, markdown notes are named according to the title of the note rather than a generated ID (like a UUID).

Each Obsidian *vault* has a directory named ``.obsidian`` containing metadata about the vault.

Dot Obsidian Directory
----------------------

This section will describe the ``.obsidian`` directory inside each *vault*.

Workspace File
^^^^^^^^^^^^^^

Within the `.obsidian` directory will be a file called `workspace` containing information about the notes in the *vault*. It stores this information as JSON.

Features
--------

Obsidian Schema Links
^^^^^^^^^^^^^^^^^^^^^

*These should not be used to link between notes.* Obsidian will not recognize these links when generating the link graph (as of Obsidian 0.13.23).

The *context menu* of each note (accessed by right-clicking a note in the sidebar) includes an option to "Copy Obsidian URL".

Interestingly, this is a less-abusive way of doing links between notes than the way Boost Note and Joplin do it. However, it may require some additional configuration, ie. you may need to register the Obisdian application with your Operating System to handle the `obsidian://` URI schema.

These links take the form ``obsidian://open?vault=VAULT_NAME&file=RELATIVE_NOTE_PATH_WITHOUT_EXTENSION``.

In the above:

- ``VAULT_NAME`` and ``RELATIVE_NOTE_PATH_WITHOUT_EXTENSION`` are both URI-escaped
- ``RELATIVE_NOTE_PATH_WITHOUT_EXTENSION`` may be nested within sub-directories
- ``VAULT_NAME`` is a little awkward because:
  - It is based on the parent directory of your notes rather than any other metadata.
  - You could have two *vault*s on the same computer with the same parent directory name. This forces Obsidian to arbitrarily choose one of the vaults.

Links Between Notes
^^^^^^^^^^^^^^^^^^^

*Internal links* use the ``[[NOTE_NAME]]`` syntax, which is custom to Obsidian.

**Renaming Notes**

Obsidian will automatically update all backlinks with the ``[[NOTE_NAME]]`` syntax if you rename a note.

Image Attachments
^^^^^^^^^^^^^^^^^

Image attachments are dumped into the same directory as the notes in Obsidian. They are not treated specially.

However, Obsidian uses a special link syntax for images that does not work in all other editors. If you drag-and-drop an image into Obsidian, it will represent the image with double-square-bracket-notation: ``![[image-path.png]]``.
