"""
SPDX-License-Identifier: Apache-2.0
"""

import html
import shutil
from typing import Literal, Optional

import vastorbit._config.config as conf
from vastorbit._typing import NoneType
from vastorbit._utils._sql._cast import to_category
from vastorbit._utils._sql._format import format_type
from vastorbit._utils._logo import vastorbit_logo_html


def print_table(
    data_columns,
    is_finished: bool = True,
    offset: int = 0,
    repeat_first_column: bool = False,
    first_element: Optional[str] = None,
    return_html: bool = False,
    dtype: Optional[dict] = None,
    percent: Optional[dict] = None,
    col_formats: Optional[list[str]] = None,
) -> str:
    """
    Returns the HTML code or string used to display the final
    relation.
    """

    theme = conf.get_option("theme")
    if theme not in ("light", "dark", "sphinx"):
        raise ValueError("Unrecognized 'theme'.")

    maxwidth = conf.get_option("max_cellwidth")
    maxwidth = max(280, maxwidth)
    maxheight = conf.get_option("max_tableheight")
    maxheight = max(300, maxheight)

    # Main Function
    dtype, percent = format_type(dtype, percent, dtype=dict)
    if not return_html:
        data_columns_rep = [] + data_columns
        if repeat_first_column:
            del data_columns_rep[0]
            columns_ljust_val = min(
                len(max([str(item) for item in data_columns[0]], key=len)) + 4, 40
            )
        else:
            columns_ljust_val = len(str(len(data_columns[0]))) + 2
        screen_columns = shutil.get_terminal_size().columns
        formatted_text = ""
        rjust_val = []
        for idx in range(0, len(data_columns_rep)):
            rjust_val += [
                min(
                    len(max([str(item) for item in data_columns_rep[idx]], key=len))
                    + 2,
                    40,
                )
            ]
        total_column_len = len(data_columns_rep[0])
        while rjust_val != []:
            columns_to_print = [data_columns_rep[0]]
            columns_rjust_val = [rjust_val[0]]
            max_screen_size = int(screen_columns) - 14 - int(rjust_val[0])
            del data_columns_rep[0]
            del rjust_val[0]
            while (max_screen_size > 0) and (rjust_val != []):
                columns_to_print += [data_columns_rep[0]]
                columns_rjust_val += [rjust_val[0]]
                max_screen_size = max_screen_size - 7 - int(rjust_val[0])
                del data_columns_rep[0]
                del rjust_val[0]
            if repeat_first_column:
                columns_to_print = [data_columns[0]] + columns_to_print
            else:
                columns_to_print = [
                    [i + offset for i in range(0, total_column_len)]
                ] + columns_to_print
            columns_to_print[0][0] = first_element
            columns_rjust_val = [columns_ljust_val] + columns_rjust_val
            column_count = len(columns_to_print)
            for i in range(0, total_column_len):
                for k in range(0, column_count):
                    val = columns_to_print[k][i]
                    if len(str(val)) > 40:
                        val = str(val)[0:37] + "..."
                    if k == 0:
                        formatted_text += str(val).ljust(columns_rjust_val[k])
                    else:
                        formatted_text += str(val).rjust(columns_rjust_val[k]) + "  "
                if rjust_val != []:
                    formatted_text += " \\\\"
                formatted_text += "\n"
            if not is_finished and (i == total_column_len - 1):
                for k in range(0, column_count):
                    if k == 0:
                        formatted_text += "...".ljust(columns_rjust_val[k])
                    else:
                        formatted_text += "...".rjust(columns_rjust_val[k]) + "  "
                if rjust_val != []:
                    formatted_text += " \\\\"
                formatted_text += "\n"
        return formatted_text
    else:
        return _render_html_table(
            data_columns,
            theme=theme,
            offset=offset,
            repeat_first_column=repeat_first_column,
            maxheight=maxheight,
            maxwidth=maxwidth,
            dtype=dtype,
            percent=percent,
            col_formats=col_formats,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Modern HTML renderer
#
# Replaces the legacy per-cell inline-style table:
#   * class-based CSS emitted once per table (HTML is ~5-10x smaller)
#   * single scroll container + position:sticky header
#     (the old display:block <tbody> hack desynchronized column widths)
#   * text-overflow ellipsis + tooltip instead of readonly <input> cells
#   * VAST brand tokens; the "sphinx" theme uses Furo CSS variables so the
#     table adapts to the docs light/dark mode automatically
# ─────────────────────────────────────────────────────────────────────────────

_THEME_TOKENS = {
    "light": {
        "bg": "#FFFFFF",
        "head-bg": "#F8F9FB",  # VAST Navy header
        "index-bg": "#F8F9FB",
        "head-fg": "#10172D",
        "head-accent": "#1FD9FE",  # VAST Cyan edge
        "row": "#FFFFFF",
        "row-alt": "#F7FAFD",
        "row-hover": "#E2F9FF",
        "fg": "#10172D",
        "fg-muted": "#6B7A90",
        "null-fg": "#9AA7B8",
        "null-bg": "#F2F2F7",
        "line": "#E7EBF1",
        "index-fg": "#0E86B8",
        "index-bg": "#E2F9FF",  # nice light blue index column
        "row-line": "#E7EBF1",  # data-cell separator
        "type-num": "#0E86B8",
        "type-txt": "#6B7A90",
        "bar-track": "#E7EBF1",
        "bar-fill": "#1FD9FE",
        "shadow": "0 4px 16px rgba(3, 20, 44, 0.06)",
    },
    "dark": {
        "bg": "#03142C",
        "head-bg": "#03142C",
        "head-fg": "#E8EFF7",
        "head-accent": "#1FD9FE",
        "row": "#03142C",
        "row-alt": "#0A2240",
        "row-hover": "#11305A",
        "fg": "#E8EFF7",
        "fg-muted": "#9FB3C8",
        "null-fg": "#5F7186",
        "null-bg": "#0A2240",
        "line": "#03142C",  # no visible separation in dark (blends with bg)
        "index-fg": "#1FD9FE",
        "index-bg": "#11305A",  # uniform, a bit lighter than bg (dark)
        "row-line": "transparent",  # no border in data cells (dark)
        "type-num": "#1FD9FE",
        "type-txt": "#9FB3C8",
        "bar-track": "#11305A",
        "bar-fill": "#1FD9FE",
        "shadow": "none",
    },
    "sphinx": {  # Furo variables: adapts to the docs theme automatically
        "bg": "var(--color-background-primary, transparent)",
        "head-bg": "var(--color-background-secondary, #03142C)",
        "head-fg": "var(--color-foreground-primary, #E8EFF7)",
        "head-accent": "#1FD9FE",
        "row": "transparent",
        "row-alt": "var(--color-background-hover, rgba(31,217,254,0.04))",
        "row-hover": "var(--color-background-item, rgba(31,217,254,0.10))",
        "fg": "var(--color-foreground-primary, #888888)",
        "fg-muted": "var(--color-foreground-secondary, #888888)",
        "null-fg": "var(--color-foreground-muted, #999999)",
        "null-bg": "var(--color-background-hover, rgba(136,136,136,0.10))",
        "line": "var(--color-background-border, #555555)",
        "index-fg": "var(--color-brand-content, #1FD9FE)",
        "index-bg": "var(--color-background-secondary, #E2F9FF)",  # website look
        "row-line": "var(--color-background-border, #1B3A5C)",  # data-cell separator
        "type-num": "var(--color-brand-content, #1FD9FE)",
        "type-txt": "var(--color-foreground-secondary, #959DAD)",
        "bar-track": "var(--color-background-border, #555555)",
        "bar-fill": "#1FD9FE",
        "shadow": "none",
    },
}

_TYPE_GLYPHS = {
    "num": ("123", "type-num"),
    "bool": ("0|1", "type-num"),
    "text": ("Abc", "type-txt"),
    "date": ("&#128197;", "type-txt"),
    "spatial": ("&#x1f30e;", "type-txt"),
    "complex": ("&#128736;", "type-txt"),
}


def _table_css(t: dict, theme_name: str = "") -> str:
    """Scoped stylesheet for one rendered table."""
    # For the docs ("sphinx") palette only: in Furo DARK mode the index column
    # should match the main background (no distinct block) and the row
    # separators should disappear. Furo light keeps its light-blue index and
    # subtle separators. (These selectors only match inside Furo, so they have
    # no effect on the hard-coded notebook "light"/"dark" palettes.)
    dark_override = ""
    if theme_name == "sphinx":
        dark_override = (
            '\n[data-theme="dark"] .vob-table tbody td.vob-idx, '
            '[data-theme="dark"] .vob-table thead th.vob-idx '
            "{ background: #11305A !important; }"
            '\n[data-theme="dark"] .vob-table tbody td, '
            '[data-theme="dark"] .vob-table thead th '
            "{ border-color: transparent !important; }"
            "\n@media (prefers-color-scheme: dark) {"
            ' body:not([data-theme="light"]) .vob-table tbody td.vob-idx, '
            'body:not([data-theme="light"]) .vob-table thead th.vob-idx '
            "{ background: #11305A !important; }"
            ' body:not([data-theme="light"]) .vob-table tbody td, '
            'body:not([data-theme="light"]) .vob-table thead th '
            "{ border-color: transparent !important; } }"
        )
    return f"""<style>
{dark_override}
.vob-table {{
  --vt-bg: {t['bg']}; --vt-line: {t['line']}; --vt-shadow: {t['shadow']};
  border: 1px solid {t['line']}; border-radius: 10px; overflow: hidden;
  box-shadow: {t['shadow']}; background: {t['bg']};
  font-family: Moderat, Inter, 'Helvetica Neue', Arial, sans-serif;
  font-size: 13px; line-height: 1.4;
  /* Shrink-wrap to content: the table is as wide as its data needs to be,
     never stretched to fill the window. Scrolls when wider than it. */
  display: inline-block; max-width: 100%; vertical-align: top;
}}
.vob-table .vob-scroll {{ overflow: auto; max-height: var(--vt-maxh); }}
.vob-table table {{
  border-collapse: separate !important; border-spacing: 0; margin: 0;
  /* width/table-layout: content-driven, with !important to defeat notebook
     host CSS (Jupyter ships table-layout:fixed + width:100%, which ignores
     min-width and divides the window proportionally -> unreadably narrow). */
  width: auto !important;
  table-layout: auto !important;
}}
.vob-table thead th {{
  position: sticky; top: 0; z-index: 2;
  background: {t['head-bg']} !important; color: {t['head-fg']} !important;
  font-weight: 700; padding: 8px 14px; text-align: center;
  border-bottom: 2px solid {t['head-accent']}; white-space: nowrap;
  max-width: var(--vt-maxw); overflow: hidden; text-overflow: ellipsis;
}}
.vob-table tbody td {{
  padding: 7px 14px; color: {t['fg']} !important; text-align: center;
  border-bottom: 1px solid {t['row-line']}; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; max-width: var(--vt-maxw);
}}
.vob-table tbody tr:last-child td {{ border-bottom: 0; }}
.vob-table tbody tr:nth-child(even) td {{ background: {t['row-alt']} !important; }}
.vob-table tbody tr:nth-child(odd) td {{ background: {t['row']} !important; }}
.vob-table tbody tr:hover td {{ background: {t['row-hover']} !important; }}
.vob-table td.vob-idx, .vob-table th.vob-idx {{
  color: {t['index-fg']} !important; font-weight: 600; min-width: 42px;
  position: sticky; left: 0; z-index: 2;
}}
.vob-table thead th.vob-idx {{ background: {t['head-bg']} !important; z-index: 4; }}  /* corner matches the header */
.vob-table tbody td.vob-idx {{ background: {t['index-bg']} !important; }}  /* index column; opaque so it stays solid on scroll, borders follow the data cells */
.vob-table td.vob-null {{ color: {t['null-fg']}; background: {t['null-bg']} !important;
  font-style: italic; }}
.vob-table .vob-glyph {{ font-size: 11px; font-weight: 700; letter-spacing: .04em;
  margin-bottom: 3px; }}
.vob-table .vob-glyph.type-num {{ color: {t['type-num']}; }}
.vob-table .vob-glyph.type-txt {{ color: {t['type-txt']}; }}
.vob-table .vob-dtype {{ font-size: 11px; font-weight: 400; color: {t['fg-muted']};
  margin-top: 3px; }}
.vob-table .vob-bar {{ display: flex; align-items: center; gap: 6px; margin-top: 5px; }}
.vob-table .vob-bar-track {{ flex: 1; height: 5px; border-radius: 3px;
  background: {t['bar-track']}; overflow: hidden; }}
.vob-table .vob-bar-fill {{ height: 100%; border-radius: 3px; background: {t['bar-fill']}; }}
.vob-table .vob-bar-pct {{ font-size: 10px; font-weight: 600; color: {t['fg-muted']}; }}
.vob-table .vob-bool-t {{ color: #5BE49B; font-weight: 700; }}
.vob-table .vob-bool-f {{ color: {t['null-fg']}; font-weight: 700; }}
.vob-table .vob-scroll::-webkit-scrollbar {{ width: 8px; height: 8px; }}
.vob-table .vob-scroll::-webkit-scrollbar-thumb {{ background: {t['line']};
  border-radius: 4px; }}
.vob-table .vob-scroll::-webkit-scrollbar-thumb:hover {{ background: {t['head-accent']}; }}
</style>"""


def _format_value(val, j, col_formats, m):
    """Comma / user format handling (same semantics as the legacy renderer)."""
    is_f = (
        isinstance(col_formats, list)
        and len(col_formats) == m - 1
        and j > 0
        and isinstance(col_formats[j - 1], str)
        and len(col_formats[j - 1]) == 1
    )
    if conf.get_option("insert_comma_numbers") and not is_f:
        try:
            float(val)
            val = "{:,}".format(val)
        except (TypeError, ValueError):
            pass
    if is_f and col_formats[j - 1] != "-":
        try:
            val = ("{:" + col_formats[j - 1] + "}").format(val)
        except (TypeError, ValueError):
            pass
    return val


def _header_cell(name, dtype, percent, full_mode):
    """Column header: type glyph + name + dtype caption + completeness bar."""
    glyph_html, dtype_html, bar_html = "", "", ""
    if name in dtype and full_mode and dtype[name] != "undefined":
        type_val = dtype[name].capitalize()
        category = to_category(type_val)
        lowered = name.lower().split(" ")
        if category == "spatial" or (
            category == "float"
            and any(k in lowered for k in ("lat", "latitude", "lon", "longitude"))
        ):
            key = "spatial"
        elif type_val.lower() == "boolean":
            key = "bool"
        elif category in ("int", "float", "binary", "uuid"):
            key = "num"
        elif category == "text":
            key = "text"
        elif category == "date":
            key = "date"
        elif category == "complex":
            key = "complex"
        else:
            key = None
        if key:
            glyph, cls = _TYPE_GLYPHS[key]
            glyph_html = f'<div class="vob-glyph {cls}">{glyph}</div>'
        dtype_html = f'<div class="vob-dtype">{type_val}</div>'
    if name in percent:
        per = int(float(percent[name]))
        bar_html = (
            '<div class="vob-bar"><div class="vob-bar-track">'
            f'<div class="vob-bar-fill" style="width:{per}%"></div></div>'
            f'<span class="vob-bar-pct">{per}%</span></div>'
        )
    return f"<th>{glyph_html}<b>{name}</b>{dtype_html}{bar_html}</th>"


def _render_html_table(
    data_columns,
    theme,
    offset,
    repeat_first_column,
    maxheight,
    maxwidth,
    dtype,
    percent,
    col_formats,
):
    t = _THEME_TOKENS[theme]
    full_mode = conf.get_option("mode") in ("full", None)

    if not repeat_first_column:
        data_columns = [
            [""] + list(range(1 + offset, len(data_columns[0]) + offset))
        ] + data_columns
    m, n = len(data_columns), len(data_columns[0])

    # Column sizing: content-driven. With width:auto + table-layout:auto +
    # nowrap, the browser sizes every column exactly to its widest content
    # (cells, name, and dtype caption are all real content). max_cellwidth
    # caps runaway columns via max-width + ellipsis. No manual minimums.

    parts = [
        _table_css(t, theme_name=theme),
        f'<div class="vastorbit_table vob-table" '
        f'style="--vt-maxh:{maxheight}px; --vt-maxw:{maxwidth}px;">',
        '<div class="vob-scroll"><table>',
    ]

    # ── header row ──
    parts.append("<thead><tr>")
    logo = vastorbit_logo_html(size="38px") if (dtype and full_mode) else ""
    parts.append(f'<th class="vob-idx">{logo}</th>')
    for j in range(1, m):
        name = data_columns[j][0]
        name = html.escape(name) if isinstance(name, str) else name
        if full_mode:
            parts.append(_header_cell(name, dtype, percent, full_mode))
        else:
            parts.append(f"<th><b>{name}</b></th>")
    parts.append("</tr></thead><tbody>")

    # ── body rows ──
    for i in range(1, n):
        parts.append("<tr>")
        for j in range(m):
            val = data_columns[j][i]
            if isinstance(val, str):
                val = html.escape(val)
            cls, title = "", ""
            if j == 0:
                cls = ' class="vob-idx"'
            elif isinstance(val, NoneType):
                val, cls = "[null]", ' class="vob-null"'
            elif isinstance(val, bool) and full_mode:
                val = (
                    '<span class="vob-bool-t">&#10003;</span>'
                    if val
                    else '<span class="vob-bool-f">&#10007;</span>'
                )
            else:
                val = _format_value(val, j, col_formats, m)
                sval = str(val)
                if len(sval) > 40:
                    title = f' title="{sval}"'
            parts.append(f"<td{cls}{title}>{val}</td>")
        parts.append("</tr>")

    parts.append("</tbody></table></div></div>")
    return "".join(parts)