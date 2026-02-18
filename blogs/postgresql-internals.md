---
title: PostgreSQL's Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-02-18 00:15:13
updated_at: 2026-02-18 00:15:13
---

## Foreword

Backend engineering is my specialty, and database is the specialty of my specialty.
The more types of databases I learn about and use in my projects,
the more I appreciate the timeless design and powerfulness of plain old PostgreSQL
compared to the so-called NoSQL contestants.

PostgreSQL is here to stay, understanding its architecture has helped me a lot with using it more effectively,
and by understanding PostgreSQL's architecture, many of the ideas carried over to other types of databases too,
so it laid a foundational for my understanding of other databases too.

I've read PostgreSQL's documentations a number of times
(and, given the richness of the information, I frankly still can't name every detail),
I've taken the "Implementation of Database" class at UCSB under database expert Professor Divy Agrawal,
and I've read a few books and a number of blogs on it too.

The following blog condenses my understanding of PostgreSQL from what I've read and learned.
Hopefully this can be a fun, informative read for you, so that you can take away the most important information without
having to read the full books.
It's not exhaustive, just the big ideas, and sometimes simplified.
And this blog assumes you as the reader is already familiar with SQL and the usage of PostgreSQL.

## The Purpose of PostgreSQL

In jargon, PostgreSQL is an ACID compliant relational database. If we break it down in plain english, it means
PostgreSQL's purpose is to:

1. Store data in the "relational" paradigm, aka. as tables and columns analogous to Excel
2. Support efficient querying and updating of data
3. Support different users querying and updating data concurrently while ensuring everyone still sees the right data (
   the "I" in ACID, which is "Isolation")
4. Meanwhile, also ensure the updates are durable and are all or nothing (the "A" "C" "D" in ACID, which are atomic,
   consistent, and durable)

Thus, to understand the internal architecture and implementation of Postgres,
we can dissect it in the order for each of the above 4 points.

## Store the data

When we insert rows to a table, PostgreSQL would store your rows in its "heap",
which is just a file on disk that has your rows and some metadata.

The rows are usually not ordered here or anything. They are simply thrown there.

Logically this is the same as appending a new JSON to a big blob of JSONS in a .json file you created.

The difference is that, since a PostgreSQL table has a defined schema of what columns it contains,
it doesn't need to store the field names again like JSON. And, since each column's type is also defined,
PostgreSQL would store an integer not as a readable string like JSON but as a byte if you know what I mean.

When you delete or modify some rows, things get interesting. Hold on to that for now.

## Efficient querying and updating of data

Okay, you have all of your rows stored in heap. Great. Now let's run some example SQL queries:

```sql
SELECT * FROM my_table LIMIT 10
```

```sql
SELECT * FROM my_table WHERE user_id = 123
```

```sql
DELETE * FROM my_table WHERE user_id = 123
```

Look at the first query. You just want 10 rows, so just grab them from heap.
Now look at the second and third query. You need just that 1 row with `user_id = 123`.
If we purely rely on the heap, we would have to check every row in the heap until we find something.
If there X rows, on average we have to check X/2 of them and that's very slow.

So how to support efficiently querying relevant data given filter conditions?

Think about this analogy. If we are writing an in-memory program,
the raw heap is like an unsorted list.
And if we want to find things more efficiently,
we would then have to put our data as a dictionary/hashmap or a binary search tree.
Then, looking up the relevant data just means dict.find(key) or searching over that binary search tree,
which is super efficient comparing to having check everything one by one.

Now back to PostgreSQL.
To support efficient querying, PostgreSQL uses the same ideas as if we need to write an in-memory program.
It gives us as user the options to create auxiliary indexes to order our data in some particular way.
If you create a HASH index, it means the data is stored as a hashmap on disk and lookup is logically dict.find(key).
If you create a BTree index, it means the data is stored as a B+Tree on disk and lookup is logically same as binary
searching over an in memory binary search tree. B+Tree is just the on disk variant of binary search tree
to be more efficient in the disk environment.

Note that, the original "heap" storage is here to stay.
The HASH and BTree index are just auxiliary indexes whose "keys" are the columns you order them by and the "values"
are pointers to the actual data in the heap location.

You might ask, "why not just make the original heap a HASH or BTree"?
This is because a PostgreSQL table frequently has more than 1 indexes,
so it's the design decision of PostgreSQL to just store the original data in heap and impose ordered indexes separately.
For PostgreSQL's competitor MySQL though, the original data is stored in B+Tree though. It really is just a design
choice.

B+Tree is more commonly used, because with caching, its querying is empirically as fast as HASH.
AND, HASH only lets you support point querying. What if you want to find `SELECT * FROM user WHERE age BETWEEN 10 AND 20`?
BTree can be used here, but HASH would be useless.

As said earlier, we as users can and should explicitly create indexes on relevant columns to speedup querying.
But note that, by default, PostgreSQL already automatically creates BTree indexes for:

1. Primary key
2. UNIQUE constraint

So this means, for an SQL query, PostgreSQL would consider and use the best indexes to speed up the query execution.
For an update query, it means PostgreSQL would not only update the original heap data, but also the relevant indexes.

But there's a catch, and we are about to explain that in the immediate section below.


## Concurrent querying and updates

If PostgreSQL only supports 1 person querying and updating the data, then none of the following architecture components
needs to be there. However, for any backend / app that have a lot of users, every instant,
there would be multiple users querying and updating the data in PostgreSQL.

Why is this a problem? In 2 regards:

1. Visibility
2. Locking

### Visibility

Well, consider Alice writing this query:

```sql
BEGIN;
INSERT INTO products(id, name, price) VALUES (1, 'Nike Air', 46.99);
INSERT INTO products(id, name, price) VALUES (2, 'Jordan', 123.99);
INSERT INTO products(id, name, price) VALUES (3, 'Adidas', 38.99);
UPDATE products SET price = price + 10 WHERE id = 2;
// hundreds more data
COMMIT;
```

Meanwhile Bob writes this query:

```sql
SELECT * FROM products WHERE name LIKE 'Jordan%'
```

By requirements of SQL transactions and concurrency protocols,
if Bob `SELECT` after Alice `COMMIT`, then Bob should see the new Jordan there.
But if Bob `SELECT` any time before the Alice `COMMIT`, even as new rows are being inserted,
Bob should NOT see the new Jordan there.
To make it even more complicated, Alice actually should see her own rows while Bob shouldn't.

To summarize, it means, for rows created, updated, or deleted for a transaction issued by user A,
user A should see all of their own changes even before `COMMIT`,
but user B should NOT see user A's changes until user A `COMMIT`.

This visibility rule doesn't matter as much for product listings, but for banks, ecommerce inventory control, it matters.

So, how does PostgreSQL's architecture support this concurrent visibility requirement?
Aka. how does it let different users see different data?

The idea is simple: for every insert, update, or delete, instead of modifying the actual row,
we simply create a new version of the row and put a transaction ID on it.

Then, for every user, when a `SELECT` or `UPDATE` or `DELETE` is issued,
PostgreSQL would compare the current user's transaction ID with the transaction ID on the versioned row,
and check, "okay, is this versioned row a row I created? If it's my row, then I should always see it. If it's others', then I should only see it if that transaction had been marked as COMMITed."

This way, PostgreSQL allows different users to see different data based on the SQL's concurrent visibility control requirements.
In jargon, this is called "Multiversion Concurrency Control" (MVCC).

Going back to how updates affect heap and secondary indexes.
This means, Heap data is never updated in place, only new versions are appended.
For indexes, multiple versions can exist there too.
Of course, PostgreSQL would periodically delete old row versions that are no longer used by any transactions
to release space.
The takeaway is, with the row version mechanism,
PostgreSQL only have to insert and delete row versions, but doesn't have to directly update things in-place.


### Locking

Now consider another scenario, equally if not more important than the previous example. We have Alice do this:

```sql
BEGIN;
UPDATE product_inventory SET count = count - 1 WHERE product_id = 12345 AND count > 0;
// Some other stuff is done in between
INSERT INTO user_orders(user_id, product_id) VALUES (123, 12345);
COMMIT;
```

This is means for an ecommerce website, Alice is trying to place a order,
and PostgreSQL must update the inventory and create the order record in 1 transaction.

We also Bob trying to order the same product:
```sql
BEGIN;
UPDATE product_inventory SET count = count - 1 WHERE product_id = 12345 AND count > 0;
// Some other stuff is done in between
INSERT INTO user_orders(user_id, product_id) VALUES (123, 12345);
COMMIT;
```

And guess what, it's a popular product item, so Bob and Alice actually try to order the item at the same instant.

Why is this a problem?

While Alice is deducting product 12345's inventory count and trying to create a order, in that split millisecond,
any other user, including Bob, is allowed to still read product 12345's inventory count but NOT update it.
This is another requirement of SQL's concurrency protocol.

Multiversion concurrency control enable concurrent reads, but we still need to ensure non-current, exclusive update,
one at a time.

So how does PostgreSQL's architecture ensure exclusive update?
