#! /usr/bin/env python
# coding:utf-8

import chartype


class JapaneseFilter:
    def _is_nihongo(self, s):
        ct = chartype.Chartype()
        allowed_chars = {"！", "？"}
        try:
            # CharType が
            #   ValueError: no such name
            # をだす可能性がある
            return all(
                ct.is_nihongo(char) or
                ct.is_ascii(char) or
                char in allowed_chars for char in s
            )
        except:
            return False

    def is_passed(self, text):
        """
        フィルターされない
        """
        return self._is_nihongo(text) and text

    def filter(self, lines: [str]) -> [str]:
        for text in lines:
            if self.is_passed(text):
                yield text
