"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Literal
import warnings

import vastorbit._config.config as conf

if conf.get_import_success("IPython"):
    from IPython.display import display, HTML, Markdown


def print_message(
    message: str, mtype: Literal["print", "warning", "display", "markdown"] = "print"
) -> None:
    """
    Prints the input message or warning.
    This function is used to manage the
    verbosity.
    """
    mtype = mtype.lower().strip()
    if mtype == "warning" and conf.get_option("verbosity") >= 1:
        warnings.warn(message, Warning)
    elif (
        mtype == "print"
        and conf.get_option("print_info")
        and conf.get_option("verbosity") >= 2
    ):
        print(message)
    elif (
        mtype in ("display", "markdown")
        and conf.get_option("print_info")
        and conf.get_option("verbosity") >= 2
    ):
        if conf.get_import_success("IPython"):
            try:
                if mtype == "markdown":
                    display(Markdown(message))
                else:
                    display(HTML(message))
            except:
                display(message)
        else:
            print(message)
