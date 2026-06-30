"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal, Optional, TYPE_CHECKING

from vastorbit._utils._sql._collect import save_vastorbit_logs
from vastorbit._utils._gen import gen_name

from vastorbit.core.vastframe._rolling import vDFRolling
from vastorbit.core.vastframe._corr import vDCCorr

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


class vDFText(vDFRolling):
    @save_vastorbit_logs
    def regexp(
        self,
        column: str,
        pattern: str,
        method: Literal[
            "count",
            "ilike",
            "instr",
            "like",
            "not_ilike",
            "not_like",
            "replace",
            "substr",
        ] = "substr",
        position: int = 1,
        occurrence: int = 1,
        replacement: Optional[str] = None,
        return_position: int = 0,
        name: Optional[str] = None,
    ) -> "VastFrame":
        """
        Computes a new VastColumn based on regular expressions.

        Parameters
        ----------
        column: str
            Input VastColumn  used  to compute the  regular
            expression.
        pattern: str
            The regular expression.
        method: str, optional
            Method used to compute the regular  expressions.

                 - count:
                    Returns the number of times a
                    regular expression matches each
                    element of the input VastColumn.
                 - ilike:
                    Returns  True if  the  VastColumn
                    element  contains a match for  the
                    regular expression (case-insensitive).
                 - instr:
                    Returns  the  starting  position
                    in  a VastColumn element where a
                    regular expression matches.
                 - like:
                    Returns  True  if the  VastColumn
                    element    matches   the   regular
                    expression.
                 - not_ilike :
                    Returns  True  if the  VastColumn
                    element  does  not match the  case
                    -insensitive  regular   expression.
                 - not_like:
                    Returns  True if  the  VastColumn
                    element  does not contain a  match
                    for the regular expression.
                 - replace:
                    Replaces   all  occurrences  of  a
                    substring  that  match  a  regular
                    expression  with another substring.
                 - substr:
                    Returns the substring that matches
                    a  regular   expression  within  a
                    VastColumn.

        position: int, optional
            The number of characters from the start of the string
            where the function should start searching for matches.
        occurrence: int, optional
            Controls  which occurrence of a pattern match in  the
            string to return.
        replacement: str, optional
            The string to replace matched substrings.
        return_position: int, optional
            Sets the position within the string to return.
        name: str, optional
            New feature name. If empty, a name is generated.

        Returns
        -------
        VastFrame
            self

        Examples
        --------

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's generate a small dataset using the following data:

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "rollno": ['1', '2', '3', '4'],
                    "subjects": [
                        'English, Math',
                        'English, Math, Computer',
                        'Math, Computer, Science',
                        'Math, Science',
                    ],
                }
            )

        Let's retrieve the second subject.

        .. code-block:: python

            data.regexp(
                column = "subjects",
                pattern = "[^,]+",
                method = "substr",
                occurrence = 2,
                name = "subject_2").select(
                    [
                        "subjects",
                        "subject_2",
                    ]
                )

        .. ipython:: python
            :suppress:

            res = data.regexp(
                column = "subjects",
                pattern = "[^,]+",
                method = "substr",
                occurrence = 2,
                name = "subject_2").select(
                    [
                        "subjects",
                        "subject_2",
                    ]
                )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_regex1.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_regex1.html

        Let's count the number of subjects.

        .. code-block:: python

            data.regexp(
                column = "subjects",
                pattern = ",",
                method = "count",
                name = "nb_subjects",
            )
            data["nb_subjects"].add(1)
            data.select(["subjects", "nb_subjects"])

        .. ipython:: python
            :suppress:

            data.regexp(
                column = "subjects",
                pattern = ",",
                method = "count",
                name = "nb_subjects",
            )
            data["nb_subjects"].add(1)
            res = data.select(["subjects", "nb_subjects"])
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_regex2.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_regex2.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.eval` : Evaluates an expression.

        """
        column = self.format_colnames(column)
        pattern_str = pattern.replace("'", "''")

        if position and position > 1:
            target = f"SUBSTR({column}, {position})"
        else:
            target = column

        if method == "count":
            # Trino: regexp_count(string, pattern) -> bigint
            expr = f"REGEXP_COUNT({target}, '{pattern_str}')"

        elif method in ("like", "ilike"):

            if method == "ilike":
                pattern_str = f"(?i){pattern_str}"
            expr = f"REGEXP_LIKE({column}, '{pattern_str}')"

        elif method in ("not_like", "not_ilike"):
            # NOT REGEXP_LIKE
            if method == "not_ilike":
                pattern_str = f"(?i){pattern_str}"
            expr = f"NOT REGEXP_LIKE({column}, '{pattern_str}')"

        elif method == "substr":

            if occurrence and occurrence > 1:
                expr = (
                    f"ELEMENT_AT(REGEXP_EXTRACT_ALL({target}, "
                    f"'{pattern_str}'), {occurrence})"
                )
            else:
                expr = f"REGEXP_EXTRACT({target}, '{pattern_str}')"

        elif method == "replace":
            if replacement is None:
                replacement = ""
            replacement_str = replacement.replace("'", "''")

            if position and position > 1:
                prefix = f"SUBSTR({column}, 1, {position - 1})"
                body = (
                    f"REGEXP_REPLACE({target}, '{pattern_str}', "
                    f"'{replacement_str}')"
                )
                expr = f"CONCAT({prefix}, {body})"
            else:
                expr = (
                    f"REGEXP_REPLACE({column}, '{pattern_str}', "
                    f"'{replacement_str}')"
                )

        elif method == "instr":

            if position and position > 1 and occurrence and occurrence > 1:
                raw = (
                    f"REGEXP_POSITION({column}, '{pattern_str}', "
                    f"{position}, {occurrence})"
                )
            elif position and position > 1:
                raw = f"REGEXP_POSITION({column}, '{pattern_str}', {position})"
            else:
                raw = f"REGEXP_POSITION({column}, '{pattern_str}')"

            if return_position and return_position != 0:
                match_len = (
                    f"COALESCE(LENGTH(REGEXP_EXTRACT({target}, "
                    f"'{pattern_str}')), 0)"
                )
                expr = f"CASE WHEN {raw} = -1 THEN 0 " f"ELSE {raw} + {match_len} END"
            else:
                expr = f"CASE WHEN {raw} = -1 THEN 0 ELSE {raw} END"

        else:
            raise ValueError(f"Unsupported regex method: {method}")

        if not name:
            name = gen_name([method, column])

        return self.eval(name=name, expr=expr)


