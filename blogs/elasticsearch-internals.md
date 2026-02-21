---
title: ElasticSearch / Lucene Internals
description: What's happening under the hood?
tags: [ Internal Architecture ]
category: Tech
created_at: 2026-02-20 23:19:13
updated_at: 2026-02-20 23:19:13
excludes_from_index: True
---

## Foreword

As the industry standard search database (along with its complicated twin OpenSearch),
ElasticSearch provides search engineers with a bundle of built-in data structures, text analysis tools, query executor, and other helpful features like typo correction
to facilitate storage and retrieval in the context of search engineering.
Its core functionality is powered by Lucene the java library,
and ElasticSearch kind of just wraps around Lucene to expose a higher level query language, HTTP interface, and standalone instance;
of course it also provides features like replication and sharding.

I was very hesitant on writing about ElasticSearch's internal.
Because, from my personal project [SearchGit](/projects),
I had the pleasure of knowing a few engineers who worked on the internals of OpenSearch,
built the search infra for big names like Github and Amazon,
and knows several magnitudes more about ElasticSearch and Lucene than I do.
I was worried that writing about ElasticSearch and Lucene make me look naive and stupid.

But by the same logic, I probably shouldn't have written any technical blogs at all,
because almost any Postgres / ClickHouse / Elasticsearch / etc. professionals
would know a magnitude more about the piece of technology they work on a daily basis deeper than I do.

The point of writing me writing my blog is to jot down what I know and think about each technology,
and how I connect the dots together with different technologies.
I guess it's about adding my own touch and saying it in my own voice that matters more.

So here we go. ElasticSearch and Lucene internal architecture. Explained in my own voice.
I assume you as the reader is familiar with the usage of ElasticSearch.
