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

## Context

### Why the extra context

For databases like PostgreSQL,
since almost every software application needs some structuralized data to be stored,
its usage and intuition behind its architecture are more familiar to the general masses.

For ElasticSearch, its use case is primarily for search engineering on core content or server logs.
Yes occasionally ElasticSearch is also used as analytical databases, but it's used there a lot less so than, say, ClickHouse.

Thus, before we dive into ElasticSearch's architecture,
it's helpful to first understand a bit of context on the domain of search engineering,
as it is a very specific usage domain.

### Search engineering

At a very abstract level, many software products are all about [domain driven design](https://en.wikipedia.org/wiki/Domain-driven_design).
In my taxonomy, a software must facilitate:

1. Users' discovery of domain objects
2. User triggered workflows, business rules, and state changes on domain objects
3. Computer derived analysis on business events
4. Computer inferred prediction for relevant business forecasts

Take Amazon shopping as an example. To plug it into the above 4 bullet points:

1. The domain objects in this case includes products for sale. Users must browse categories, search for, or get recommended products
2. The user triggered workflows include adding products to shopping cart, purchasing items, and requesting for refund.
3. The computer derived analysis include how many users viewed a particular item last hour and what's the conversion rate.
4. The computer inferred prediction include which products are inferred to be similar and what's the predicted demand for a product

Take any other well known internet-scale software, and they will fit these 4 bullet points in one way or another.

And each of the 4 bullet points **roughly** correspond to 4 different but overlapping and intertwined domains of software engineering:

1. Content discovery: search and recommendation engineering
2. Backend engineering: all about workflows, business rules, and state changes
3. Data engineering: all about analyzed / derived data
4. ML engineering: all about predicting

So we see that content discovery sits at the first layer of the user journey,
because without them, the users won't even know what is there.
For a small site that doesn't have many things on it,
content discovery usually means a simple pagination.
But for internet-scale software like Amazon shopping, as there are billions of products for sale,
content discovery becomes much more important and sophisticated to implement.

Production scale content discovery boils down to 2 things: recommendation and search.
Recommendation is when the user hasn't express any explicit intent yet,
so we recommend things based on implicit intent of past user behavior, trending items, and many more latent signals.
Search is when the user has expressed an explicit intent to find something,
so we return results based on the explicit string of user query and the user specified filters / sorting,
plus implicit intent analyzed from the user query and past user behavior, trending items, and other latent signals.

### The beauty of search engineering

So in a way, search engineering uses recommendation engineering, as the search results are often times personalized.
Actually, search engineering also uses data engineering, as it needs metrics like item click-through rate
to boost search results, and computing such metrics is data engineering.
Finally, search engineering definitely uses ML engineering too,
as the latest retrieval technology involves using text embeddings and rankings generated by transformer models,
content and query analysis powered by NLP NER, and many more.

This is why I was so fascinated with search engineering and decided to build my own search engine project [SearchGit](/projects).
This experience allowed me to learn about and practice backend, data engineering, and ML engineering
all at once;
it was the first time I get some seriously hands-on with data engineering and ML engineering;
and I was able to learn about how backend, data, and ML come together to form the architecture of modern software.

### Where Elasticsearch comes in
