#!/usr/bin/env python3
import datetime
import os
import sys
import tempfile
import re

import boostnote
import joplin


def replace_links(
    content: str,
    store
) -> str:
    def get_replacement(m: re.Match) -> str:
        link_text = m.group(1)
        joplin_id = m.group(2)

        # handle resources
        joplin_entity = store.get_note_by_id(joplin_id)
        if isinstance(joplin_entity, joplin.JoplinResource):
            attachment_relpath = os.path.join(joplin_entity.id, joplin_entity.basename)
            repl = f"[{link_text}](:storage/{attachment_relpath})"
            print(f"Replaced attachment: {repl}")
        elif isinstance(joplin_entity, joplin.ParsedJoplinNote):
            repl = f"[{link_text}](:note:{joplin_id})"
            print(f"Replaced link: {repl}")

        else:
            raise Exception("Failed to process link")

        return repl

    prog = re.compile(r"\[([^\]]*)\]\(:\/([^\)]*)\)")
    content = prog.sub(get_replacement, content)

    return content


def main(jex_path: str):
    store = joplin.JoplinTarStore(jex_path)

    col = boostnote.BoostnoteCollection.create(tempfile.mkdtemp())
    print(f"Building boostnote collection at path: '{col.dir_path}'")

    #
    # Create folders in boostnote metadata file
    #
    print("Generating boostnote metadata file")
    for p in store.list():
        joplin_entity = joplin.parse_joplin_note(store.read(p))
        if isinstance(joplin_entity, joplin.JoplinFolder):
            print(f"Adding folder with id '{joplin_entity.headers['id']}'")
            col.meta.add_folder(
                joplin_entity.headers["id"], "#FFFFFF", joplin_entity.name
            )
    col.meta.write_to_file(os.path.join(col.dir_path, "boostnote.json"))

    #
    # Copy all notes over
    #
    print("Copying notes")
    for p in store.list():
        joplin_entity = joplin.parse_joplin_note(store.read(p))
        #
        # Notes
        #
        if joplin_entity.model_type == joplin.JoplinModelType.Note:
            print(f"Adding note with id '{joplin_entity.headers['id']}'")
            boost_entity = boostnote.BoostnoteNote(
                id=joplin_entity.headers["id"],
                created_at=datetime.datetime.strptime(
                    joplin_entity.headers["created_time"], joplin.JOPLIN_DATE_FORMAT
                ),
                updated_at=datetime.datetime.strptime(
                    joplin_entity.headers["updated_time"], joplin.JOPLIN_DATE_FORMAT
                ),
                title=joplin_entity.body.split("\n\n", 1)[0],
                folder_id=joplin_entity.headers["parent_id"],
                tags=[],
                is_starred=False,
                is_trashed=False,
                content=replace_links(joplin_entity.body.split("\n\n", 1)[-1], store),
            )
            col.add_entity(boost_entity)
        #
        # Resources
        #
        elif isinstance(joplin_entity, joplin.JoplinResource):
            print(f"Adding resource with id '{joplin_entity.headers['id']}'")
            col.add_attachment(
                os.path.join(joplin_entity.id, joplin_entity.basename),
                store.read_resource_bin(joplin_entity)
            )

    print(f"Finished building boostnote collection at path: '{col.dir_path}'")


if __name__ == "__main__":
    jex_path = sys.argv[1]
    main(jex_path)
