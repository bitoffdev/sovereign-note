#!/usr/bin/env python3
import abc
import argparse
from collections import Counter
import datetime
import enum
import io
import mimetypes
import os
import tarfile
from typing import Counter, Iterator, NamedTuple

JOPLIN_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


class JoplinMarkupLanguage(enum.Enum):
    # https://github.com/laurent22/joplin/blob/8063c94ff7133948604e7dc6bf0c13f8402e11ff/packages/renderer/MarkupToHtml.ts#L7
    Markdown = 1
    Html = 2


class JoplinModelType(enum.Enum):
    # https://github.com/laurent22/joplin/blob/8e55fe31eecdb9772ab1df8f020669b406918269/packages/lib/BaseModel.ts#L10
    Note = 1
    Folder = 2
    Setting = 3
    Resource = 4
    Tag = 5
    NoteTag = 6
    Search = 7
    Alarm = 8
    MasterKey = 9
    ItemChange = 10
    NoteResource = 11
    ResourceLocalState = 12
    Revision = 13
    Migration = 14
    SmartFilter = 15
    Command = 16


def _parse_model_type(text: str) -> JoplinModelType:
    return JoplinModelType(int(text))


class ParsedJoplinNote(NamedTuple):
    body: str
    headers: dict

    @property
    def model_type(self) -> JoplinModelType:
        return JoplinModelType(int(self.headers["type_"]))


class JoplinFolder(ParsedJoplinNote):
    @property
    def name(self):
        """Get the folder name"""
        return self.body


def parse_joplin_note(content: str) -> ParsedJoplinNote:
    parts = content.rsplit("\n\n", 1)
    if len(parts) == 2:
        raw_body, raw_headers = parts
    else:
        raw_body = ""
        raw_headers = parts[0]
    headers = {
        k: v.strip() for k, v in (row.split(":", 1) for row in raw_headers.split("\n"))
    }
    model_type = _parse_model_type(headers["type_"])
    # TODO If and only if the model type is 'Note', then we also need to parse out the title
    if model_type == JoplinModelType.Folder:
        return JoplinFolder(body=raw_body, headers=headers)
    return ParsedJoplinNote(body=raw_body, headers=headers)


def unparse_joplin_note(parsed: ParsedJoplinNote) -> str:
    serialized_headers = "\n".join(f"{k}: {v}" for k, v in parsed.headers.items())
    return f"{parsed.body}\n\n{serialized_headers}"


def joplin_create_folder(id: str, name: str) -> ParsedJoplinNote:
    return ParsedJoplinNote(
        body=name,
        headers={
            "id": id,
            "created_time": "2021-08-07T14:51:30.227Z",
            "updated_time": "2021-08-07T14:51:30.227Z",
            "user_created_time": "2021-08-07T14:51:30.227Z",
            "user_updated_time": "2021-08-07T14:51:30.227Z",
            "encryption_cipher_text": "",
            "encryption_applied": 0,
            "parent_id": "",
            "is_shared": 0,
            "share_id": "",
            "type_": JoplinModelType.Folder.value,
        },
    )


def joplin_create_tag(id: str, name: str) -> ParsedJoplinNote:
    return ParsedJoplinNote(
        body=name,
        headers={
            "id": id,
            "created_time": "2021-08-07T14:51:30.227Z",
            "updated_time": "2021-08-07T14:51:30.227Z",
            "user_created_time": "2021-08-07T14:51:30.227Z",
            "user_updated_time": "2021-08-07T14:51:30.227Z",
            "encryption_cipher_text": "",
            "encryption_applied": 0,
            "parent_id": "",
            "is_shared": 0,
            "share_id": "",
            "type_": JoplinModelType.Tag.value,
        },
    )


def joplin_create_notetag(id: str, note_id: str, tag_id: str) -> ParsedJoplinNote:
    return ParsedJoplinNote(
        body="",
        headers={
            "id": id,
            # "node_id": "d1da2d486ed44e528281bd499ecf57b6",
            "note_id": note_id,
            "tag_id": tag_id,
            "created_time": "2021-08-07T14:51:30.227Z",
            "updated_time": "2021-08-07T14:51:30.227Z",
            "user_created_time": "2021-08-07T14:51:30.227Z",
            "user_updated_time": "2021-08-07T14:51:30.227Z",
            "encryption_cipher_text": "",
            "encryption_applied": 0,
            "parent_id": "",
            "is_shared": 0,
            # "share_id": "",
            "type_": JoplinModelType.NoteTag.value,
        },
    )


def joplin_create_note(
    id: str,
    title: str,
    body: str,
    folder_id: str,
    created_time: datetime.datetime,
    updated_time: datetime.datetime,
) -> ParsedJoplinNote:
    return ParsedJoplinNote(
        body=f"{title}\n\n{body}",
        headers={
            "id": id,
            "parent_id": folder_id,
            "created_time": created_time.strftime(JOPLIN_DATE_FORMAT),
            "updated_time": updated_time.strftime(JOPLIN_DATE_FORMAT),
            "is_conflict": 0,
            "latitude": "0.00000000",
            "longitude": "0.00000000",
            "altitude": "0.0000",
            "author": "",
            "source_url": "",
            "is_todo": 0,
            "todo_due": 0,
            "todo_completed": 0,
            "source": "evernote",
            "source_application": "net.cozic.joplin-desktop",
            "application_data": "",
            "order": 0,
            "user_created_time": created_time.strftime(JOPLIN_DATE_FORMAT),
            "user_updated_time": created_time.strftime(JOPLIN_DATE_FORMAT),
            "encryption_cipher_text": "",
            "encryption_applied": 0,
            "markup_language": JoplinMarkupLanguage.Markdown.value,
            "is_shared": 0,
            "share_id": "",
            "conflict_original_id": "",
            "type_": JoplinModelType.Note.value,
        },
    )


