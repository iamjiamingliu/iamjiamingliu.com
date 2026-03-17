---
title: MinIO Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-03-10 14:36:57
updated_at: 2026-03-10 14:36:57
excludes_from_index: True
---

## Foreword

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
This is because, unlike files, objects:

1. Cannot be partially edited. If you are on a local file, you can edit it. But for architectural simplicity and use case design, object storage database only support creation and deletion of objects in full.
2. TODO

But really, objects and files are the same thing. They are just whatever arbitrary content you want to be stored.
Whether it's a TXT, image, PDF, Excel sheet, Parquet click logs... anything.

Many things in software engineering, or in the world in general, that have funny names, but really, they are not complicated.

Let's take a closer look at the architecture behind MinIO, the open-source object storage database.
Experience with the usage of AWS S3 or MinIO is necessary for understanding the rest of this article.

## Content Delivery Network

## HDFS

## A Fun Question

Why not just store everything in Postgres or RocksDB?

You can, but you shouldn't.
PostgreSQL and RocksDB can store arbitrary bytes, however,
if you look into their architectures, their internals are designed around the assumption that
the payloads would be a small row or a small key-value pair,
but for PDF, images, or whatever file content, the payload size can be a, say, 2MB image file or 100 gigabytes click logs Parquet file,
which will kill the performance of PostgreSQL and RocksDB.

It's all about different granularity. Pick the right tool for the right use case.
Object storage databases like MinIO or S3 is meant for large data granularity in MBs or GBs,
thus, use object storage.

Or, as said in the beginning of this article, if everything can fit comfortably in one local file system,
just use the local file system.
