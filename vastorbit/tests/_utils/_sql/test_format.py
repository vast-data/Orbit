"""
SPDX-License-Identifier: Apache-2.0
"""

# Pytest
import pytest

# vastorbit
from vastorbit._utils._sql._format import schema_relation
from vastorbit._utils._sql._format import quote_ident
from vastorbit.errors import ParsingError
import vastorbit._config.config as conf


@pytest.fixture(scope="module", autouse=True)
def temp_schema_fixture():
    # Save the current value
    original_temp_schema = conf.get_option("temp_schema")

    # Set the temp schema for tests
    conf.set_option("temp_schema", "temp_schema")

    # Run the tests
    yield

    # Restore the original value after tests in this file
    conf.set_option("temp_schema", original_temp_schema)


@pytest.mark.parametrize(
    "input_relation, expected_schema, expected_table",
    [
        # No schema: should use temp schema
        ("my_table", "temp_schema", "my_table"),
        # Basic schema.table
        ("my_schema.my_table", "my_schema", "my_table"),
        # Namespace.schema.table
        ("namespace.schema.table", "namespace.schema", "table"),
        # Quoted relation
        ('"my_schema"."my_table"', "my_schema", "my_table"),
        # Quoted table only
        # ('"my_table"', "temp_schema", "my_table"), # need to check this
    ],
)
def test_schema_relation_basic(input_relation, expected_schema, expected_table):
    result_schema, result_table = schema_relation(input_relation, do_quote=False)
    assert result_schema == expected_schema
    assert result_table == expected_table


@pytest.mark.parametrize(
    "input_relation, expected_schema, expected_table",
    [
        ("my_schema.my_table", quote_ident("my_schema"), quote_ident("my_table")),
        (
            "namespace.schema.table",
            quote_ident("namespace.schema"),
            quote_ident("table"),
        ),
    ],
)
def test_schema_relation_with_quotes(input_relation, expected_schema, expected_table):
    result_schema, result_table = schema_relation(input_relation, do_quote=True)
    assert result_schema == expected_schema
    assert result_table == expected_table


@pytest.mark.parametrize(
    "invalid_input",
    [
        "too.many.dots.in.this",  # more than 3 parts
        "missing.dot",  # should be fine, temp_schema used
        '"weirdquote.table',  # unbalanced quote
    ],
)
def test_schema_relation_invalid_inputs(invalid_input):
    if (
        invalid_input.count(".") >= 3
        or '"' in invalid_input
        and invalid_input.count('"') % 2 != 0
    ):
        with pytest.raises(ParsingError):
            schema_relation(invalid_input)


def test_schema_relation_non_string_input():
    # Input is not a string, should return temp_schema + empty string
    schema, table = schema_relation(12345, do_quote=False)
    assert schema == "temp_schema"
    assert table == ""
