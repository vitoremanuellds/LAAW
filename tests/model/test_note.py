"""Tests for laaw.model.note."""

import unittest

from laaw.model.note import Note


class NoteTest(unittest.TestCase):
    def test_given_note_when_word_count_then_counts_whitespace_tokens(self):
        # arrange
        note = Note(tag="decision", text="we  used   refresh tokens")
        # act
        count = note.word_count()
        # assert
        self.assertEqual(count, 4)

    def test_given_empty_note_when_word_count_then_zero(self):
        # arrange
        note = Note(tag="other", text="")
        # act
        count = note.word_count()
        # assert
        self.assertEqual(count, 0)

    def test_given_note_dict_when_from_dict_then_round_trips(self):
        # arrange
        note = Note(tag="gotcha", text="watch out for the edge case")
        # act
        restored = Note.from_dict(note.to_dict())
        # assert
        self.assertEqual(restored, note)


if __name__ == "__main__":
    unittest.main()
