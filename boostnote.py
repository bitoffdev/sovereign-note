from collections import Counter
from dataclasses import dataclass
import datetime
import enum
import json
import traceback
from typing import Dict, Iterator, List, Set
import os

import cson

BOOSTNOTE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


class BoostnoteEntityType(enum.Enum):
    SNIPPET_NOTE = "SNIPPET_NOTE"
    MARKDOWN_NOTE = "MARKDOWN_NOTE"


@dataclass
class BoostnoteEntity:
    """Superclass for notes and snippets with shared fields"""
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    title: str
    folder_id: str
    tags: List[str]
    is_starred: bool
    is_trashed: bool


@dataclass
class BoostnoteNote(BoostnoteEntity):
    content: str
    type_: str = "MARKDOWN_NOTE"


@dataclass
class BoostnoteSnippet(BoostnoteEntity):
    description: str
    snippets: List
    type_: str = "SNIPPET_NOTE"



class BoostnoteMeta:
    """Reads Boostnote collection metadata from a `boostnote.json` file."""

    @classmethod
    def from_file(cls, filepath):
        with open(filepath) as fh:
            data = json.load(fh)
        self = cls()
        self.data = data
        return self

    @property
    def version(self):
        return self.data['version']

    def get_folder_name(self, folder_id: str):
        return next(filter(lambda row: row['key'] == folder_id, self.data['folders']))['name']

    def list_folder_ids(self) -> List[str]:
        return [folder['key'] for folder in self.data['folders']]

class BoostnoteCollection:
    @classmethod
    def from_dir(cls, dir_path: str):
        self = cls()
        self.dir_path = dir_path
        self.meta = BoostnoteMeta.from_file(os.path.join(dir_path, 'boostnote.json'))
        return self
    @staticmethod
    def _marshal_entity(id: str, dat: dict) -> BoostnoteEntity:
        if dat['type'] == BoostnoteEntityType.SNIPPET_NOTE.value:
            return BoostnoteSnippet(
                id=id,
                created_at=datetime.datetime.strptime(dat['createdAt'], BOOSTNOTE_DATE_FORMAT),
                updated_at=datetime.datetime.strptime(dat['updatedAt'], BOOSTNOTE_DATE_FORMAT),
                folder_id=dat['folder'],
                title=dat['title'],
                tags=dat['tags'],
                description=dat['description'],
                snippets=dat['snippets'],
                is_starred=dat['isStarred'],
                is_trashed=dat['isTrashed'],
            )
        assert dat['type'] == BoostnoteEntityType.MARKDOWN_NOTE.value

        return BoostnoteNote(
            id=id,
            created_at=datetime.datetime.strptime(dat['createdAt'], BOOSTNOTE_DATE_FORMAT),
            updated_at=datetime.datetime.strptime(dat['updatedAt'], BOOSTNOTE_DATE_FORMAT),
            # type_=dat['type'],
            folder_id=dat['folder'],
            title=dat['title'],
            tags=dat['tags'],
            content=dat['content'],
            is_starred=dat['isStarred'],
            is_trashed=dat['isTrashed'],
        )
    def get_entity_paths(self) -> List[str]:
        notes_dir = os.path.join(self.dir_path, 'notes')
        return list(map(lambda f: os.path.join(notes_dir, f), os.listdir(notes_dir)))
    def get_entities(self) -> Iterator[BoostnoteEntity]:
       for note_path in self.get_entity_paths():
           try:
               note_id = os.path.basename(note_path).rsplit('.', 1)[0]
               with open(note_path) as fh:
                   dat = cson.load(fh)
                   yield self._marshal_entity(note_id, dat)
           except cson.ParseError:
               print(f"CSON parsing failed for note: {note_path}")
           except Exception as exc:
               print(exc)
               traceback.print_exc()
               print(f"Bad note: {note_path}")
    def list_tags(self) -> Set[str]:
        tags = set()
        for entity in self.get_entities():
            tags.update(entity.tags)
        return tags
    def stats(self):
        counts = Counter()
        for entity in self.get_entities():
            counts.update({
                "notes": 1 if isinstance(entity, BoostnoteNote) else 0,
                "snippets": 1 if isinstance(entity, BoostnoteSnippet) else 0,
                "starred": 1 if entity.is_starred else 0,
                "trashed": 1 if entity.is_trashed else 0,
            })
        return counts


