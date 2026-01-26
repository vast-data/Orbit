"""
SPDX-License-Identifier: Apache-2.0
"""

# VAST
from vastorbit.tests.plotting.base_test_files import VDCRangeCurve, VDFRangeCurve

# Testing variables
TIME_COL = "date"
COL_NAME_1 = "value"


class TestHighchartsVDCRangeCurve(VDCRangeCurve):
    """
    Testing different attributes of range curve plot on a VastColumn
    """


class TestHighchartsVDFRangeCurve(VDFRangeCurve):
    """
    Testing different attributes of range curve plot on a VastFrame
    """
