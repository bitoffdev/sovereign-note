Sovereign Note
==============

Getting Started
---------------

Before starting, make sure you have installed:

- Python 3.8 or newer
- Poetry

Clone this repo.

Run::

    poetry install

Now, you are ready to run the main program. To see the command line help, run::

    poetry run sovereign-note --help

Example
-------

For example, if you wanted to convert a Boost Note directory to a Joplin JEX
file, you would run the following::

    poetry run sovereign-note boost2jex tests/resources/example-boostnote-collection

For the example Boost Note directory (which is included in this repo), the
output of the command would look like this::

    Writing folder Folder One to Joplin store
    Writing folder Folder Two to Joplin store
    Writing folder Special 123 !@#$%^&*()_+-=`~ Folder to Joplin store
    Writing attachment meta to Joplin store: BoostnoteAttachment(relative_path='9836727e-da73-4191-b4e2-81770565e494/25c981e1.svg')
    Writing attachment blob to Joplin store: BoostnoteAttachment(relative_path='9836727e-da73-4191-b4e2-81770565e494/25c981e1.svg')
    Writing attachment meta to Joplin store: BoostnoteAttachment(relative_path='9836727e-da73-4191-b4e2-81770565e494/6ea0d43d.png')
    Writing attachment blob to Joplin store: BoostnoteAttachment(relative_path='9836727e-da73-4191-b4e2-81770565e494/6ea0d43d.png')
    Creating Joplin note for Boostnote note with ID 9836727eda734191b4e281770565e494
    Replaced attachment: [oc_boxes.svg](:/3edb302d6c6742df9e86b9c1c6ea3ec8)
    Replaced attachment: [oc_boxes.png](:/8449599a40df4146952119dd78ac9da5)
    Creating Joplin note for Boostnote note with ID d70facf23fba46e8a17202a7be3742c7
    Replaced link: [My First Note](:/ae08726c53434f59a3d6bd0544381a1e)
    Replaced link: [My Second Note](:/d70facf23fba46e8a17202a7be3742c7)
    Creating Joplin note for Boostnote note with ID ae08726c53434f59a3d6bd0544381a1e
    Replaced link: [My First Note](:/ae08726c53434f59a3d6bd0544381a1e)
    Replaced link: [My Second Note](:/d70facf23fba46e8a17202a7be3742c7)
    Saved output to /tmp/tmpc_9bomqu.jex

Notice the last line: The output JEX file is written to the temporary
directory. You will want to move it after running the above command if you want
to save it permanently.

Additional Docs
---------------

Additional docs can be found in the docs directory.

To render the docs found in the docs directory, run::

    docker-compose up --build docs

Then, open your browser to http://localhost:8080.

Local Development
-----------------

To test changes you've made locally, run the following commands::

    docker-compose build dev
    docker-compose up lint
    docker-compose up test
