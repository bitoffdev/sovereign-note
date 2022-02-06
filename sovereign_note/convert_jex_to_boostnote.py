#!/usr/bin/env python3
import datetime
import logging
import os
import re
import sys
import tempfile
from collections import defaultdict
from typing import Optional, Set

from . import boostnote, joplin

logger = logging.getLogger(__name__)

UUID_CHARSET_WITHOUT_DASHES = "0123456789abcdefABCDEF"


def convert_id_from_joplin_to_boostnote(joplin_id: str) -> str:
    """
    Recent versions of legacy boostnote generate UUIDs by default, though just
    about anything can be used as an ID for backwards compatibility.
    """
    if len(joplin_id) == 32 and all(
        c in UUID_CHARSET_WITHOUT_DASHES for c in joplin_id
    ):
        return f"{joplin_id[:8]}-{joplin_id[8:12]}-{joplin_id[12:16]}-{joplin_id[16:20]}-{joplin_id[20:]}"
    logger.warn("Could not map Joplin ID to UUID. The Joplin ID will be used as-is.")
    return joplin_id


def find_attachments(content: str, store) -> Set[str]:
    """Return a list of <Joplin IDs> referencing attachments"""
    prog = re.compile(r"\[[^\]]*\]\(:\/([^\)]*)\)")
    linked_joplin_ids = prog.findall(content)
    # filter out non-attachments
    result = set()
    for joplin_id in linked_joplin_ids:
        joplin_entity = store.get_note_by_id(joplin_id)
        if isinstance(joplin_entity, joplin.JoplinResource):
            result.add(joplin_id)
    return result


def replace_links(
    content: str,
    store,
    map_attachment_to_notes,
) -> str:
    def get_replacement(m: re.Match) -> str:
        link_text = m.group(1)
        joplin_id = m.group(2)

        # handle resources
        joplin_entity = store.get_note_by_id(joplin_id)
        boostnote_entity_id = convert_id_from_joplin_to_boostnote(
            joplin_entity.headers["id"]
        )
        if isinstance(joplin_entity, joplin.JoplinResource):
            if len(map_attachment_to_notes[joplin_entity.id]) == 1:
                prefix = convert_id_from_joplin_to_boostnote(
                    next(iter(map_attachment_to_notes[joplin_entity.id]))
                )
            else:
                prefix = joplin_entity.id
            attachment_relpath = os.path.join(prefix, joplin_entity.basename)
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


def main(jex_path: str, output_location: Optional[str] = None):
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
    note_queue = []
    resource_queue = []
    for p in store.list():
        joplin_entity = joplin.parse_joplin_note(store.read(p))
        if joplin_entity.model_type == joplin.JoplinModelType.Note:
            note_queue.append(joplin_entity)
        elif isinstance(joplin_entity, joplin.JoplinResource):
            resource_queue.append(joplin_entity)

    # Build up a mapping from Joplin attachment ID to the notes that use the
    # attachment.
    map_attachment_to_notes = defaultdict(set)
    for joplin_entity in note_queue:
        joplin_id = joplin_entity.headers["id"]
        print(f"Searching note with joplin id '{joplin_id}' for attachments")
        content = joplin_entity.body.split("\n\n", 1)[-1]
        for _attach_id in find_attachments(content, store):
            map_attachment_to_notes[_attach_id].add(joplin_id)
    print(map_attachment_to_notes)

    for joplin_entity in note_queue:
        boostnote_entity_id = convert_id_from_joplin_to_boostnote(
            joplin_entity.headers["id"]
        )
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
            content=replace_links(
                joplin_entity.body.split("\n\n", 1)[-1], store, map_attachment_to_notes
            ),
        )
        col.add_entity(boost_entity)

    for joplin_entity in resource_queue:
        print(f"Adding resource with id '{joplin_entity.headers['id']}'")
        if len(map_attachment_to_notes[joplin_entity.id]) == 1:
            prefix = convert_id_from_joplin_to_boostnote(
                next(iter(map_attachment_to_notes[joplin_entity.id]))
            )
        else:
            prefix = joplin_entity.id
        col.add_attachment(
            os.path.join(prefix, joplin_entity.basename),
            store.read_resource_bin(joplin_entity),
        )

    print(f"Finished building boostnote collection at path: '{col.dir_path}'")


if __name__ == "__main__":
    jex_path = sys.argv[1]
    main(jex_path)
