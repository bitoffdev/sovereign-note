Joplin JEX File Format
======================

File Hierarchy
--------------

This document will describe the JEX file format, which is one of the export
formats supported by Joplin.

At a high-level, a JEX file is a tarball_ containing *notes* and
*attachments*.

The *notes* are all placed at the top level of the tarball.

The *attachments* are placed under the "attachments" directory in the tarball.

Example
^^^^^^^

For example, this is what the file hierarchy may look like inside a JEX file::

    .
    ├── 0e1fe57d81ff26afea38.md
    ├── 3edb302d6c6742df9e86b9c1c6ea3ec8.md
    ├── 8449599a40df4146952119dd78ac9da5.md
    ├── 9836727eda734191b4e281770565e494.md
    ├── 994f8d784b2b3fc2cd04.md
    ├── 9f132269d958068b11e0.md
    ├── ae08726c53434f59a3d6bd0544381a1e.md
    ├── d70facf23fba46e8a17202a7be3742c7.md
    └── resources
        ├── 3edb302d6c6742df9e86b9c1c6ea3ec8.svg
        └── 8449599a40df4146952119dd78ac9da5.png


Resource Files
--------------

Each *resource* in a JEX file is represented as a single markdown file.

There are 16 *resource* types::

    export enum ModelType {
    	Note = 1,
    	Folder = 2,
    	Setting = 3,
    	Resource = 4,
    	Tag = 5,
    	NoteTag = 6,
    	Search = 7,
    	Alarm = 8,
    	MasterKey = 9,
    	ItemChange = 10,
    	NoteResource = 11,
    	ResourceLocalState = 12,
    	Revision = 13,
    	Migration = 14,
    	SmartFilter = 15,
    	Command = 16,
    }

(From the Joplin ModelType_ enum)

General Resource File Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each *resource* in a JEX file is represented as a single markdown file.

The markdown file will have a **body** containing markdown (or other contents)
followed by a newline followed by a number of ``key: value`` lines containing
metadata for the resource.

Note
^^^^

Here is an example of a serialized note within the JEX file::

    My First Note
    
    # My First Note
    
    ## References
    
    - [My First Note](:/ae08726c53434f59a3d6bd0544381a1e)
    - [My Second Note](:/d70facf23fba46e8a17202a7be3742c7)
    
    id: ae08726c53434f59a3d6bd0544381a1e
    parent_id: 9f132269d958068b11e0
    created_time: 2021-10-02T16:38:20.381000+0000
    updated_time: 2021-10-02T16:39:17.579000+0000
    is_conflict: 0
    latitude: 0.00000000
    longitude: 0.00000000
    altitude: 0.0000
    author: 
    source_url: 
    is_todo: 0
    todo_due: 0
    todo_completed: 0
    source: evernote
    source_application: net.cozic.joplin-desktop
    application_data: 
    order: 0
    user_created_time: 2021-10-02T16:38:20.381000+0000
    user_updated_time: 2021-10-02T16:38:20.381000+0000
    encryption_cipher_text: 
    encryption_applied: 0
    markup_language: 1
    is_shared: 0
    share_id: 
    conflict_original_id: 
    type_: 1

Note that the actual document you will see in the Joplin editor is this::

    My First Note
    
    # My First Note
    
    ## References
    
    - [My First Note](:/ae08726c53434f59a3d6bd0544381a1e)
    - [My Second Note](:/d70facf23fba46e8a17202a7be3742c7)

All other lines in the *resource* are metadata headers.

Also, note that the special link ``[My First
Note](:/ae08726c53434f59a3d6bd0544381a1e)`` points to another note in the JEX
file with the id ``ae08726c53434f59a3d6bd0544381a1e``.

Folder
^^^^^^

Here is an example of a serialized folder within the JEX file::

    Folder One

    id: 9f132269d958068b11e0
    created_time: 2021-08-07T14:51:30.227Z
    updated_time: 2021-08-07T14:51:30.227Z
    user_created_time: 2021-08-07T14:51:30.227Z
    user_updated_time: 2021-08-07T14:51:30.227Z
    encryption_cipher_text: 
    encryption_applied: 0
    parent_id: 
    is_shared: 0
    share_id: 

.. _ModelType: https://github.com/laurent22/joplin/blob/8e55fe31eecdb9772ab1df8f020669b406918269/packages/lib/BaseModel.ts#L10
.. _tarball: https://en.wikipedia.org/w/index.php?oldid=1067325544
