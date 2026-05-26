---
title: MinIO Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-03-10 14:36:57
updated_at: 2026-05-25 20:59:57
excludes_from_index: True
---

## Why Object Storage

As human computer users, we create folders and files on our laptops to store txt, PDFs, videos, spreadsheet, or whatever file we want.
We are also able to edit the files via Word, Excel, or any editor we desire.

Automated software systems likewise have such need to store files.
If I am Canvas the university curriculum platform, I need to store the PDFs student submitted for grading.
If I am Instagram the social media, I need to store the images they users uploaded to be shown to other users.
If I am Amazon or really any large scale software platform,
I need to store analytics data like user click events, purchase events, server error logs, and more.

If the data fit in one machine, software systems could simply store the files in the local file systems.
The blog you are reading right now, for example, is stored as Markdown files in a folder on my cloud server.

But if I am Instagram where there's TBs if not PBs of user uploaded content,
and TBs if not PBs of user events, server logs, or any data of interest,
I can't fit everything in one machine.
Plus, I also have the need to expose the files over the internet for remote access.
And, it would be nice if there's mechanisms like fault-tolerance and replication built-in
for high-availability and scalability needed in large scale software systems,
which is something a simple local file system lacks.

Thus comes the need for object storage database like AWS S3 or MinIO,
which leverages multiple machines under the hood and expose a unified interface over HTTP or other network protocols
to store and retrieve whatever files need to be stored,
with mechanisms like fault-tolerance and replication built-in.

Actually, the "files" in such object storage database is not called "files", but "objects".
This is because, unlike files, objects cannot be partially edited. If you are on a local file, you can edit it.
But for architectural simplicity and use case design, object storage database only support creation and deletion of objects in full.

But really, objects and files are the same thing. They are just whatever arbitrary bytes you want to be stored.
Whether it's a TXT, image, PDF, Excel sheet, Parquet click logs... anything.

Many things in software engineering, or in the world in general, that have funny names, but really, they are not complicated.

Let's take a closer look at the architecture behind MinIO, the open-source object storage database.
Experience with the usage of AWS S3 or MinIO is recommended for understanding the rest of this article.

## Understanding MinIO's Architecture

### Erasure Coding

MinIO's architecture is designed around the erasure coding mechanism,
which provides fault tolerance by
slicing the stored data into chunks,
computing some derived data based on the chunks,
and storing the derived data along with the original chunks.
Then, in case some chunks become unavailable due to crashes or network error,
the derived data would enable constructing the missing chunks,
thus enabling fault tolerance.

In a world without erasure coding,
to enable fault tolerance,
we need to duplicate the same data N times
so that if N - 1 of the nodes crash,
at least 1 node alive will still have the data.

But simply duplicating the data N times is highly inefficient.
In the smallest case when N is 2,
to provide fault tolerance for 1 TB of original data,
you need to use 2 TB of actual storage.
If N is 3, you need 3 TB.

So the golden question of engineering comes in:
how can we do better?
How can we provide fault tolerance without having to incur so much overhead?

Enters erasure coding.
Suppose we have a file of size 100 GB.
We split it up into 2 chunks each of 50 GB.
Next, we compute the XOR of the 2 chunks, which is another 50 GB.
Finally, we store the 2 chunks each of 50 GB, and the XOR 50 GB, for the total of 150 GB;
each chunk and the XOR would be stored on different physical nodes.

During retrieval, suppose all nodes are healthy,
then we just need to fetch the two original chunks from the nodes they live in.
Now suppose one of the nodes storing the original chunks fail.
Then, we just need to grab the XOR 50 GB, apply XOR against the other chunk of 50 GB original data that's still available,
which, by property of XOR, will reconstruct the other 50 GB chunk of original data!

In effect, we used 150 GB of storage to enable fault tolerance for 100 GB of original data using XOR erasure coding.
Had we used simple duplication, we would have used at least 200 GB of storage.

The actual erasure coding used in practice, in MinIO and in other systems,
is not XOR. XOR is simply to illustrate the concept.
The actual erasure coding used is a more sophisticated algorithm
called Reed Solomon,
which provides strictly storage efficiency and higher fault tolerance than simple XOR.

### Reed Solomon

As the industry-standard erasure coding algorithm,
the idea behind Reed Solomon is very similar to XOR erasure coding:
split up the data into chunks, compute the derived chunks,
and store the original chunks and the derived chunks.
Then upon failures, retrieve the derived chunks to reconstruct the missing original chunks.
The difference between Reed Solomon and simple XOR lies in how the derived chunks are computed,
and how to reconstruct the original chunks with the derived chunks upon failure.

In Reed Solomon,
the derived chunks are called **parity** chunks,
and the original chunks are called **data** chunks.

Suppose the original data had been split into 3 data chunks, denoted as C1, C2, and C3.
In the simple XOR erasure coding,
we would create exactly 1 parity chunk: `P1 = C1 XOR C2 XOR C3`.
In Reed Solomon,
we would create multiple parity chunks, differentiated by the coefficients in front of each data chunk.
For example, we might have P1 still being `C1 XOR C2 XOR C3`,
but we will also have `P2 = (1 * C1) XOR (2 * C2) XOR (3 * C3)`.

By adding coefficients in front of the XORs,
Reed Solomon allows us to create many distinct combinations of the original data chunks that result in different parity chunks.
The coefficients are the core enhancement Reed Solomon offers over the simple XOR erasure coding.

When we have K data chunks and M parity chunks,
Reed Solomon requires that
any coefficient vectors subset of size K must be linearly independent.

