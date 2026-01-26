"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.errors import ParsingError


def get_magic_options(line: str) -> dict:
    """
    Parses the input line and returns the dictionary
    of options.
    """

    # parsing the line
    i, n, splits = 0, len(line), []
    while i < n:
        while i < n and line[i] == " ":
            i += 1
        if i < n:
            k = i
            op = line[i]
            if op in ('"', "'"):
                i += 1
                while i < n - 1:
                    if line[i] == op and line[i + 1] != op:
                        break
                    i += 1
                i += 1
                quote_in = True
            else:
                while i < n and line[i] != " ":
                    i += 1
                quote_in = False
            if quote_in:
                splits += [line[k + 1 : i - 1]]
            else:
                splits += [line[k:i]]

    # Creating the dictionary
    n, i, options_dict = len(splits), 0, {}
    while i < n:
        if splits[i][0] != "-":
            raise ParsingError(
                f"Can not parse option '{splits[i][0]}'. "
                "Options must start with '-'."
            )
        options_dict[splits[i]] = splits[i + 1]
        i += 2

    return options_dict
