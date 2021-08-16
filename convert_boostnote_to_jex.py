import tempfile
import uuid

import boostnote
import joplin


col = boostnote.BoostnoteCollection.from_dir('/data/offline/notes')
output_location = tempfile.mktemp(suffix='.jex')
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



# create notes
for boostnote_entity in col.get_entities():
    if not isinstance(boostnote_entity, boostnote.BoostnoteNote):
        continue
    print(f"Creating Joplin note for Boostnote note with ID {boostnote_entity.id}")
    joplin_entity = joplin.joplin_create_note(boostnote_entity.id, boostnote_entity.title, boostnote_entity.content, boostnote_entity.folder_id, boostnote_entity.created_at, boostnote_entity.updated_at)
    # print(joplin_entity.headers)
    payload = joplin.unparse_joplin_note(joplin_entity)
    store.write(f"{boostnote_entity.id}.md", payload)
    # Create entities tagging notes
    for tag_name in boostnote_entity.tags:
        notetag_id = str(uuid.uuid4())
        tag_id = tag_name_to_id[tag_name]
        joplin_notetag_entity = joplin.joplin_create_notetag(notetag_id, boostnote_entity.id, tag_id)
        store.write(f"{notetag_id}.md", joplin.unparse_joplin_note(joplin_notetag_entity))
        print(f"Wrote NoteTag with ID {notetag_id}")


print(f"Saved output to {output_location}")

