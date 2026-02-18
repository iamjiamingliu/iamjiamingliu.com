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

```
SELECT * FROM my_table LIMIT 10
```

```
SELECT * FROM my_table WHERE user_id = 123
```

```
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
we would then have to put our data as a dictionary/hashmap or a sorted list.
Then, looking up the relevant data just means dict.find(key) or binary searching over that sorted list,
which is super efficient comparing to having check everything one by one.

Now back to PostgreSQL.
To support efficient querying, PostgreSQL uses the same ideas as if we need to write an in-memory program:

# TODO
