import datetime
import enum
import json
import os
import pathlib
import traceback
from collections import Counter
from contextlib import suppress
from dataclasses import dataclass
from typing import Iterator, List, Set

import cson

from ..util import get_child_paths

BOOSTNOTE_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def to_utc(dt):
    if not dt.tzinfo:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return (dt - dt.utcoffset()).replace(tzinfo=datetime.timezone.utc)


def boostnote_format_date(dt):
    # XXX In order show milliseconds only, we specify that we want microseconds
    # (`%f`) and then strip off the last three characters.
    return to_utc(dt).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


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


@dataclass
class BoostnoteAttachment:
    """
    relative_path: path within the attachments directory
    """

    relative_path: str

    @property
    def filename(self):
        return os.path.basename(self.relative_path)

    def __hash__(self):
        # From Python documentation: The only required property is that objects
        # which compare equal have the same hash value; it is advised to mix
        # together the hash values of the components of the object that also
        # play a part in comparison of objects by packing them into a tuple and
        # hashing the tuple.
        return hash(self.relative_path)


class BoostnoteMeta:
    """Reads Boostnote collection metadata from a `boostnote.json` file."""

    DEFAULT_VERSION = "1.0"

    @classmethod
    def create(cls):
        """Create a new metadata object"""
        self = cls()
        self.data = {"version": cls.DEFAULT_VERSION, "folders": []}
        return self

    @classmethod
    def from_file(cls, filepath):
        with open(filepath) as fh:
            data = json.load(fh)
        self = cls()
        self.data = data
        return self

    def write_to_file(self, filepath):
        with open(filepath, "w") as fh:
            json.dump(self.data, fh)

    @property
    def version(self):
        return self.data["version"]

    @version.setter
    def version(self, value: str):
        self.data["version"] = value

    def get_folder_name(self, folder_id: str) -> str:
        return next(filter(lambda row: row["key"] == folder_id, self.data["folders"]))[
            "name"
        ]

    def list_folder_ids(self) -> List[str]:
        return [folder["key"] for folder in self.data["folders"]]

    def add_folder(self, key: str, color: str, name: str):
        self.data["folders"].append({"key": key, "color": color, "name": name})


class BoostnoteCollection:
    @classmethod
    def create(cls, dir_path: str):
        """Create a new boostnote collection

        This should yield an error if the dir_path already exists and is not empty.
        """
        self = cls()
        self.dir_path = dir_path
        self.meta = BoostnoteMeta.create()
        return self

    @classmethod
    def from_dir(cls, dir_path: str):
        self = cls()
        self.dir_path = dir_path
        self.meta = BoostnoteMeta.from_file(os.path.join(dir_path, "boostnote.json"))
        return self

    @staticmethod
    def _serialize_entity(entity: BoostnoteEntity) -> dict:
        return {
            "type": BoostnoteEntityType.MARKDOWN_NOTE.value,
            "id": entity.id,
            "createdAt": boostnote_format_date(entity.created_at),
            "updatedAt": boostnote_format_date(entity.updated_at),
            "folder": entity.folder_id,
            "title": entity.title,
            "tags": entity.tags,
            "content": entity.content,
            "isStarred": entity.is_starred,
            "isTrashed": entity.is_trashed,
        }

    @staticmethod
    def _marshal_entity(id: str, dat: dict) -> BoostnoteEntity:
        if dat["type"] == BoostnoteEntityType.SNIPPET_NOTE.value:
            return BoostnoteSnippet(
                id=id,
                created_at=datetime.datetime.strptime(
                    dat["createdAt"], BOOSTNOTE_DATE_FORMAT
                ),
                updated_at=datetime.datetime.strptime(
                    dat["updatedAt"], BOOSTNOTE_DATE_FORMAT
                ),
                folder_id=dat["folder"],
                title=dat["title"],
                tags=dat["tags"],
                description=dat["description"],
                snippets=dat["snippets"],
                is_starred=dat["isStarred"],
                is_trashed=dat["isTrashed"],
            )
        assert dat["type"] == BoostnoteEntityType.MARKDOWN_NOTE.value

        return BoostnoteNote(
            id=id,
            created_at=datetime.datetime.strptime(
                dat["createdAt"], BOOSTNOTE_DATE_FORMAT
            ),
            updated_at=datetime.datetime.strptime(
                dat["updatedAt"], BOOSTNOTE_DATE_FORMAT
            ),
            # type_=dat['type'],
            folder_id=dat["folder"],
            title=dat["title"],
            tags=dat["tags"],
            content=dat["content"],
            is_starred=dat["isStarred"],
            is_trashed=dat["isTrashed"],
        )

    def get_entity_paths(self) -> List[str]:
        notes_dir = os.path.join(self.dir_path, "notes")
        return list(map(lambda f: os.path.join(notes_dir, f), os.listdir(notes_dir)))

    def get_entities(self) -> Iterator[BoostnoteEntity]:
        """Get all entities (ie. notes and code snippets) for this collection"""
        for note_path in self.get_entity_paths():
            try:
                note_id = os.path.basename(note_path).rsplit(".", 1)[0]
                with open(note_path) as fh:
                    dat = cson.load(fh)
                    yield self._marshal_entity(note_id, dat)
            except cson.ParseError:
                print(f"CSON parsing failed for note: {note_path}")
            except Exception as exc:
                print(exc)
                traceback.print_exc()
                print(f"Bad note: {note_path}")

    def add_entity(self, entity: BoostnoteEntity):
        notes_dir = os.path.join(self.dir_path, "notes")
        with suppress(FileExistsError):
            os.mkdir(notes_dir)
        note_path = os.path.join(notes_dir, f"{entity.id}.cson")
        with open(note_path, "w") as fh:
            cson.dump(self._serialize_entity(entity), fh)

    @property
    def _attachments_path(self):
        return os.path.join(self.dir_path, "attachments")

    def add_attachment(self, relpath: str, data: bytes):
        """
        :param relpath: Path relative to the attachments directory
        :param fh: File handle to read data from
        """
        attachment_path = os.path.join(self._attachments_path, relpath)
        pathlib.Path(attachment_path).parent.mkdir(parents=True, exist_ok=True)
        with open(attachment_path, "wb") as write_fh:
            write_fh.write(data)

    def get_attachments(self) -> Iterator[BoostnoteAttachment]:
        attachments_path = os.path.join(self.dir_path, "attachments")
        for note_relpath in get_child_paths(attachments_path):
            yield BoostnoteAttachment(note_relpath)

    def read_attachment(self, a: BoostnoteAttachment):
        with open(
            os.path.join(self.dir_path, "attachments", a.relative_path), "rb"
        ) as fh:
            return fh.read()

    def list_tags(self) -> Set[str]:
        tags = set()
        for entity in self.get_entities():
            tags.update(entity.tags)
        return tags

    def stats(self):
        counts = Counter()
        for entity in self.get_entities():
            counts.update(
                {
                    "notes": 1 if isinstance(entity, BoostnoteNote) else 0,
                    "snippets": 1 if isinstance(entity, BoostnoteSnippet) else 0,
                    "starred": 1 if entity.is_starred else 0,
                    "trashed": 1 if entity.is_trashed else 0,
                }
            )
        return counts
