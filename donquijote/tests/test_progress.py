from datetime import datetime as dt
from datetime import timedelta as td

import pytest

from donquijote.bot.conversationbot import SRS_DICT, progress


@pytest.mark.parametrize("level", [(1), (2), (3), (4)])
def test_correct(level):
    """
    Tests that the 'progress' function correctly increments the level and sets the next_learn attribute of an SRS item.

    Args:
        level (int): The initial level of the SRS item.

    Returns:
        None
    """
    srs_item = {
        "user_id": 463338589,
        "vocab_id": 867,
        "level": level,
        "last_learn": None,
        "next_learn": None,
        "quick_repeat": False,
    }

    srs_item = progress(srs_item, 1)

    assert srs_item["level"] == level + 1

    if level < 4:
        assert srs_item["next_learn"] == srs_item["last_learn"].replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + td(days=SRS_DICT[level + 1])
    else:
        assert srs_item["next_learn"] == dt(2099, 1, 1)


@pytest.mark.parametrize("level", [(1), (2), (3), (4)])
def test_incorrect(level):
    """
    Tests that the 'progress' function correctly decrements the level, sets the quick_repeat attribute to True,
    and sets the next_learn attribute of an SRS item to the current date plus one day.

    Args:
        level (int): The initial level of the SRS item.

    Returns:
        None
    """
    srs_item = {
        "user_id": 463338589,
        "vocab_id": 867,
        "level": level,
        "last_learn": None,
        "next_learn": None,
        "quick_repeat": False,
    }

    srs_item = progress(srs_item, 2)

    assert srs_item["next_learn"] == srs_item["last_learn"].replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + td(days=1)

    if level == 1:
        assert srs_item["level"] == 1
    else:
        assert srs_item["level"] == (level - 1)
        assert srs_item["quick_repeat"]


@pytest.mark.parametrize("level", [(2), (3)])
def test_correct_repeat(level):
    """
    Tests that the 'progress' function correctly sets the level and next_learn attribute of an SRS item to
    their initial values when the item has the quick_repeat attribute set to True.

    Args:
        level (int): The initial level of the SRS item.

    Returns:
        None
    """
    srs_item = {
        "user_id": 463338589,
        "vocab_id": 867,
        "level": level,
        "last_learn": None,
        "next_learn": None,
        "quick_repeat": True,
    }

    srs_item = progress(srs_item, 1)

    assert srs_item["level"] == level
    assert srs_item["next_learn"] == srs_item["last_learn"].replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + td(days=SRS_DICT[level])


@pytest.mark.parametrize("level", [(1), (2), (3), (4)])
def test_incorrect_repeat(level):
    """
    Tests that the 'progress' function correctly sets the next_learn attribute of an SRS item to the
    current date plus one day, and sets the level and quick_repeat attributes to their initial values,
    when the item has the quick_repeat attribute set to True.

    Args:
        level (int): The initial level of the SRS item.

    Returns:
        None
    """
    srs_item = {
        "user_id": 463338589,
        "vocab_id": 867,
        "level": level,
        "last_learn": None,
        "next_learn": None,
        "quick_repeat": True,
    }

    srs_item = progress(srs_item, 2)

    assert srs_item["next_learn"] == srs_item["last_learn"].replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + td(days=1)

    if level == 1:
        assert srs_item["level"] == 1
        assert srs_item["quick_repeat"]
    else:
        assert srs_item["level"] == level - 1
        assert srs_item["quick_repeat"]
