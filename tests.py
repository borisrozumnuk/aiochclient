import datetime as dt
from uuid import uuid4

import aiohttp
import pytest

from aiochclient import ChClient, ChClientError

pytestmark = pytest.mark.asyncio


@pytest.fixture
def uuid():
    return uuid4()


@pytest.fixture
def rows(uuid):
    return [
        (
            1,
            1000,
            10000,
            12_345_678_910,
            -4,
            -453,
            21322,
            -32123,
            23.432,
            -56754.564_542,
            "hello man",
            "hello fixed man".ljust(32, " "),
            dt.date(2018, 9, 21),
            dt.datetime(2018, 9, 21, 10, 32, 23),
            "hello",
            "world",
            [1, 2, 3, 4],
            (4, "hello"),
            0,
            ["hello", "world"],
            "'\b\f\r\n\t\\",
            uuid,
            [uuid, uuid, uuid],
            ["hello", "world", "hello"],
            [dt.date(2018, 9, 21), dt.date(2018, 9, 22)],
            [
                dt.datetime(2018, 9, 21, 10, 32, 23),
                dt.datetime(2018, 9, 21, 10, 32, 24),
            ],
            "hello man",
            "hello man",
            777,
            dt.date(1994, 9, 7),
            dt.datetime(2018, 9, 21, 10, 32, 23),
        ),
        (
            2,
            1000,
            10000,
            12_345_678_910,
            -4,
            -453,
            21322,
            -32123,
            23.432,
            -56754.564_542,
            "hello man",
            "hello fixed man".ljust(32, " "),
            None,
            None,
            "hello",
            "world",
            [1, 2, 3, 4],
            (4, "hello"),
            None,
            [],
            "'\b\f\r\n\t\\",
            None,
            [],
            [],
            [],
            [],
            "hello man",
            None,
            777,
            dt.date(1994, 9, 7),
            dt.datetime(2018, 9, 21, 10, 32, 23),
        ),
    ]


@pytest.fixture(
    params=[
        {
            "compress_response": True,
            "user": "default",
            "password": "",
            "database": "default",
        },
        {},
    ]
)
async def chclient(request):
    async with aiohttp.ClientSession() as s:
        yield ChClient(s, **request.param)


@pytest.fixture
async def all_types_db(chclient, rows):
    await chclient.execute("DROP TABLE IF EXISTS all_types")
    await chclient.execute(
        """
    CREATE TABLE all_types (uint8 UInt8, 
                            uint16 UInt16,
                            uint32 UInt32,
                            uint64 UInt64,
                            int8 Int8,
                            int16 Int16,
                            int32 Int32,
                            int64 Int64,
                            float32 Float32,
                            float64 Float64,
                            string String,
                            fixed_string FixedString(32),
                            date Nullable(Date),
                            datetime Nullable(DateTime),
                            enum8 Enum8('hello' = 1, 'world' = 2),
                            enum16 Enum16('hello' = 1000, 'world' = 2000),
                            array_uint8 Array(UInt8),
                            tuple Tuple(UInt8, String),
                            nullable Nullable(Int8),
                            array_string Array(String),
                            escape_string String,
                            uuid Nullable(UUID),
                            array_uuid Array(UUID),
                            array_enum Array(Enum8('hello' = 1, 'world' = 2)),
                            array_date Array(Date),
                            array_datetime Array(DateTime),
                            low_cardinality_str LowCardinality(String),
                            low_cardinality_nullable_str LowCardinality(Nullable(String)),
                            low_cardinality_int LowCardinality(Int32),
                            low_cardinality_date LowCardinality(Date),
                            low_cardinality_datetime LowCardinality(DateTime)
                            
                            ) ENGINE = Memory
    """
    )
    await chclient.execute("INSERT INTO all_types VALUES", *rows)


@pytest.fixture
def class_chclient(chclient, all_types_db, rows, request):
    request.cls.ch = chclient
    request.cls.rows = rows


@pytest.mark.client
@pytest.mark.usefixtures("class_chclient")
class TestClient:
    async def test_is_alive(self):
        assert await self.ch.is_alive() is True

    async def test_bad_query(self):
        with pytest.raises(ChClientError):
            await self.ch.execute("SELE")

    async def test_bad_select(self):
        with pytest.raises(ChClientError):
            await self.ch.execute("SELECT * FROM all_types WHERE", 1, 2, 3, 4)


