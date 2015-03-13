#! /usr/bin/env python
# coding:utf-8

import re


class Preprocessing:

    def __init__(self):
        self.html_regex = re.compile(
            r'(http|https)://[a-zA-Z0-9-./"#$%&\':?=_]+')
        self.newline_regex = re.compile(r'\n')
        self.cont_spaces_regex = re.compile(r'\s+')

    def _subs(self, regex: "re obj", repl: str, text: str):
        return regex.sub(repl, text)

    def remove_link(self, text: str) -> str:
        return self._subs(self.html_regex, "", text)

    def remove_newline(self, text: str) -> str:
        return self._subs(self.newline_regex, "", text)

    def remove_spaces(self, text: str) -> str:
        return self._subs(self.cont_spaces_regex, "", text)

    def convert_cont_spaces(self, text: str) -> str:
        return self._subs(self.cont_spaces_regex, " ", text)

    def strip(self, text: str) -> str:
        return text.strip()

    def convert(self, text: str) -> str:
        funcs = [
            self.remove_newline,
            self.remove_link,
            self.convert_cont_spaces,
            self.strip]
        _text = text
        for func in funcs:
            _text = func(_text)
        return _text


class TwitterPreprocessing(Preprocessing):

    def __init__(self):
        Preprocessing.__init__(self)
        username = r'@[a-zA-Z0-9_]+'
        tag = r'#[a-zA-Z0-9_]+'
        self.mention_regex = re.compile(r'{}'.format(username))
        self.retweet_regex = re.compile(r'RT {}:'.format(username))
        self.tag_regex = re.compile(r'{}'.format(tag))

    def remove_mention(self, text: str) -> str:
        return self._subs(self.mention_regex, "", text)

    def remove_retweet(self, text: str) -> str:
        return self._subs(self.retweet_regex, "", text)

    def remove_tag(self, text: str) -> str:
        return self._subs(self.tag_regex, "", text)

    def convert(self, text: str) -> str:
        funcs = [
            self.remove_newline,
            self.remove_link,
            self.remove_retweet,
            self.remove_mention,
            self.remove_tag,
            self.convert_cont_spaces,
            self.strip]
        _text = text

        for func in funcs:
            _text = func(_text)

        return _text


class KyTeaPreprocessing(TwitterPreprocessing):
    def __init__(self):
        TwitterPreprocessing.__init__(self)

    def _convert_slash(self, xs: str) -> str:
        """
        形態素解析のため
        """
        slash_regex = r"/"
        return re.sub(slash_regex, "／", xs)

    def convert(self, xs: str) -> str:
        # TwitterPreprocess.convert
        # に加えて
        #
        # *   空白の削除
        # *   slash の削除
        #
        # を行う
        #
        # Do
        #   remove_newline
        #   remove_link
        #   remove_retweet
        #   remove_mention
        #   remove_tag
        #   convert_cont_spaces
        #   strip
        #
        #   remove spaces
        convtw = TwitterPreprocessing.convert(self, xs)
        for func in [
                self.remove_spaces,
                self._convert_slash,
        ]:
            convtw = func(convtw)

        return convtw
