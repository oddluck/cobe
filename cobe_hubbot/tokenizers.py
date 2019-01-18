import re
import Stemmer


class MegaHALTokenizer:
    """
    A traditional MegaHAL style tokenizer.
    This considers any of theseto be a token:
        * one or more consecutive alpha characters (plus apostrophe)
        * one or more consecutive numeric characters
        * one or more consecutive punctuation/space characters (not apostrophe)

    This tokenizer ignores differences in capitalization.
    """

    def split(self, phrase):
        if len(phrase) == 0:
            return []

        # add ending punctuation if it is missing
        if phrase[-1] not in ".!?":
            phrase = phrase + "."

        words = re.findall("([A-Z']+|[0-9]+|[^A-Z'0-9]+)", phrase.upper(),
                           re.UNICODE)
        return words

    def join(self, words):
        """
        Capitalize the first alpha character in the reply
        and the first alpha character that follows one of [.?!] and a space.
        """
        chars = list("".join(words))
        start = True

        for i in range(len(chars)):
            char = chars[i]
            if char.isalpha():
                if start:
                    chars[i] = char.upper()
                else:
                    chars[i] = char.lower()

                start = False
            else:
                if i > 2 and chars[i - 1] in ".?!" and char.isspace():
                    start = True

        return "".join(chars)


class CobeTokenizer:
    """
    A tokenizer that is somewhat improved from MegaHAL.
    These are considered tokens:
        * one or more consecutive Unicode word characters (plus apostrophe and dash)
        * one or more consecutive Unicode non-word characters, possibly with internal whitespace
        * the whitespace between word or non-word tokens
        * an HTTP url, [word]: followed by any run of non-space characters.

    This tokenizer collapses multiple spaces in a whitespace token into a single space character.
    It preserves differences in case. foo, Foo, and FOO are different tokens.
    """

    def __init__(self):
        # Add hyphen to the list of possible word characters, so hyphenated
        # words become one token (e.g. hy-phen). But don't remove it from
        # the list of non-word characters, so if it's found entirely within
        # punctuation it's a normal non-word (e.g. :-( )

        self.regex = re.compile(r"(\w+://\S+"             # urls
                                r"|[\w'-]+"               # words
                                r"|[^\w\s][^\w]*[^\w\s]"  # multiple punctuation
                                r"|[^\w\s]"               # a single punctuation character
                                r"|\s+)",                 # whitespace
                                re.UNICODE)

    def split(self, phrase):
        # Strip leading and trailing whitespace. This might not be the
        # correct choice long-term, but in the brain it prevents edges
        # from the root node that have has_space set.
        phrase = phrase.strip()

        if len(phrase) == 0:
            return []

        tokens = self.regex.findall(phrase)

        # collapse runs of whitespace into a single space
        space = " "
        for i, token in enumerate(tokens):
            if token[0] == " " and len(token) > 1:
                tokens[i] = space

        return tokens

    def join(self, words):
        return "".join(words)


class CobeStemmer:
    def __init__(self, name):
        # use the PyStemmer Snowball stemmer bindings
        self.stemmer = Stemmer.Stemmer(name)

    def stem(self, token):
        if not re.search(r"\w", token, re.UNICODE):
            return self.stem_nonword(token)

        # Don't preserve case when stemming, i.e. create lowercase stems.
        # This will allow us to create replies that switch the case of
        # input words, but still generate the reply in context with the
        # generated case.

        stem = self.stemmer.stemWord(token.lower())

        return stem

    def stem_nonword(self, token):
        # Stem common smile and frown emoticons down to :) and :(
        if re.search(r":-?[ )]*\)", token):
            return ":)"

        if re.search(r":-?[' (]*\(", token):
            return ":("