@pytest.mark.types
@pytest.mark.usefixtures("class_chclient")
class TestTypes:
    async def select_field(self, field):
        return await self.ch.fetchval(f"SELECT {field} FROM all_types WHERE uint8=1")

    async def select_record(self, field):
        return await self.ch.fetchrow(f"SELECT {field} FROM all_types WHERE uint8=1")

    async def test_uint8(self):
        assert await self.select_field("uint8") == 1
        record = await self.select_record("uint8")
        assert record[0] == 1
        assert record["uint8"] == 1

    async def test_uint16(self):
        result = 1000
        assert await self.select_field("uint16") == result
        record = await self.select_record("uint16")
        assert record[0] == result
        assert record["uint16"] == result

    async def test_uint32(self):
        result = 10000
        assert await self.select_field("uint32") == result
        record = await self.select_record("uint32")
        assert record[0] == result
        assert record["uint32"] == result

    async def test_uint64(self):
        result = 12_345_678_910
        assert await self.select_field("uint64") == result
        record = await self.select_record("uint64")
        assert record[0] == result
        assert record["uint64"] == result

    async def test_int8(self):
        result = -4
        assert await self.select_field("int8") == result
        record = await self.select_record("int8")
        assert record[0] == result
        assert record["int8"] == result

    async def test_int16(self):
        result = -453
        assert await self.select_field("int16") == result
        record = await self.select_record("int16")
        assert record[0] == result
        assert record["int16"] == result

    async def test_int32(self):
        result = 21322
        assert await self.select_field("int32") == result
        record = await self.select_record("int32")
        assert record[0] == result
        assert record["int32"] == result

    async def test_int64(self):
        result = -32123
        assert await self.select_field("int64") == result
        record = await self.select_record("int64")
        assert record[0] == result
        assert record["int64"] == result

    async def test_float32(self):
        result = 23.432
        assert await self.select_field("float32") == result
        record = await self.select_record("float32")
        assert record[0] == result
        assert record["float32"] == result

    async def test_float64(self):
        result = -56754.564_542
        assert await self.select_field("float64") == result
        record = await self.select_record("float64")
        assert record[0] == result
        assert record["float64"] == result

    async def test_string(self):
        result = "hello man"
        assert await self.select_field("string") == result
        record = await self.select_record("string")
        assert record[0] == result
        assert record["string"] == result

    async def test_fixed_string(self):
        result = "hello fixed man".ljust(32, " ")
        assert await self.select_field("fixed_string") == result
        record = await self.select_record("fixed_string")
        assert record[0] == result
        assert record["fixed_string"] == result

    async def test_date(self):
        result = dt.date(2018, 9, 21)
        assert await self.select_field("date") == result
        record = await self.select_record("date")
        assert record[0] == result
        assert record["date"] == result

    async def test_datetime(self):
        result = dt.datetime(2018, 9, 21, 10, 32, 23)
        assert await self.select_field("datetime") == result
        record = await self.select_record("datetime")
        assert record[0] == result
        assert record["datetime"] == result

    async def test_enum8(self):
        result = "hello"
        assert await self.select_field("enum8") == result
        record = await self.select_record("enum8")
        assert record[0] == result
        assert record["enum8"] == result

    async def test_enum16(self):
        result = "world"
        assert await self.select_field("enum16") == result
        record = await self.select_record("enum16")
        assert record[0] == result
        assert record["enum16"] == result

    async def test_array_uint8(self):
        result = [1, 2, 3, 4]
        assert await self.select_field("array_uint8") == result
        record = await self.select_record("array_uint8")
        assert record[0] == result
        assert record["array_uint8"] == result

    async def test_tuple(self):
        result = (4, "hello")
        assert await self.select_field("tuple") == result
        record = await self.select_record("tuple")
        assert record[0] == result
        assert record["tuple"] == result

    async def test_nullable(self):
        result = 0
        assert await self.select_field("nullable") == result
        record = await self.select_record("nullable")
        assert record[0] == result
        assert record["nullable"] == result

    async def test_array_string(self):
        result = ["hello", "world"]
        assert await self.select_field("array_string") == result
        record = await self.select_record("array_string")
        assert record[0] == result
        assert record["array_string"] == result

    async def test_escape_string(self):
        result = "'\b\f\r\n\t\\"
        assert await self.select_field("escape_string") == result
        record = await self.select_record("escape_string")
        assert record[0] == result
        assert record["escape_string"] == result

    async def test_uuid(self, uuid):
        result = uuid
        assert await self.select_field("uuid") == result
        record = await self.select_record("uuid")
        assert record[0] == result
        assert record["uuid"] == result

    async def test_array_uuid(self, uuid):
        result = [uuid, uuid, uuid]
        assert await self.select_field("array_uuid") == result
        record = await self.select_record("array_uuid")
        assert record[0] == result
        assert record["array_uuid"] == result

    async def test_array_enum(self):
        result = ["hello", "world", "hello"]
        assert await self.select_field("array_enum ") == result
        record = await self.select_record("array_enum ")
        assert record[0] == result
        assert record["array_enum"] == result

    async def test_array_date(self):
        assert await self.select_field("array_date ") == [
            dt.date(2018, 9, 21),
            dt.date(2018, 9, 22),
        ]

    async def test_array_datetime(self):
        assert await self.select_field("array_datetime ") == [
            dt.datetime(2018, 9, 21, 10, 32, 23),
            dt.datetime(2018, 9, 21, 10, 32, 24),
        ]

    async def test_low_cardinality_str(self):
        result = "hello man"
        assert await self.select_field("low_cardinality_str") == result
        record = await self.select_record("low_cardinality_str")
        assert record[0] == result
        assert record["low_cardinality_str"] == result

    async def test_low_cardinality_nullable_str(self):
        result = "hello man"
        assert await self.select_field("low_cardinality_nullable_str") == result
        record = await self.select_record("low_cardinality_nullable_str")
        assert record[0] == result
        assert record["low_cardinality_nullable_str"] == result

    async def test_low_cardinality_int(self):
        result = 777
        assert await self.select_field("low_cardinality_int") == result
        record = await self.select_record("low_cardinality_int")
        assert record[0] == result
        assert record["low_cardinality_int"] == result

    async def test_low_cardinality_date(self):
        result = dt.date(1994, 9, 7)
        assert await self.select_field("low_cardinality_date") == result
        record = await self.select_record("low_cardinality_date")
        assert record[0] == result
        assert record["low_cardinality_date"] == result

    async def test_low_cardinality_datetime(self):
        assert await self.select_field("low_cardinality_datetime") == dt.datetime(
            2018, 9, 21, 10, 32, 23
        )


