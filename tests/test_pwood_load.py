"""Tests for the .pwood loader."""

import zipfile
from collections.abc import Callable
from pathlib import Path

import pytest

from phrasewood import Session, load, play
from phrasewood.errors import LoadError
from phrasewood.pwood import schema
from phrasewood.pwood.frontmatter import split_frontmatter

REFERENCE = Path(__file__).resolve().parent.parent / "examples" / "the-lamplighters-debt"


def scripted(lines: list[str]) -> Callable[[], str | None]:
    it = iter(lines)
    return lambda: next(it, None)


def write_project(root: Path, files: dict[str, str]) -> Path:
    for relpath, text in files.items():
        target = root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


class TestLoadReferenceGame:
    def test_structure(self) -> None:
        tree = load(REFERENCE)
        assert tree.id == "the-lamplighters-debt"
        assert tree.title == "The Lamplighter's Debt"
        assert tree.start == "bridge"
        assert [f.name for f in tree.features] == ["trust"]
        # two entities, loaded from one list-form file (entities/cast.yaml)
        assert [e.id for e in tree.entities] == ["ferryman", "lantern"]
        assert tree.entities[0].features[0].default == "wary"
        assert tree.entities[1].kind == "thing"
        assert {b.id for b in tree.buds} == {"bridge", "ferry", "debt", "shore-warm", "shore-cold"}

    def test_bud_details_survive_loading(self) -> None:
        tree = load(REFERENCE)
        bridge = tree.bud("bridge")
        assert bridge.content.startswith("The bridge is out.")
        assert bridge.choices[0].label == "Offer your lantern as payment"
        assert bridge.choices[0].effect is not None  # the do string compiled
        assert tree.bud("debt").when == "false"

    def test_plays_to_the_warm_ending(self) -> None:
        out: list[str] = []
        session = play(load(REFERENCE), read=scripted(["1", "1", "1"]), write=out.append)
        assert session.is_over()
        assert "unquenched" in "\n".join(out)

    def test_plays_to_the_cold_ending(self) -> None:
        out: list[str] = []
        session = play(load(REFERENCE), read=scripted(["2", "1"]), write=out.append)
        assert session.is_over()
        assert "never knew" in "\n".join(out)


class TestFlexibleStructures:
    def test_single_entity_file(self, tmp_path: Path) -> None:
        write_project(
            tmp_path,
            {"pwood.yaml": "id: t\n", "entities/solo.yaml": "id: solo\nkind: place\n"},
        )
        tree = load(tmp_path)
        assert [e.id for e in tree.entities] == ["solo"]
        assert tree.entities[0].kind == "place"

    def test_list_of_entities_in_one_file(self, tmp_path: Path) -> None:
        write_project(
            tmp_path,
            {"pwood.yaml": "id: t\n", "entities/cast.yaml": "- id: a\n- id: b\n"},
        )
        assert [e.id for e in load(tmp_path).entities] == ["a", "b"]

    def test_entities_inline_in_manifest(self, tmp_path: Path) -> None:
        write_project(tmp_path, {"pwood.yaml": "id: t\nentities:\n  - id: a\n  - id: b\n"})
        assert [e.id for e in load(tmp_path).entities] == ["a", "b"]

    def test_features_inline_in_manifest(self, tmp_path: Path) -> None:
        write_project(
            tmp_path, {"pwood.yaml": "id: t\nfeatures:\n  hp:\n    type: int\n    default: 5\n"}
        )
        tree = load(tmp_path)
        assert [f.name for f in tree.features] == ["hp"]
        assert tree.features[0].default == 5

    def test_yaml_anchor_reuses_a_feature_shape(self, tmp_path: Path) -> None:
        cast = (
            "- id: c1\n"
            "  features:\n"
            "    mood: &m\n"
            "      type: enum\n"
            "      values: [wary, warm]\n"
            "      default: wary\n"
            "- id: c2\n"
            "  features:\n"
            "    mood: *m\n"
        )
        write_project(tmp_path, {"pwood.yaml": "id: t\n", "entities/cast.yaml": cast})
        tree = load(tmp_path)
        assert tree.entities[0].features[0].default == "wary"
        assert tree.entities[1].features[0].default == "wary"  # the aliased shape


class TestLoadFromZip:
    def test_loads_a_pwood_zip(self, tmp_path: Path) -> None:
        archive = tmp_path / "game.pwood"
        with zipfile.ZipFile(archive, "w") as zf:
            for path in REFERENCE.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(REFERENCE).as_posix())

        tree = load(archive)
        assert tree.id == "the-lamplighters-debt"
        assert {b.id for b in tree.buds} == {"bridge", "ferry", "debt", "shore-warm", "shore-cold"}
        # and it still plays
        assert Session(tree).view().content.startswith("The bridge is out.")


class TestFrontmatter:
    def test_splits_frontmatter_and_body(self) -> None:
        front, body = split_frontmatter("---\nid: x\n---\nHello there", "f")
        assert front.strip() == "id: x"
        assert body.strip() == "Hello there"

    def test_missing_fence_raises(self) -> None:
        with pytest.raises(LoadError, match="frontmatter"):
            split_frontmatter("just prose, no fence", "f")


class TestCoercion:
    def test_bool_becomes_lowercase_string(self) -> None:
        # A YAML bool in an expression field must read as the expression's word.
        assert schema.as_str(False, "f") == "false"
        assert schema.as_str(True, "f") == "true"

    def test_as_bool_is_strict(self) -> None:
        assert schema.as_bool(True, "f") is True
        with pytest.raises(LoadError):
            schema.as_bool("yes", "f")  # the Norway problem, refused

    def test_as_int_rejects_bool(self) -> None:
        with pytest.raises(LoadError):
            schema.as_int(True, "f")


class TestLoadErrors:
    def test_missing_manifest(self, tmp_path: Path) -> None:
        write_project(tmp_path, {"buds/x.md": "---\nid: x\n---\nhi"})
        with pytest.raises(LoadError, match="pwood.yaml"):
            load(tmp_path)

    def test_unknown_feature_type(self, tmp_path: Path) -> None:
        write_project(
            tmp_path,
            {"pwood.yaml": "id: t\n", "features.yaml": "x:\n  type: frobnicate\n"},
        )
        with pytest.raises(LoadError, match="unknown feature type"):
            load(tmp_path)

    def test_bud_without_frontmatter(self, tmp_path: Path) -> None:
        write_project(tmp_path, {"pwood.yaml": "id: t\n", "buds/x.md": "just prose"})
        with pytest.raises(LoadError, match="frontmatter"):
            load(tmp_path)

    def test_missing_path(self) -> None:
        with pytest.raises(LoadError, match="no such path"):
            load("/definitely/not/here.pwood")
