---
title: Clickhouse Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-02-20 2:26:13
updated_at: 2026-02-20 2:26:13
excludes_from_index: True
---

## Foreword

What if we need to build a relational database like PostgreSQL,
where you store and query data with SQL,
but the use case is for analytical queries instead of transactional updates and point queries?

This means, usage wise, we do NOT need to be concerned with:

1. ACID transactions. Aka not too worried about atomic updates, consistency, durability, or concurrency isolation
2. Point querying. Aka not too worried about `SELECT * FROM users where id = 123`
3. Updates. Aka not too worried about `UPDATE users SET username = 'joe' WHERE id = 123`

Instead, our usage will mostly be for analytical queries, such as analyzing click logs, user events, etc.

So the SQLs we need to worry about are mostly:

1. Batch insert. Example: `INSERT INTO click_events VALUES (10000 rows here)`
2. Big analytical queries instead of point querying or updates. Example:

```sql
SELECT user_id, MONTH(timestamp), AVG(HOUR(timestamp)) FROM click_events
JOIN users ON users.id = click_events.user_id
GROUP BY user_id, MONTH(timestamp)
ORDER BY COUNT(*)
```

And that's what ClickHouse is built for.
As a over simplification, ClickHouse is engineered for fast analytical querying,
and its architecture achieves this performance by:

1. Not needing MVCC, Write Ahead Log, etc.
2. Organizing the underlying data in columnar fashion, with compression, skip indexes, etc.

Clickhouse's architecture is a lot cleaner to understand than [PostgreSQL](/blogs/postgresql-internals.md).
I have a lot less experience with Clickhouse than PostgreSQL,
but the big ideas in the following blog should be accurate.

This reading assumes the reader is familiar with SQL and PostsgreSQL,
which is used as occasional comparison for illustrative purpose. Let's dive in.

## Data storage

### Columnar storage layout

When a batch of rows is inserted, ClickHouse builds them into a "part".
1000 new rows become a part. Another 5000 rows become another part.
The rows within a part are ordered by whatever primary key the users specifies.
And over time, ClickHouse merges parts together.

Within a part, ClickHouse would store the column values together as a file.
For example, "user id" would be stored in a file together, and "purchased product id" would be in another file.

This is different from transactional databases like PostgreSQL.
PostgreSQL ensures a row stays together,
but ClickHouse would break up a row into its columns and store all the values for a column together instead.

As a Python psuedo code, Clickhouse would:

```python
user_ids = [1, 2, 34, 451]  # This gets stored in a file, ordered by primary key
purchased_product_ids = [2342, 923234, 34, 13423]  # This gets stored in another file, ordered by primary key
```

While PostgreSQL would:

```python
rows = [
    {'user_id': 1, 'purchased_product_id': 2342},
    {'user_id': 2, 'purchased_product_id': 923234}
    # etc.
]
```

Why does ClickHouse store data in columnar fashion?

This is because for analytical databases, a table would frequently have, say, dozens to a hundred fields.
And when we write analytical SQL queries, usually we would be querying through a lot of rows, but only, say, 10 columns.

With ClickHouse's columnar storage layout,
if our SQL query aggregates 10 out of 100 columns of 10 million rows in a table, we touch 1 / 10th of total data.

Had we stored rows together instead of columns, we would have touched ALL the data,
because in that case we have to scan all the rows and not use the 90 / 100 columns in each row,
which is very inefficient.

However, columnar storage layout suffers from point query.
Suppose we run `SELECT * FROM users WHERE id = 100`,
then ClickHouse would need to touch 100 files to assemble all the column values for that row together.

But that's totally fine,
because ClickHouse's use case is for analytical queries that touches a lot of rows but a few columns.
Columnar storage layout wins here.

For transactional databases that emphasize on point query and updates, storing rows together is a must,
which is what PostgreSQL do.

### Compression

When we store columns together instead of rows together, compression becomes super easy and effective.
This is because the same column would have the same data type,
and due to data semantics, the same column's data usually gives huge room for compression.

Why does compression matter? 2 reasons:

1. Less disk usage, so that saves cost
2. Less IO needed. Compression trades data size against CPU. If you can compress 10 MB to 5 MB, that means you are doing half of disk IOs at the cost of CPU overhead with compression. But that's win, because CPU is super fast compared to disk IO. So the overall performance increases

### Primary key and granule

TODO

### Partitions

For transactional databases like PostgreSQL,
BTree or HASH indexes allow us to find rows efficiently and avoid scanning unnecesary data given some filter condition.

When we write a large analytical SQL with a lot of filter conditions,
ClickHouse is able to use the mechanisms of partitions to avoid scanning unnecessary data.
These mechanisms differ from BTree or HASH indexes, but the purpose is the same: avoid scanning unnecessary data.

When a table is defined in ClickHouse, we have the option to instruct it to "partition" the data by time range.
For example, all the July 2025 data goes in 1 partition, August 2025 in another, February 2026 in another, and so on.
Each partition is manifested on disk as a folder.

Then, when a "part" is created, it would be split up by the partition rule into the correct partition folders.
For example, all the newly inserted rows with timestamp July 2025 goes under 1 partition, February 2026 in another, and so on.

So roughly, the underlying data storage would look like this folder structure:

```
July 2025
   Part 1
        user id column.file
        purchased product id column.file
   Part 2
        user id column.file
        purchased product id column.file
Janurary 2026
   Part 1
        user id column.file
        purchased product id column.file
   Part 2
        user id column.file
        purchased product id column.file
   Part 3
        user id column.file
        purchased product id column.file
```

For analytical databases like ClickHouse, timestamp is a first class concept,
because analytical databases usually ingest rows that are semantically "events" of some sorts,
and time is what defines an event.

Thus, when we write analytical queries, we frequently filter by timestamp.
With the partition mechanism, as the data is already partitioned by timestamps,
we are able to identify what partitions are relevant and avoid scanning partitions that don't match the timestamp filter.

We also commonly have the use case of removing data that is too old.
With the partition mechanism, this becomes easy,
because ClickHouse just needs to periodically delete the entire partition folder once they become too old.

### Skip Indexes

Skip index is another mechanism for ClickHouse to avoid scanning data that do not match the filter condition for an analytical SQL query,
at a finer granularity than partitions.

Partition lets us avoid scanning parts that are out of the time range (or other partition ranges) in their entirely.
But can we go a step further to avoid scanning data within a part too?

As an example:

```sql
SELECT
    country,
    SUM(money)
FROM purchase_events
GROUP BY country
WHERE
    timestamp BETWEEN '2025-12-01' AND '2026-2-05'
    AND money > 100
```

Partitioning by timestamp lets us skip all the data that are not in December 2025 or February 2026.
But we still have to scan all the parts' country and money column files within December 2025 and February 2026 partitions
despite we only care about a purchase event if money > 10.

Can we make it even more efficient by skipping irrelevant data at an even finer granularity? Enters skip index.

## Query execution

## Conclusion
