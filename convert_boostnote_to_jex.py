import re
import tempfile
import uuid

import boostnote
import joplin


def joplin_uuid() -> str:
    return str(uuid.uuid4()).replace("-", "")


# UUID4_REGEX = "^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"


def boostnote_to_joplin_id(boostnote_id: str):
    # If the boostnote ID is already in the correct form, return it.
    if len(boostnote_id) == 32 and re.match(r"^[0-9a-fA-F]*$", boostnote_id):
        return boostnote_id
    # At one point, Boostnote was generating 10-byte keys represented via hex.
    #
    # As a workaround, we'll prepend 6 hard-coded bytes. Yes, this is a little
    # jank. However, a conflict is exorbitantly unlikely to occur.
    if len(boostnote_id) == 20 and re.match(r"^[0-9a-fA-F]*$", boostnote_id):
        return f"b0057b005700{boostnote_id}"
    # If the boostnote ID is a standard UUID, we can just strip out the hyphens.
    uuid4_prog = re.compile(
        r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"
    )
    if uuid4_prog.match(boostnote_id):
        return boostnote_id.replace("-", "")
    # Otherwise, the conversion is poorly defined. Generate a new ID.
    print(f"No direct conversion from boostnote ID {boostnote_id} to Joplin")
    return joplin_uuid()


def replace_boostnote_links_with_joplin_links(
    content: str, map_boostnote_to_joplin: dict
) -> str:
    def get_replacement(m: re.Match) -> str:
        boostnote_id = m.group(2)
        joplin_id = map_boostnote_to_joplin.get(boostnote_id)
        if joplin_id is None:
            print(f"Could not find replacement link for {joplin_id}")
            joplin_id = boostnote_id
        repl = f"[{m.group(1)}](:/{joplin_id})"
        print(f"Replaced link: {repl}")
        return repl

    prog = re.compile(r"\[([^\]]*)\]\(:note:([^\)]*)\)")
    return prog.sub(get_replacement, content)


col = boostnote.BoostnoteCollection.from_dir("/data/offline/notes")
output_location = tempfile.mktemp(suffix=".jex")
store = joplin.JoplinTarStore(output_location)
for folder_id in col.meta.list_folder_ids():
    folder_name = col.meta.get_folder_name(folder_id)
    print(f"Writing folder {folder_name} to Joplin store")
    joplin_entity = joplin.joplin_create_folder(folder_id, folder_name)
    payload = joplin.unparse_joplin_note(joplin_entity)
    store.write(f"{folder_id}.md", payload)


# create tags
tag_name_to_id = {}
for tag_name in col.list_tags():
    print(f"Writing tag to Joplin store: {tag_name}")
    tag_id = str(uuid.uuid4())
    tag_name_to_id[tag_name] = tag_id
    joplin_tag = joplin.joplin_create_tag(tag_id, tag_name)
    payload = joplin.unparse_joplin_note(joplin_tag)
    store.write(f"{tag_id}.md", payload)


boostnote_entities = list(col.get_entities())
map_boostnote_to_joplin = {}
for e in boostnote_entities:
    new_id = boostnote_to_joplin_id(e.id)
    map_boostnote_to_joplin[e.id] = new_id
    e.id = new_id

# create notes
for boostnote_entity in boostnote_entities:
    if not isinstance(boostnote_entity, boostnote.BoostnoteNote):
        continue

    print(f"Creating Joplin note for Boostnote note with ID {boostnote_entity.id}")
    joplin_entity = joplin.joplin_create_note(
        boostnote_entity.id,
        boostnote_entity.title,
        replace_boostnote_links_with_joplin_links(
            boostnote_entity.content, map_boostnote_to_joplin
        ),
        boostnote_entity.folder_id,
        boostnote_entity.created_at,
        boostnote_entity.updated_at,
    )
    # print(joplin_entity.headers)
    payload = joplin.unparse_joplin_note(joplin_entity)
    store.write(f"{boostnote_entity.id}.md", payload)
    # Create entities tagging notes
    for tag_name in boostnote_entity.tags:
        notetag_id = str(uuid.uuid4())
        tag_id = tag_name_to_id[tag_name]
        joplin_notetag_entity = joplin.joplin_create_notetag(
            notetag_id, boostnote_entity.id, tag_id
        )
        store.write(
            f"{notetag_id}.md", joplin.unparse_joplin_note(joplin_notetag_entity)
        )
        print(f"Wrote NoteTag with ID {notetag_id}")


print(f"Saved output to {output_location}")
