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