class vDCText(vDCCorr):
    @save_vastorbit_logs
    def str_contains(self, pat: str) -> "VastFrame":
        """
        Verifies  if the  regular expression  is in each of  the
        VastColumn records. The VastColumn will be transformed.

        Parameters
        ----------
        pat: str
            Regular expression.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo


        Let's generate a small dataset using the following data:

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "rollno": ['1', '2', '3', '4'],
                    "subjects": [
                        'English, Math',
                        'English, Math, Computer',
                        'Math, Computer, Science',
                        'Math, Science',
                    ],
                }
            )

        Let's check if subjects contain "English".

        .. code-block:: python

            data["subjects"].str_contains(pat = "English").select(
                [
                    "rollno",
                    "subjects as has_english",
                ]
            )

        .. ipython:: python
            :suppress:

            res = data["subjects"].str_contains(pat = "English").select(
                [
                    "rollno",
                    "subjects as has_english",
                ]
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_str_contains.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_str_contains.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_count` : Counts occurrences matching the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_extract` : Extracts the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_replace` : Replaces the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_slice` : Slices the Regular Expression.
        """
        pat = pat.replace("'", "''")
        # Use REGEXP_LIKE for pattern matching
        return self.apply(func=f"REGEXP_LIKE({{}}, '{pat}')")

    @save_vastorbit_logs
    def str_count(self, pat: str) -> "VastFrame":
        """
        Computes the number of matches for the regular expression in
        each  record  of  the VastColumn.  The VastColumn will  be
        transformed.

        Parameters
        ----------
        pat: str
            regular expression.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's generate a small dataset using the following data:

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "rollno": ['1', '2', '3', '4'],
                    "subjects": [
                        'English, Math',
                        'English, Math, Computer',
                        'Math, Computer, Science',
                        'Math, Science',
                    ],
                }
            )

        Let's count number of times "English" appears in "subjects"
        VastColumn.

        .. code-block:: python

            data["subjects"].str_count(pat = "English").select(
                [
                    "rollno",
                    "subjects as english_count",
                ]
            )

        .. ipython:: python
            :suppress:

            res = data["subjects"].str_count(pat = "English").select(
                [
                    "rollno",
                    "subjects as english_count",
                ]
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_str_count.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_str_count.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_contains` : Validates the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_extract` : Extracts the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_replace` : Replaces the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_slice` : Slices the Regular Expression.
        """
        pat = pat.replace("'", "''")
        # REGEXP_COUNT(string, pattern) → bigint
        return self.apply(func=f"REGEXP_COUNT({{}}, '{pat}')")

    @save_vastorbit_logs
    def str_extract(self, pat: str) -> "VastFrame":
        """
        Extracts  the regular  expression in  each record of
        the VastColumn. The VastColumn will be transformed.

        Parameters
        ----------
        pat: str
            regular expression.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo


        Let's generate a small dataset using the following data:

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "name": [
                        'Mr. Steve Smith',
                        'Mr. Charlie Dickens',
                        'Mrs. Helen Ross',
                        'Dr. Jack Smith',
                    ]
                }
            )

        Let's extract the name prefix.

        .. code-block:: python

            data["name"].str_extract(pat = r"([A-Za-z])+\\.")

        .. ipython:: python
            :suppress:
            :okwarning:

            res = data["name"].str_extract(pat = r"([A-Za-z])+\\.")
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_str_extract.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_str_extract.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_contains` : Validates the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_count` : Counts occurrences matching the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_replace` : Replaces the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_slice` : Slices the Regular Expression.
        """
        pat = pat.replace("'", "''")
        # REGEXP_EXTRACT(string, pattern) → varchar
        return self.apply(func=f"REGEXP_EXTRACT({{}}, '{pat}')")

    @save_vastorbit_logs
    def str_replace(self, to_replace: str, value: Optional[str] = None) -> "VastFrame":
        """
        Replaces  the  regular expression matches in each  of  the
        VastColumn record by an input value. The VastColumn will
        be transformed.

        Parameters
        ----------
        to_replace: str
            Regular expression to replace.
        value: str, optional
            New value.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo

        Let's generate a small dataset using the following data:

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "name": [
                        'Mr. Steve Smith',
                        'Mr. Charlie Dickens',
                        'Mrs. Helen Ross',
                        'Dr. Jack Smith',
                    ]
                }
            )

        Let's replace the name prefix with static text
        "[Name_Prefix]".

        .. code-block:: python

            data["name"].str_replace(
                to_replace  = r"([A-Za-z])+\\.",
                value = "[Name_Prefix]"
            )

        .. ipython:: python
            :suppress:
            :okwarning:

            res = data["name"].str_replace(
                to_replace  = r"([A-Za-z])+\\.",
                value = "[Name_Prefix]"
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_str_replace.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_str_replace.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_contains` : Validates the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_count` : Counts occurrences matching the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_extract` : Extracts the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_slice` : Slices the Regular Expression.
        """
        to_replace = to_replace.replace("'", "''")
        if value is None:
            value = ""
        value = value.replace("'", "''")
        # REGEXP_REPLACE(string, pattern, replacement) → varchar
        return self.apply(func=f"REGEXP_REPLACE({{}}, '{to_replace}', '{value}')")

    @save_vastorbit_logs
    def str_slice(self, start: int, step: int) -> "VastFrame":
        """
        Slices the VastColumn. The VastColumn will be transformed.

        Parameters
        ----------
        start: int
            Start of the slicing (1-indexed).
        step: int
            Size of the slicing.

        Returns
        -------
        VastFrame
            self._parent

        Examples
        ---------

        Let's begin by importing `vastorbit`.

        .. ipython:: python

            import vastorbit as vo


        Let's generate a small dataset using the following data:

        .. ipython:: python

            data = vo.VastFrame(
                {
                    "name": [
                        'Mr. Steve Smith',
                        'Mr. Charlie Dickens',
                        'Mrs. Helen Ross',
                        'Dr. Jack Smith',
                    ]
                }
            )

        Let's extract the first 3 characters of name.

        .. code-block:: python

            data["name"].str_slice(start = 1, step = 3)

        .. ipython:: python
            :suppress:

            res = data["name"].str_slice(start = 1, step = 3)
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_text_str_slice.html", "w")
            html_file.write(res._repr_html_())
            html_file.close()

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_text_str_slice.html

        .. seealso::

            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_contains` : Validates the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_count` : Counts occurrences matching the regular expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_replace` : Replaces the Regular Expression.
            | ``VastFrame.``:py:meth:`~vastorbit.VastFrame.str_extract` : Extracts the Regular Expression.
        """
        # SUBSTR(string, start) → varchar
        # SUBSTR(string, start, length) → varchar
        if start == 0:
            start = 1
        return self.apply(func=f"SUBSTR({{}}, {start}, {step - 1})")
