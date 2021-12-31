#!/usr/bin/env python3
import datetime
import os
import sys
import tempfile
from typing import Optional
import logging
import re

import boostnote
import joplin

logger = logging.getLogger(__name__)


UUID_CHARSET_WITHOUT_DASHES = "0123456789abcdefABCDEF"


def convert_id_from_joplin_to_boostnote(joplin_id: str) -> str:
    """
    Recent versions of legacy boostnote generate UUIDs by default, though just
    about anything can be used as an ID for backwards compatibility.
    """
    if len(joplin_id) == 32 and all(c in UUID_CHARSET_WITHOUT_DASHES for c in joplin_id):
        return f"{joplin_id[:8]}-{joplin_id[8:12]}-{joplin_id[12:16]}-{joplin_id[16:20]}-{joplin_id[20:]}"
    logger.warn("Could not map Joplin ID to UUID. The Joplin ID will be used as-is.")
    return joplin_id


def replace_links(
    content: str,
    store
) -> str:
    def get_replacement(m: re.Match) -> str:
        link_text = m.group(1)
        joplin_id = m.group(2)

        # handle resources
        joplin_entity = store.get_note_by_id(joplin_id)
        boostnote_entity_id = convert_id_from_joplin_to_boostnote(joplin_entity.headers['id'])
        if isinstance(joplin_entity, joplin.JoplinResource):
            attachment_relpath = os.path.join(joplin_entity.id, joplin_entity.basename)
            repl = f"[{link_text}](:storage/{attachment_relpath})"
            print(f"Replaced attachment: {repl}")
        elif isinstance(joplin_entity, joplin.ParsedJoplinNote):
            repl = f"[{link_text}](:note:{boostnote_entity_id})"
            print(f"Replaced link: {repl}")

        else:
            raise Exception("Failed to process link")

        return repl

    prog = re.compile(r"\[([^\]]*)\]\(:\/([^\)]*)\)")
    content = prog.sub(get_replacement, content)

    return content


def main(jex_path: str, output_location: Optional[str]=None):
    store = joplin.JoplinTarStore(jex_path)
    if not output_location:
        output_location = tempfile.mkdtemp()

    col = boostnote.BoostnoteCollection.create(output_location)
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
        boostnote_entity_id = convert_id_from_joplin_to_boostnote(joplin_entity.headers['id'])
        #
        # Notes
        #
        if joplin_entity.model_type == joplin.JoplinModelType.Note:
            print(f"Adding note with id '{boostnote_entity_id}'")
            boost_entity = boostnote.BoostnoteNote(
                id=boostnote_entity_id,
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
