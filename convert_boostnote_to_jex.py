import tempfile

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
for boostnote_entity in col.get_entities():
    if not isinstance(boostnote_entity, boostnote.BoostnoteNote):
        continue
    print(f"Creating Joplin note for Boostnote note with ID {boostnote_entity.id}")
    joplin_entity = joplin.joplin_create_note(boostnote_entity.id, boostnote_entity.title, boostnote_entity.content, boostnote_entity.folder_id, boostnote_entity.created_at, boostnote_entity.updated_at)
    # print(joplin_entity.headers)
    payload = joplin.unparse_joplin_note(joplin_entity)
    store.write(f"{boostnote_entity.id}.md", payload)

print(f"Saved output to {output_location}")