In the above example, the coefficient vectors are the `[1, 1, 1]` for P1, `[1, 2, 3]` for P2,
and `[1, 0, 0]` for C1, `[0, 1, 0]` for C2, and `[0, 0, 1]` for C3.
The coefficient vectors in this example are valid for Reed Solomon,
because any K=3 subset of them are linearly independent.

Why this linearly independent rule?
Well, for M data chunks and K data chunks for a total of K + M chunks,
Reed Solomon tolerates up to any M of the K + M chunks failing.
Then, this leaves us with at least K chunks, some being data chunks and some being parity chunks,
and we can recover the missing data chunks by solving a system of linear equations,
based on the linearly independent coefficient vectors.

Using our example above, suppose with only have P1, P2, and C3 available, with C1 and C2 dead,
we can still construct C1 and C2 because we have a system of these linear equations:

```text
1 * C3 = C3
(1 * C1) XOR (1 * C2) XOR (1 * C3) = P1
(1 * C1) XOR (2 * C2) XOR (3 * C3) = P2
```

Because Reed Solomon enforce that any subset of size K of the coefficient vectors are linearly independent,
there's a guaranteed solution to the above problem.

To illustrate, if we solve it manually, the process is:

```text
(1 * C1) XOR (1 * C2) = P1 XOR C3
(1 * C1) XOR (2 * C2) = P2 XOR (3 * C3)

Let:
A = P1 XOR C3
B = P2 XOR (3 * C3)

(1 XOR 2) * C2 = A XOR B

C2 = (A XOR B) / (1 XOR 2)
C1 = A XOR C2
```

Note that, C1, C2, C3, P1, P2...
these are not simple integers.
These are arbitrarily large bytestream.
If C1, C2, and C3 are the data chunks that represent user avatar image for example,
then each chunk could be like 20MB large.

That means, the `XOR` operation would still work perfectly fine on them.
The multiplication `*` and division `/` are somewhat different than multiplication and division on integers though,
since we are dealing with bytestream.
These specialized multiplication and division operations
are applied as if each bytestream is a finite field,
which I don't understand fully, so I will leave it to you the reader to carry out your own exploration.


### MinIO's Implementation

In the most simple scenario where,
perhaps as a hobby project,
MinIO only has 1 node configured,
the core mechanism of erasure coding doesn't really kick in because one node alone can't provide any fault tolerance,
so it behaves very much like an HTTP wrapper for file storage (excuse me, object storage).

In the robust scenario where,
for enterprises and whatever other serious use case demands,
MinIO would have multiple nodes configured together,
and the core mechanism of erasure coding does kick in.
This is where its purpose shines.

The logical hierarchy for MinIO's nodes in a robust deployment goes like this:

1. At the very bottom, you have physical hard drives, preferably NVME or faster instead of slower HDD
2. Multiple physical hard drives would be bundled together, along with other important stuff like RAM and CPU, to form a machine. That machines would then be running the MinIO executable. This is considered a node.
3. Multiple machines, aka nodes, would be bundled together, to logically form an erasure set
4. Finally, all the erasure sets together logically make up the entire MinIO server pool (aka cluster)

This is a diagram from MinIO's documentation to illustrate the above point:

![](https://docs.min.io/aistor/operations/core-concepts/images/erasure-coding-erasure-set.svg)

Whenever a new object is created,
the write path goes like this:

1. Based on the hash of the object key, it will be routed to an erasure set
2. The object is split up into K data chunks, and then their M parity chunks are computed
3. The data and parity chunks will then be stored onto the nodes in that erasure set, along with metadata

Whenever an object needs to be fetched,
the read path goes like this:

1. Based on the hash of the object key, determine which erasure set this object is stored
2. Go fetch up the object's data chunks from the nodes in that erasure set. Given the property of erasure coding, any K data chunks would suffice because the complements can just be reconstructed using Reed Solomon
3. Return the merged result as one unified object
4. If any repair needs to be done, such as a data or parity chunk missing or corrupted, it can do so

So, it's a classic load balancing topology
based on the hash of the object key and then routed to the appropriate erasure set.
But you can imagine a problem with such hash based routing scheme is,
if any new node or erasure set is added, we need to somehow rebalance the existing routing schemes.
But it's not like resizing happens all the time, most likely, it only happens when the existing server pool runs out of space.
So, MinIO's solution is just:

1. It doesn't support downsizing well
2. If you want to upsize, you just add a new server pool (aka cluster), and then MinIO would have to check every server pool whenever it wants to write or retrieve an object

Once again, if MinIO doesn't care about fault tolerance or scalability,
then doesn't need erasure coding,
and its architecture could degenerate into a simple HTTP wrapper over the file system.
But MinIO must care about fault tolerance and scalability,
thus its architecture must be orchestrated around the complexity of erasure coding.

## Content Delivery Network

## HDFS

## One More Thought

Why do we need object storage?
Why not just store the bytes data of, say, a user profile image directly in Postgres or RocksDB?

You can, but you shouldn't.
PostgreSQL and RocksDB can store arbitrary bytes, however,
if you look into their architectures, their internals are designed around the assumption that
the payloads would be a small row or a small key-value pair.
But for PDF, images, or whatever file content, the payload size can be a, say, 2MB image file or 100 gigabytes click logs Parquet file,
which will kill the performance of PostgreSQL and RocksDB.

It's all about different granularity. Pick the right tool for the right use case.
Object storage databases like MinIO or S3 is meant for large data granularity in MBs or GBs,
thus, use object storage.

Or, as said in the beginning of this article, if everything can fit comfortably in one local file system,
just use the local file system.

And at the end of the day, object storage, relational databases, KV store...
they are all just some abstractions over the file system,
which by transitivity abstracts over the underlying disk or SSD.
At the end of the day, the bytes need to be stored somewhere.
