"""
SPDX-License-Identifier: Apache-2.0
"""

from vastorbit.core.vastframe.base import VastFrame

"""
Sample Datasets to do testing.
"""


def load_dataset_cl() -> VastFrame:
    """
    Returns the classification dataset.

    This dataset is ideal for classification.
    If a table with the same name and schema already exists,
    this function creates a VastFrame from the input relation.

    Returns
    -------
    VastFrame
        The classification VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_dataset_cl

        vdf = load_dataset_cl()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_dataset_cl

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_dataset_cl.html", "w")
        html_file.write(
            load_dataset_cl()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_dataset_cl.html
    """

    # Classification Dataset

    data = [
        [1, "Bus", "Male", 0, "Cheap", "Low"],
        [2, "Bus", "Male", 1, "Cheap", "Med"],
        [3, "Train", "Female", 1, "Cheap", "Med"],
        [4, "Bus", "Female", 0, "Cheap", "Low"],
        [5, "Bus", "Male", 1, "Cheap", "Med"],
        [6, "Train", "Male", 0, "Standard", "Med"],
        [7, "Train", "Female", 1, "Standard", "Med"],
        [8, "Car", "Female", 1, "Expensive", "Hig"],
        [9, "Car", "Male", 2, "Expensive", "Med"],
        [10, "Car", "Female", 2, "Expensive", "Hig"],
    ]
    return VastFrame(data)


def load_dataset_reg() -> VastFrame:
    """
    Returns the regression dataset.

    Returns
    -------
    VastFrame
        The regression VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_dataset_reg

        vdf = load_dataset_reg()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_dataset_reg

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_dataset_reg.html", "w")
        html_file.write(
            load_dataset_cl()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_dataset_reg.html
    """

    # Regression Dataset

    data = [
        [1, 0, "Male", 0, "Cheap", "Low"],
        [2, 0, "Male", 1, "Cheap", "Med"],
        [3, 1, "Female", 1, "Cheap", "Med"],
        [4, 0, "Female", 0, "Cheap", "Low"],
        [5, 0, "Male", 1, "Cheap", "Med"],
        [6, 1, "Male", 0, "Standard", "Med"],
        [7, 1, "Female", 1, "Standard", "Med"],
        [8, 2, "Female", 1, "Expensive", "Hig"],
        [9, 2, "Male", 2, "Expensive", "Med"],
        [10, 2, "Female", 2, "Expensive", "Hig"],
    ]
    return VastFrame(data)


def load_dataset_num() -> VastFrame:
    """
    Returns the numerical dataset.

    Returns
    -------
    VastFrame
        The numerical VastFrame.

    Examples
    --------
    .. code-block:: python

        from vastorbit.datasets import load_dataset_num

        vdf = load_dataset_num()

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_dataset_num

        html_file = open("SPHINX_DIRECTORY/figures/datasets_loaders_load_dataset_num.html", "w")
        html_file.write(
            load_dataset_num()._repr_html_()
        )
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/datasets_loaders_load_dataset_num.html
    """

    # Numerical Dataset

    data = [
        [1, 7.2, 3.6, 6.1, 2.5],
        [2, 7.7, 2.8, 6.7, 2.0],
        [3, 7.7, 3.0, 6.1, 2.3],
        [4, 7.9, 3.8, 6.4, 2.0],
        [5, 4.4, 2.9, 1.4, 0.2],
        [6, 4.6, 3.6, 1.0, 0.2],
        [7, 4.7, 3.2, 1.6, 0.2],
        [8, 6.5, 2.8, 4.6, 1.5],
        [9, 6.8, 2.8, 4.8, 1.4],
        [10, 7.0, 3.2, 4.7, 1.4],
    ]

    return VastFrame(data)
