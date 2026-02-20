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
so it laid the foundation for my understanding of other databases.

I've read PostgreSQL's documentations a number of times
(and, given the richness of the information, I frankly still can't name every detail),
I've taken the "Implementation of Database" class at UCSB under database expert Professor Divy Agrawal,
and I've read a few books and a number of blogs on it too.
The following blog condenses my understanding of PostgreSQL from what I've read and learned.

Hopefully this can be a fun, informative read for you, so that you can take away the most important information without
having to read the full books.
It's not exhaustive, just the big ideas, and sometimes simplified.
But it's still quite long because PostgreSQL has so many interesting aspects to be talked about!

This blog assumes you as the reader is already familiar with SQL, transactions, and the usage of PostgreSQL.

## The Purpose of PostgreSQL

In jargon, PostgreSQL is an ACID compliant relational database. If we break it down in plain english, it means
PostgreSQL's purpose is to:

1. Store data in the "relational" paradigm, aka. as tables and columns analogous to Excel
2. Support efficient querying and updating of data
3. Support different users querying and updating data concurrently while ensuring everyone still sees the right data (
   the "I" in ACID, which is "Isolation")
4. Ensure the updates are durable (the "D" in ACID, which is "Durability")
5. Ensure the updates in a transaction are atomic ("A" in ACID)
6. Ensure the updates don't affect the data consistency ("C" in ACID)


Thus, to understand the internal architecture and implementation of Postgres,
we can dissect it in the order for each of the above points.

## Store the data

When we insert rows to a table, PostgreSQL would store your rows in its "heap",
which is just a file on disk that has your rows and some metadata.

The rows are not ordered here or anything. They are simply thrown there.

Logically this is the same as appending a new JSON to a big blob of JSONS in a .json file you created.

The difference is that, since a PostgreSQL table has a defined schema of what columns it contains,
for each row, it doesn't need to store the field names again like JSON. And, since each column's type is also defined,
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
Now look at the second and third query.
Even if uou need only that 1 row with `user_id = 123`,
we would have to check every row in the heap until we find something.
If there X rows, on average we have to check X/2 of them and that's very slow.

So how to support efficiently querying relevant data given filter conditions?

### Secondary Indexes

Think about this analogy. If we are writing an in-memory program,
the raw heap is like an unsorted list.
And if we want to find things more efficiently,
we would then have to put our data as a dictionary/hashmap or a binary search tree.
Then, looking up the relevant data just means dict.find(key) or searching over that binary search tree,
which is super efficient compared to having check everything one by one.

Now back to PostgreSQL.
To support efficient querying, PostgreSQL uses the same ideas as if we need to write an in-memory program.
It gives us as user the options to create auxiliary indexes to order our data in some particular way.
If you create a HASH index on a column, it means the data is stored as a hashmap on disk and lookup is logically dict.find(key).
If you create a BTree index on some columns,
it means the data is stored as a B+Tree on disk and lookup is logically same as binary searching over an in memory binary search tree.
B+Tree is just the on disk variant of binary search tree to be more efficient in the disk environment.

Note that, the original "heap" storage is here to stay.
The HASH and BTree index are just auxiliary indexes whose "keys" are the columns you explicitly order them by
and the "values" are pointers to the actual data in the heap location called "tuple IDs".

You might ask, "why not just make the original heap a HASH or BTree"?
This is because a PostgreSQL table frequently has more than 1 indexes,
so it's the design decision of PostgreSQL to just store the original data in heap and impose ordered indexes separately.
For PostgreSQL's competitor MySQL though, the original data is stored in B+Tree though. It really is just a design
choice.

B+Tree is more commonly used than HASH, because with caching (discussed next), its querying is empirically as fast as HASH.
AND, HASH only lets you support point querying. What if you want to find
`SELECT * FROM user WHERE age BETWEEN 10 AND 20`?
BTree can be used here, but HASH would be useless.

As said earlier, we as users can and should explicitly create indexes on relevant columns to speedup querying.
But note that, by default, PostgreSQL already automatically creates BTree indexes for:

1. Primary key
2. UNIQUE constraint

When an SQL query is actually executed, PostgreSQL would evaluate and use the best indexes to speed up the query
execution.
For an update query, it means PostgreSQL would not only update the original heap data, but also the relevant indexes.

### Caching
What else can we do to make querying faster? Caching.

For durability and cost-effectiveness, PostgreSQL is meant to store the data on disk instead of in RAM.
So like, if we have a million rows, and it takes 100 GB, we just need 100 GB of disk and little RAM.
However, disk access is 1000x slower than RAM.
Had we had the luxury of storing all the data in RAM instead of on disk,
then our queries can be 1000x faster because RAM is faster than disk.
But once again we must use disk primarily instead of RAM.

Here's where a great idea comes in: caching.
The philosophy of caching exists everywhere in software, from CPU to OS to distributed systems.
The big idea behind caching is, even if all the data is stored on disk,
if we store a fraction of the data also in RAM,
as long as we are wise on choosing what should also be in RAM,
we can still speed up the overall performance by magnitudes while using a fraction of RAM proportional to all the data.

Here's how PostgreSQL does caching.
Naively, all the heap row data and the secondary indexes reads and writes would directly happen to the underlying disk.
But no, PostgreSQL doesn't do that.
Instead, all low level data reads and writes go to a proxy layer called "Buffer Cache".
And, for later convenience, each data read and write must happen 8KB unit at a time,
and that 8KB unit is called a "page".

Buffer Cache essentially proxies all the page reads and writes and caches frequently accessed pages in RAM.
If full, it evicts pages using a "clock-sweep" algorithm
that is conceptually analogous to FIFO eviction, with second chances given for the more frequently accessed pages.

At the high level, this means, if a row is read from heap more frequently,
or if a tree node in the BTree index data structure is traversed more frequently,
or if a hash bucket in the HASH index data structure is checked more frequently,
these data will very likely already to be in the Buffer Cache, which is in RAM,
which means we don't have to read the disk and that's 1000x faster.

Without Buffer Cache, every write might need, say, 7 disk page reads.
With Buffer Cache, it's super likely that the 6 or 7 of the disk pages are already in RAM in the cache,
which means we just need to issue 1 more disk read and that's a lot faster.

To clarify, Caching doesn't speed up writes, but speed up reads by a lot.
Usually there's far more reads than writes, so caching increases the overall PostgreSQL performance by a lot.

By the way, PostgreSQL could not have simply used OS's native page cache or MMAP.
PostgreSQL must manage its own buffer pool as cache because it also needs to
ensure some fine-grained control mechanism called "pinning", which OS's native page cache or MMAP doesn't provide.

## Concurrent querying and updates

If PostgreSQL only supports 1 person querying and updating the data, then none of the following architecture components
needs to be there. However, for any backend / app that have a lot of users, every instant,
there would be multiple users querying and updating the data in PostgreSQL.

Why is this a problem? In 2 regards:

1. Visibility
2. Locking

### Visibility

Consider Alice writing this query:

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

This visibility rule doesn't matter as much for product listings, but for banks, ecommerce inventory control, it
matters.

So, how does PostgreSQL's architecture support this concurrent visibility requirement?
Aka. how does it let different users see different data?

The idea is simple: for every insert, update, or delete, instead of modifying the actual row,
we simply create a new version of the row called "row version" and put a transaction ID on it.

Then, for every user, when a `SELECT` or `UPDATE` or `DELETE` is issued,
PostgreSQL would compare the current user's transaction ID with the transaction ID on the row version,
and check, "okay, is this row version a row I created? If it's my row, then I should always see it. If it's others',
then I should only see it if that transaction had already committed."

This way, PostgreSQL allows different users to see different data based on the SQL's concurrent visibility control
requirements.
In jargon, this is called "Multiversion Concurrency Control" (MVCC).

Going back to how updates affect heap and secondary indexes.
This means, rows in heap is never updated in place; rather, new row versions are appended.
For indexes, it points to row versions instead of the raw rows.
Of course, PostgreSQL would periodically delete old row versions that are no longer used by any transactions
to release space.

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
INSERT INTO user_orders(user_id, product_id)VALUES (123, 45678);
COMMIT;
```

And guess what, it's a popular product item, so Bob and Alice actually try to order the item at the same instant.

Why is this a problem?

While Alice is deducting product 12345's inventory count and trying to create a order, in that split millisecond,
any other user, including Bob, is allowed to still read product 12345's inventory count but NOT update it.
This is another requirement of SQL's concurrency protocol.

Multiversion concurrency control enable concurrent reads on the same row, but we still need to ensure non-current,
exclusive update for a given row.

So how does PostgreSQL's architecture ensure mutually exclusive update?

Consider this analogy. If we are writing a simple in-memory computer program of some sorts
and we need to ensure mutually exclusive update, what do we do?
We use a Lock.

And that's logically what PostgreSQL does. PostgreSQL logically would put a lock on the row
to ensure mutually exclusive update.

But if we have, say, 100 thousand rows, does it mean PostgreSQL would need to create and maintain 100 thousand locks?
No, that would destroy the memory efficiency.
Instead, PostgreSQL relies on the fact that there's already a transaction ID on the row version,
and that row version's logical lock would only be released upon the whole transaction's commit or abort.
Because of this, PostgreSQL simply need to maintain lock / waiting at the transaction ID level instead of actual rows.

To illustrate the locking with an example:

1. Alice (transaction id = 1) is updating row (id = 123). A new row version is created, and Alice's transaction id 1 is
   written on there. Alice goes on to modify some other rows, so the transaction is NOT committed yet
2. Bob (transaction id = 2) also wants to update row (id = 123). It checks the latest row version and see that:
    - It's the row version Alice just created
    - Alice's transaction id = 1 hasn't committed yet
    - This means Bob should NOT update row (id = 123) until Alice has committed her transaction
    - So PostgreSQL would use lock to remember that, "transaction id = 2 is waiting for transaction id = 1 to commit or
      rollback", and transaction id = 2 (Bob's) is now blocked from doing anything further
3. After Alice transaction id = 1 commits or abort, PostgreSQL removes the blocking for Bob's transaction id = 2.
4. Bob then checks to see that Alice's row version is already committed / aborted (which, it is), and can safely proceed
   with next steps

## Durability

First, we need to understand that, disks are naturally durable.
SSD and HDD have mechanisms built-in (like, RAID) to ensure data won't easily be loss even if a part of the disk fails.
And, SSD and HDD exposes a hardware level API to ensure any data update in a 4KB unit would all succeed or fail,
but no partial updates.

Then why does PostgreSQL's architecture need to worry about durability?

As said earlier, PostgreSQL has the Buffer Cache mechanism
that coordinates all disk accesses into 8KB units called "page" and caches popular pages to increase read performance.

Thus, to achieve durability,
don't we just need to flush the updated page to disk and update the cached person in RAM too?

In theory yes. PostgreSQL simply needs to flush the pages to disk as they get updated,
and durability is achieved. But the problem is performance.
For a UPDATE query, a new row version is created in the heap, a few index entries in BTree might be affected,
the transaction status also needs to be updated. This means at least 1 if not multiple 8KB pages need to be changed.
Now suppose we have 100 transactions all updating different data.
If we proactively flush pages everytime it's changed, PostgreSQL would quickly be overwhelmed with all the disk IOs...

So how to ensure durability without having to flush a 8KB page everytime its changed?

The key observation is that, every time a page is changed,
it's likely that only dozens or at most hundreds of bytes are affected within that page.
Another observation is that, the changes only need to be flushed to disk upon the acting transaction's commit.
If the transaction hasn't committed and the machine fails, by SQL requirements,
the changes shouldn't take place, that's why we don't need to flush it to disk until that transaction commits.

Driven by these two observations,
PostgreSQL's architecture is engineered with a powerful mechanism that ensures data durability and performance:
Write-Ahead Log (WAL).

The big idea behind Write-Ahead Log is that,
instead of having to flush those 8KB pages to disk every time they are changed, we defer their flush indefinitely.
Instead, we would record all page modification events
(ex. "page id = 123's bytes between 125 to 434 had been changed" to 0x123aoifasdf...)
across all the pages to a centralized log, and that log is called our Write-Ahead Log.
Write-Ahead Log is implemented as a series of files on disk.

And guess what, write-ahead log itself doesn't need to be flushed to disk immediately too.
It just needs to be flushed to disk whenever a transaction commits.

Had we used the naive method of flushing a page every time it's changed,
PostgreSQL might only be able to support, say, 100 modification queries per second.
With Write-Ahead Log, PostgreSQL is able to, say, do 5000 modification queries per second.
Not an exact number, just for intuitive explanation.

And the reason why Write-Ahead Log would speed up page modifications by so much is because,
it only appends the changes in dozens or hundreds of bytes instead of writing a 8KB page,
and it's able to defer the logged changes to be flushed to disk in batch too until a transaction commits.
This ties back to the "two observations" said a few paragraphs ago.

To summarize, Buffer Cache constrains low level data movement to 8KB pages and massively speeds-up reads,
and our Write-Ahead Log enable pages to be modified with great throughput while ensuring durability.

## Atomic updates

In SQL's ACID requirements, atomic updates means, in a transaction commit or abort,
all changes must occur or not together as 1 inseparate thing, hence atomic.

Here's a concrete example:

```sql
BEGIN;
UPDATE balances SET money = money - 10 WHERE user_id = 1;
UPDATE balances SET money = money + 10 WHERE user_id = 2;
```

And then we might do `COMMIT` or `ROLLBACK`.

This example means user 1 wants to send user 2 $10.

If the commit goes through, then user 1 should end up with $10 less and user 2 $10 more.
If the commit doesn't go through because of rollback, or because it violates some data constraints,
or because it creates a deadlock, or PostgreSQL crashes in between,
then user 1 and user 2's balances should not be changed at all.

How does PostgreSQL's architecture support the atomic update requirement?

Through MVCC and WAL. And we've explained these earlier.

With its row version mechanisms, MVCC never updates rows in place,
but instead MVCC always create new versions of a row
and tracks whichever transaction id created that row veresion as metadata.

Then, if commit goes through, we just mark that transaction id as completed.
And logically all the changes would kick in together as one, thus atomically.
On the other hand, if we need to rollback, we just mark that transaction id as failed.
And logically all the changes would disappear together as one, thus atomically.

Finally, as explained earlier, WAL is there to ensure committed changes are durable and uncommitted changes are not
in light of power outage or any RAM failure.


## Consistency
We've talked about atomic, isolation, and durability in ACID. Let's finally talk about consistency.

Consistency is a murkier topic than the previous 3, and it seems that people have varying definitions on this.
But in general, consistency in PostgreSQL and relational databases as a whole means:

1. All the inserted rows must match the table definition or be rejected.
   - If a field is an integer, then the inserted row must have that field as an integer
   - If a varchar field says the length must be under 255, then the inserted row must have that field be short enough
2. UNIQUE constraint, foreign key constraint, primary key constraints must be respected
3. Custom defined CHECK constraint must be respected
4. Logical data consistency. If Alice sends Bob $10, then their balances at the end of the transaction must match up and be consistent. However, this bleeds into "Atomic, Isolation, and Durability" though, and this point, from my reading, frequently have varying definitions.


How does PostgreSQL's architecture ensure consistency then?
It's relatively straightforward. For every new row version created, check if it's valid based on
field types, UNIQUE constraint, foreign key constraints, custom constraints, whatever.
If it's not, then rollback the entire transaction with MVCC.


## A quick recap before continuing

If you go back to the earlier section [The Purpose of PostgreSQL](#the-purpose-of-postgresql),
we said that PostgreSQL is designed to do these things:

1. Store data in the "relational" paradigm
2. Support efficient querying and updates
3. Support concurrent querying and updates ("I" in ACID)
4. Support durable updates ("D" in ACID)
5. Ensure the updates in a transaction are atomic ("A" in ACID)
6. Ensure the updates don't affect the data consistency ("C" in ACID)

We have gone through all the mechanisms PostgreSQL is architectured with to satisfy each of the above requirements.
These mechanisms are:

1. Heap storage
2. Indexes
3. Buffer Cache
4. Write-ahead log (WAL)
5. MVCC with row versions and locking

But that's not all.
There are still a couple more important architectural components to be discussed.
In the next few sections, we will use the Life Cycle of an SQL Query to illustrate
how everything we've talked about come together, and explore the stuff we haven't talked about yet.


## The Life Cycle of an SQL Query

When PostgreSQL is started on a machine, its master process spawns,
and also spins a few background processes, some being:

1. WAL writer (writes WAL entries to disk)
2. Writer (eventually flushes modified pages in Buffer Cache to disk)
3. Auto vacuumer (removes old row versions, etc.)
4. Statistics collector (collects statistics on tables and indexes. More on this in a second.)

The master process also allocates a global memory region for Buffer Cache, transaction management, etc.

Now, whenever a new connection is established to PostgreSQL,
the master process forks a new worker process and hands off the connection to that worker process
to serve all future SQL executions for that new connection.
Meanwhile, the master process tracks and monitors the health of all worker processes present
and respawn ones if they die.

Now, suppose the user issues a few SQLs like this:

```sql
SELECT * FROM users WHERE id = 123;
```

```sql
BEGIN;
UPDATE users set username = 'iam_joe' WHERE id = 123;
COMMIT;
```

```sql
SELECT
    user.id,
    user.name,
    COUNT(order),
    SUM(order.amount) OVER PARTITION BY (country.continent)
FROM user
JOIN order ON order.user_id = user.id
JOIN country ON user.country_id = country.id
GROUP BY user.id, user.name
ORDER BY SUM(order.amount) OVER PARTITION BY (country.continent)
LIMIT 10
```

Upon receiving each SQL query, the worker process primarily:

1. Parses the SQL query string into a structuralized language tree called "abstract syntax tree" and ensure it's grammatically correct
2. Initializes transaction context and MVCC metadata
3. From the structuralized language tree, evaluates a few different execution plans and choose the seemingly optimal plan
4. Executes the optimal execution plan
5. Return result rows

Step 1 is just converting a raw string of SQL statement to a data structure so that computer can understand better.

For step 2, as a recap, MVCC compares the current transaction ID to the transaction ID on row versions
to resolve which row versions should be visible to the current transaction.
And step 2 simply initializes the various metadata data structures needed to facilitate MVCC transactions.

For step 3 and 4, let's zoom in a bit.
They are called "query planning and execution". A lot of important things happen here.

### Query planning

At the lower level, PostgreSQL can:

1. Scan row versions from heap, unordered
2. Lookup row versions from heap, given their tuple IDs (low level identifiers for a row)
3. Scan tuple IDs from secondary BTree and HASH indexes, given some filter condition

For a simple query like `SELECT * FROM users WHERE id = 123`, to execute the query, we have a few options:

1. Just scan all the row versions from users, resolve the visible ones against MVCC, and return the ones that match the filter criteria id = 123
2. If there's a BTree index ordered by id, then we can just the BTree data structure to efficiently find tuple IDs where id = 123, lookup the actual row versions from heap, resolve visibility against MVCC, and return them

Which one to choose? Likely option 2, because looking up by BTree would be a lot faster than scanning every row.

Now consider a more complicated query like this:

```sql
SELECT
    name, username, age
FROM users
WHERE
    (is_active = true AND nation IN ('China', 'United States') AND age BETWEEN 28 AND 36)
    OR (is_active = false AND is_flagged = true)
ORDER BY login_frequency DESC
```

And suppose there's a few different indexes out there:

1. A BTree unique index on username
2. A BTree index sorted by (age ASC, login_frequency DESC)
3. A HASH index on nation
4. A BTree index sorted by (is_active ASC, nation DESC)

To execute the above query, which indexes should PostgreSQL use?

To make the matter even worse, suppose we also JOIN the query 4 more times on a few other tables,
have 3 subqueries, aggregate by some columns, and finally sort the result by some columns.

Now the question explodes even further:

1. What order should the JOIN happen? Table A join B join C is equivalent to B join C to A. There's like O(N!) join possibilities. And different JOIN order result in different performance because joining A and B first would make the result super small, but joining B and C first would make the result set explode
2. For each adjacent pair of table, like, table A and B and B and C, should the relevant rows be joined by a double for loop, by a hashmap, or by two pointers if they are both sorted?
3. For aggregation, can we fit all the data in RAM, or do we need to spill it to disk? Do we build a hashmap or use a for loop if the data is already sorted?
4. What parts of the query can be parallelized onto multiple CPUs / forked workers?
5. Should we rewrite the query so that top level filter conditions are pushed down further?

In short, there's so many different ways to execute the same SQL query and all arrive at the equivalent correct result.

It would take a few chapters of a book to explain them in depth.
But, in short, just know that, when the user writes a SQL and executes it in PostgreSQL,
PostgreSQL would evaluate the different execution plan of the SQL by considering the individual and collective costs of the JOIN clause, SELECT, GROUP BY, etc,
and pick the execution plan with the least cost.

Now the question boils down to, what exactly do we mean by the "cost" of a plan? It means:

1. How many rows it would have to touch. For a full heap scan, it's however many rows is in there. For a BTree index scan, it's Log(N) of rows. Joining A and B first might give 1 million rows while B and C first might give just 1 thousand  rows
2. How big is the average row width? If a BTree index have 2 integer columns it would be 8 bytes. A heap scan might be like 120 bytes
3. CPU overhead. If we do a double for loop join it's O(N^2) for number of rows

And the final cost is something like rows * row width * 5 + cpu overhead. I forgot the exact number.
See PostgreSQL source code for exact numbers.

Cool. If we can calculate the cost for each plan, we know which plan is the best, and we just executes that plan.

But how do we estimate, say, how many rows might the index scan return, might the JOIN return, etc?

### Table and index statistics
If you remember in the opening paragraph of [query planning](#query-planning),
PostgreSQL has a "Statistics collector" process always running in the background collecting statistics on data in indexes and tables.
Why is this needed? This is needed so that we can use the statistics to estimate query plan costs!

For each table and index, PostgreSQL collects these statistics:

1. How many rows there are
2. How many pages (the 8KB units) does it occupy
3. What portion of the column values are NULL values
4. How many distinct values are for each column
5. What are the most common values for each column
6. Histogram of column values
7. For each column, average length. If it's a int then its 4 bytes. If it's text then it could be like 10 bytes or 100 bytes
8. How correlated are all the rows relative to this column. If a column is called "timestamp", then the rows are likely very sorted by the timestamp

Note that the statistics do NOT need to be 100% accurate.
They just need to be somewhat accurate to guide query planning.

With all of these statistics, PostgreSQL is able to look at a query plan,
and infer how many rows might it need to look through and how wide are the rows.
And then pick the optimal plan and executes it.

### Executing query

From the optimal query plan, PostgreSQL finally can execute it.
It runs the BTree traversal code, checks MVCC visibility,
interacts with the Buffer Cache and the underlying Write Ahead Log,
actually runs the JOIN for loop or hash tables, and more.

## Conclusion

As developers, we just issue SQLs to PostgreSQL and it just works.

But so much effort goes behind the curtains of PostgreSQL's architecture to ensure our SQL queries:

1. Can be concurrent
2. While still being correct and safe. In jargon, it means atomic, consistent, isolated, and durable (ACID)
3. While still being fast

The SQL query can be as simple as a CRUD lookup,
or a complicated 300 lines analytical SQL with subqueries, common table expressions, JOINS, window functions, aggregations, sorting, etc.
and PostgreSQL's query parsing, planning, and execution will faithfully give us the correct rows / updates.

Isn't it magical?

It's not magic. It's the fruit of decades of database research and engineering.
Ever since Ted Codd laid forth the conceptual foundation of relational databases,
from Oracle to MySQL, corporations and open source projects alike never stopped chasing
bringing the conceptual to practicality.

Among the available relational database systems,
PostgreSQL remains my favorite, for its powerful set of features, intuitive usage, and timeless architecture.
The more NoSQL databases I get more exposed, the more I realized that,
many NoSQL databases' in effect are only faster than PostgreSQL by sacrificing their features, ACID, or other aspects.

I built my first software project Leetdeal (see [Projects](/projects)) with SQLite, then migrated to MySQL.
Ever since UCSBPlat, my projects had been PostgreSQL, and many pain points just miraculously disappeared.

By the time I finished high school, I thought I had learned it all about database --- and of course I was wrong haha.

As I built more projects, I realized that common table expressions exist, window functions exist,
you can JOIN things again and again, you can create materialized views, schemas...
I realized you can natively replicate PostgreSQL to different instances to multiply its read capacity.
I realized that with open source options like Citus, you can shard PostgreSQL to multiply its write capacity.
I realized indexes exist (should have found out about it earlier!), I realized permission control exist.
I sporadically read about MVCC, vacuum, buffer cache, to name a few,
but the concepts were so hard to grasp, as they are so scattered.

This article cohesively condenses the past few years of my understanding of PostgreSQL's internal architecture.
There's definitely errors in it, please [contact me](/contact) and I'll correct them accordingly.
Or, if you have something to share, let me know too!

I love PostgreSQL.

Jiaming Liu

Feb 20, 2026

## Next Steps

If you want to learn more about the internals of PostgreSQL, these are the resources that helped me the most:

1. [The PostgreSQL Internals Book](https://edu.postgrespro.com/postgresql_internals-14_en.pdf)
2. [The Official PostgreSQL Documentation](https://www.postgresql.org/docs/current/index.html)
3. [The PostgreSQL Source Code on Github](https://github.com/postgres/postgres?referrer_channel=typeahead&referrer_query=postgre)
