"""
SPDX-License-Identifier: Apache-2.0
"""

from collections import namedtuple

AggregateFun = namedtuple("AggregateFun", ["vpy", "py"])
functions = {
    "aad": [
        "vo_data.aad()",
        "np.absolute(py_data - py_data.mean(numeric_only=True)).mean(numeric_only=True)",
    ],
    "count": ["vo_data.count()", "py_data.count()"],
    "cvar": [
        "vo_data.cvar()",
        "py_data[py_data >= py_data.quantile(0.95, numeric_only=True)].mean(numeric_only=True)",
    ],
    "iqr": [
        "vo_data.iqr()",
        "py_data.quantile(0.75, numeric_only=True) - py_data.quantile(0.25, numeric_only=True)",
    ],
    "kurt": ["vo_data.kurt()", "py_data.kurt(numeric_only=True)"],
    "kurtosis": [
        "vo_data.kurtosis()",
        "py_data.kurtosis(numeric_only=True)",
    ],
    "jb": ["vo_data.jb()", "jarque_bera(py_data, nan_policy='omit').statistic"],
    "mad": [
        "vo_data.mad()",
        "median_abs_deviation(py_data, nan_policy='omit')",
    ],
    "max": ["vo_data.max()", "py_data.max(numeric_only=True)"],
    "mean": ["vo_data.mean()", "py_data.mean(numeric_only=True)"],
    "avg": ["vo_data.avg()", "py_data.mean(numeric_only=True)"],
    "median": ["vo_data.median()", "py_data.median(numeric_only=True)"],
    "min": ["vo_data.min()", "py_data.min(numeric_only=True)"],
    "mode": ["vo_data.mode()", "py_data.mode(numeric_only=True, dropna=False).values"],
    "percent": ["vo_data.percent()", "py_data.count()/len(py_data)*100"],
    "quantile": [
        "vo_data.quantile(q=[0.2, 0.5])",
        "py_data.quantile(q=[0.2, 0.5],numeric_only=True).values",
    ],
    "10%": ["vo_data.q10()", "py_data.quantile(0.1, numeric_only=True)"],
    "90%": ["vo_data.q90", "py_data.quantile(0.9, numeric_only=True)"],
    "prod": ["vo_data.prod()", "py_data.prod(numeric_only=True)"],
    "product": ["vo_data.product()", "py_data.product(numeric_only=True)"],
    "range": [
        "vo_data.range()",
        "py_data.max(numeric_only=True) - py_data.min(numeric_only=True)",
    ],
    "sem": ["vo_data.sem()", "py_data.sem(numeric_only=True)"],
    "skew": ["vo_data.skew()", "py_data.skew(numeric_only=True)"],
    "skewness": ["vo_data.skewness()", "py_data.skew(numeric_only=True)"],
    "sum": ["vo_data.sum()", "py_data.sum(numeric_only=True)"],
    "std": ["vo_data.std()", "py_data.std(numeric_only=True)"],
    "stddev": ["vo_data.stddev()", "py_data.std(numeric_only=True)"],
    "topk": ["vo_data.topk(k=3)", "py_data.value_counts(dropna=False)"],
    "top1": ["vo_data.topk(k=1)", "py_data.value_counts(dropna=False).index[0]"],
    "top1_percent": [
        "vo_data.top1_percent()",
        "py_data.value_counts(dropna=False).iloc[0]/len(py_data)*100",
    ],
    "nunique": ["vo_data.nunique(approx=False)", "py_data.nunique()"],
    "unique": ["vo_data.nunique(approx=False)", "py_data.nunique()"],
    "var": ["vo_data.var()", "py_data.var(numeric_only=True)"],
    "variance": ["vo_data.variance()", "py_data.var(numeric_only=True)"],
    "value_counts": [
        "vo_data.value_counts()",
        "py_data.value_counts(dropna=False)",
    ],
    "distinct": [
        "vo_data.distinct()",
        "py_data.unique()",
    ],
}
