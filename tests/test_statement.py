from acsylla import (
    Consistency,
    create_statement,
    errors,
    types,
)

import pytest

pytestmark = pytest.mark.asyncio


class TestStatement:

    OUT_OF_BAND_PARAMETER = 10

    @pytest.fixture(params=["none_prepared", "prepared"])
    async def statement(self, request, session):
        statement_str = (
            "INSERT INTO test (id, value, value_int, value_float, value_bool, value_text, value_blob, value_uuid) values "  # noqa
            + "(?, ?, ?, ?, ?, ?, ?, ?)"
        )
        if request.param == "none_prepared":
            statement_ = create_statement(statement_str, parameters=8)
        elif request.param == "prepared":
            prepared = await session.create_prepared(statement_str)
            statement_ = prepared.bind()
        else:
            raise ValueError()

        return statement_

    def test_create_with_timeout(self):
        statement = create_statement("INSERT INTO test (id) values (1)", timeout=1.0)
        assert statement is not None

    @pytest.mark.parametrize(
        "consistency",
        [
            Consistency.ANY,
            Consistency.ONE,
            Consistency.TWO,
            Consistency.THREE,
            Consistency.QUORUM,
            Consistency.ALL,
            Consistency.LOCAL_QUORUM,
            Consistency.EACH_QUORUM,
            Consistency.SERIAL,
            Consistency.LOCAL_SERIAL,
            Consistency.LOCAL_ONE,
        ],
    )
    async def test_create_with_consistency(self, consistency):
        statement = create_statement("INSERT INTO test (id) values (1)", consistency=consistency)
        assert statement is not None

    def test_bind_list(self, statement):
        statement.bind_list(
            [1, None, 2, 10.0, True, "acsylla", b"acsylla", types.uuid("550e8400-e29b-41d4-a716-446655440000")]
        )

    def test_bind_null(self, statement):
        statement.bind(1, None)

    def test_bind_null_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, None)

    def test_bind_int(self, statement):
        statement.bind(2, 10)

    def test_bind_int_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, 10)

    def test_bind_float(self, statement):
        statement.bind(3, 10.0)

    def test_bind_float_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, 10.0)

    def test_bind_bool(self, statement):
        statement.bind(4, True)

    def test_bind_bool_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, True)

    def test_bind_string(self, statement):
        statement.bind(5, "acsylla")

    def test_bind_string_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, "acsylla")

    def test_test_bind_uuidbind_bytes(self, statement):
        statement.bind(6, b"acsylla")

    def test_bind_bytes_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, b"acsylla")

    def test_bind_uuid(self, statement):
        statement.bind(7, types.uuid("550e8400-e29b-41d4-a716-446655440000"))

    def test_bind_uuid_invalid_index(self, statement):
        with pytest.raises(errors.CassErrorLibIndexOutOfBounds):
            statement.bind(TestStatement.OUT_OF_BAND_PARAMETER, types.uuid("550e8400-e29b-41d4-a716-446655440000"))


class TestStatementOnlyPrepared:
    """Special tests for testing some methods that are only allowed for statements
    that were created by using prepared statements."""

    @pytest.fixture
    async def statement(self, session):
        statement_str = (
            "INSERT INTO test (id, value, value_int, value_float, value_bool, value_text, value_blob, value_uuid) values "  # noqa
            + "(?, ?, ?, ?, ?, ?, ?, ?)"
        )
        prepared = await session.create_prepared(statement_str)
        statement_ = prepared.bind()
        return statement_

    def test_bind_dict(self, statement):
        statement.bind_dict(
            {
                "id": 1,
                "value": None,
                "value_int": 2,
                "value_float": 10.0,
                "value_bool": True,
                "value_text": "acsylla",
                "value_blob": b"acsylla",
                "value_uuid": types.uuid("550e8400-e29b-41d4-a716-446655440000"),
            }
        )

    def test_bind_null_by_name(self, statement):
        statement.bind_by_name("value", None)

    def test_bind_null_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", None)

    def test_bind_int_by_name(self, statement):
        statement.bind_by_name("value_int", 10)

    def test_bind_int_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", 10)

    def test_bind_uuid_by_name(self, statement):
        statement.bind_by_name("value_uuid", types.uuid("550e8400-e29b-41d4-a716-446655440000"))

    def test_bind_uuid_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", types.uuid("550e8400-e29b-41d4-a716-446655440000"))

    def test_bind_float_by_name(self, statement):
        statement.bind_by_name("value_float", 10.0)

    def test_bind_float_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", 10.0)

    def test_bind_bool_by_name(self, statement):
        statement.bind_by_name("value_bool", True)

    def test_bind_bool_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", True)

    def test_bind_string_by_name(self, statement):
        statement.bind_by_name("value_text", "acsylla")

    def test_bind_string_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", "acsylla")

    def test_bind_bytes_by_name(self, statement):
        statement.bind_by_name("value_blob", b"acsylla")

    def test_bind_bytes_by_name_invalid_name(self, statement):
        with pytest.raises(errors.CassErrorLibNameDoesNotExist):
            statement.bind_by_name("invalid_field", b"acsylla")