@pytest.mark.fetching
@pytest.mark.usefixtures("class_chclient")
class TestFetching:
    async def test_fetchrow_full(self):
        assert (await self.ch.fetchrow("SELECT * FROM all_types WHERE uint8=1"))[
            :
        ] == self.rows[0]

    async def test_fetchrow_with_empties(self):
        assert (await self.ch.fetchrow("SELECT * FROM all_types WHERE uint8=2"))[
            :
        ] == self.rows[1]

    async def test_fetchone_full(self):
        assert (await self.ch.fetchone("SELECT * FROM all_types WHERE uint8=1"))[
            :
        ] == self.rows[0]

    async def test_fetchone_with_empties(self):
        assert (await self.ch.fetchone("SELECT * FROM all_types WHERE uint8=2"))[
            :
        ] == self.rows[1]

    async def test_fetch(self):
        rows = await self.ch.fetch("SELECT * FROM all_types")
        assert [row[:] for row in rows] == self.rows

    async def test_cursor(self):
        assert [
            row[:] async for row in self.ch.cursor("SELECT * FROM all_types")
        ] == self.rows

    async def test_iterate(self):
        assert [
            row[:] async for row in self.ch.iterate("SELECT * FROM all_types")
        ] == self.rows

    async def test_records_common_objects(self):
        records = await self.ch.fetch("SELECT * FROM all_types")
        assert id(records[0]._converters) == id(records[1]._converters)
        assert id(records[0]._names) == id(records[1]._names)

    async def test_record_lazy_decoding(self):
        record = await self.ch.fetchrow("SELECT * FROM all_types WHERE uint8=2")
        assert type(record._row[0]) == bytes
        record[0]
        assert type(record._row[0]) == int

    async def test_record_mapping(self):
        record = await self.ch.fetchrow("SELECT * FROM all_types WHERE uint8=2")
        assert list(record.values())[0] == 2
        assert list(record.keys())[0] == "uint8"
        assert list(record.items())[0] == ("uint8", 2)
        assert record.get("uint8") == 2
        assert record.get(0) == 2

    async def test_record_bool(self):
        records = await self.ch.fetch("SELECT * FROM all_types WITH TOTALS")
        assert bool(records[-2]) is False

    async def test_record_len(self):
        record = await self.ch.fetchrow("SELECT * FROM all_types WHERE uint8=2")
        assert len(record) == len(self.rows[1])
