---
title: MinIO Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-03-10 14:36:57
updated_at: 2026-03-10 14:36:57
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

## The Distributed Architecture

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

### Reed Solomon Erasure Coding

TODO

### The Actual Architecture

TODO

### All the Overhead, For What?

Arguably, if MinIO doesn't care about fault tolerance or scalability,
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
