---
title: Clickhouse Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-02-20 2:26:13
updated_at: 2026-02-20 2:26:13
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
2. Long, analytical queries instead of point querying or updates. Example:

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

Let's dive in.

## Data storage

## Query execution

## Conclusion