def joplin_create_resource(id: str, original_name: str) -> ParsedJoplinNote:
    extension = original_name.rsplit(".", 1)[-1]
    mime = mimetypes.guess_type(original_name)[0]
    return ParsedJoplinNote(
        body=original_name,
        headers={
            "id": id,
            "mime": mime,
            "filename": "",  # It seems like the Joplin JEX exporter leaves this blank...
            "created_time": "2021-08-16T23:18:33.343Z",
            "updated_time": "2021-08-16T23:18:33.343Z",
            "user_created_time": "2021-08-16T23:18:33.343Z",
            "user_updated_time": "2021-08-16T23:18:33.343Z",
            "file_extension": extension,
            "encryption_cipher_text": "",
            "encryption_applied": 0,
            "encryption_blob_encrypted": 0,
            "size": 253631,
            "is_shared": 0,
            "share_id": "",
            "type_": JoplinModelType.Resource.value,
        },
    )


class Store(abc.ABC):
    @abc.abstractmethod
    def list(self, relative_path: str = ""):
        pass

    @abc.abstractmethod
    def read(self, relative_path: str):
        pass

    @abc.abstractmethod
    def write(self, relative_path: str, contents: str):
        pass

    @abc.abstractmethod
    def write_bin(self, relative_path: str, contents: bytes):
        pass


class JoplinRawStore(Store):
    def __init__(self, path: str):
        self._path = path

    def list(self, relative_path=""):
        return [
            p
            for p in os.listdir(os.path.join(self._path, relative_path))
            if os.path.isfile(p)
        ]

    def read(self, relative_path):
        with open(os.path.join(self._path, relative_path)) as fh:
            return fh.read()

    def write(self, relative_path, contents):
        with open(os.path.join(self._path, relative_path), "w") as fh:
            fh.write(contents)

    def write_bin(self, relative_path: str, contents: bytes):
        with open(os.path.join(self._path, relative_path), "wb") as fh:
            fh.write(contents)


def filter_object_keys(object_keys: Iterator[str], prefix: str = "") -> Iterator[str]:
    """
    Get object keys starting with prefix
    """
    for k in object_keys:
        # skip any keys that don't start with the prefix
        if k[: len(prefix)] != prefix:
            continue
        # skip child keys (with a slash not in the prefix)
        if "/" in k[len(prefix) :]:
            continue
        yield k


class JoplinTarStore(Store):
    def __init__(self, tar_path: str):
        self._tar_path = tar_path

    def list(self, relative_path: str = "") -> Iterator[str]:
        arc = tarfile.TarFile(self._tar_path, mode="r")
        names = list(filter_object_keys(arc.getnames(), relative_path))
        arc.close()
        return names

    def read(self, relative_path: str) -> str:
        arc = tarfile.TarFile(self._tar_path, mode="r")
        with arc.extractfile(relative_path) as fh:
            contents = fh.read().decode("utf-8")
        arc.close()
        return contents

    def write(self, relative_path: str, contents: str):
        # create a bytes IO object and calculate its size
        fobj = io.BytesIO(contents.encode("utf-8"))
        fobj.seek(0, 2)
        size = fobj.tell()
        fobj.seek(0)

        info = tarfile.TarInfo(name=relative_path)
        # the "size" attribute of the TarInfo will be used to determine how
        # many bytes are read from `fileobj`, so it's quite important
        info.size = size

        arc = tarfile.TarFile(self._tar_path, mode="a")
        arc.addfile(info, fobj)
        arc.close()

    def write_bin(self, relative_path: str, contents: bytes):
        # create a bytes IO object and calculate its size
        fobj = io.BytesIO(contents)
        fobj.seek(0, 2)
        size = fobj.tell()
        fobj.seek(0)

        info = tarfile.TarInfo(name=relative_path)
        # the "size" attribute of the TarInfo will be used to determine how
        # many bytes are read from `fileobj`, so it's quite important
        info.size = size

        arc = tarfile.TarFile(self._tar_path, mode="a")
        arc.addfile(info, fobj)
        arc.close()


def store_get_stats(store: Store) -> Counter[JoplinModelType]:
    c = Counter()
    for p in store.list():
        try:
            n = parse_joplin_note(store.read(p))
            c.update({n.model_type: 1})
        except Exception:
            print(f"Could not parse {p}")
    return c


def install_parser(parser: argparse.ArgumentParser) -> None:
    pass


def main():
    parser = argparse.ArgumentParser()
    install_parser(parser)
    parser.parse_args()

    s = JoplinRawStore(".")
    print(store_get_stats(s))


if __name__ == "__main__":
    main()
