"""
SPDX-License-Identifier: Apache-2.0
"""

from typing import Union

import matplotlib.animation as animation
import matplotlib.pyplot as plt

import vastorbit._config.config as conf

from vastorbit.plotting._matplotlib.base import MatplotlibBase

if conf.get_import_success("IPython"):
    from IPython.display import HTML


class AnimatedBase(MatplotlibBase):
    @staticmethod
    def _return_animation(a: animation.Animation) -> Union["HTML", animation.Animation]:
        if conf.get_import_success("IPython"):
            anim = a.to_jshtml()
            plt.close("all")
            return HTML(anim)
        else:
            return a
