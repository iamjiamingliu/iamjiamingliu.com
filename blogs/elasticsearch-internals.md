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

For both vertical search engine (the searchbar within a site, like Amazon's searchbar)
and horizontal search engine (search engine for world-wide-web, like Google) alike,
the workflow boils down to **ingestion, indexing, searching, and tracking.**

For vertical search engine, ingestion means bulk loading or listening for changes of domain data (ex. Amazon product items)
so that they can be indexed next.
For horizontal search engine, ingestion is a magnitude more complicated, as it means crawling the world wide web.

For indexing, search engines would normalize, distill, and derive analyzed / inferred insights from the original content.
For example, Amazon product search might first normalize the description to raw string,
distill the information by extracting brand names mentioned in the description and converting the information to ML embeddings,
and infer how popular this product might become given the seller's past sales volume.
For Google search, the derived insights would include page rank, page quality score, to name a few.

Then, all the original, normalized, distilled, and analyzed information will be stored to a search database
to facilitate fast retrieval.
Google has its own storage and retrieval engine,
Amazon builds theirs on top of Lucene, and Github directly uses ElasticSearch.
So this is where ElasticSearch / Lucene comes in for a complex search engine: **as the storage and retrieval engine**.
For any of the previous steps like ingestion and content analysis, that's not for ElasticSearch to do.

Now, whenever a user types in a query, specifies some filters, and hit "search", 2 workflows happen:

1. Typeahead: autocomplete queries, directly search items as they type, and correct typo
2. The actual search: after the user hit "search", the search engine would
    - Perform query understanding
    - Retrieval candidate items, aka items that might be relevant
    - Rank the candidate items, aka what which items are actually relevant and how to order them
    - Pack and return the items

For typeahead, ElasticSearch exposes built-in typo correction, prefix search, and query suggestion features based on classical algorithms,
so smaller search engines would **directly use ElasticSearch to build the typeahead experience**,
while more robust search engines like WeChat search, TikTok Shop search, and definately Google would
build their own typo correction and query suggestion functionalities with ML, personalization, and more.

For the actual search,
ElasticSearch of courses facilitates **classical BM25 retrieval as well as embedding cosine similarity retrieval**,
and exposes the option to **rank the results with hard-coded weights**.
For more robust search engines, the retrieval functionality of ElasticSearch is efficient and powerful,
as the underlying data structures are state of the art and don't justify using other options anyways.
But for ranking, more robust search engines frequently need to calculate personalization score,
boost by trending metrics that need to be looked up separately,
and by many more things that isn't within ElasticSearch.
Thus, more robust search engines would have a separate ranking phase after the initial retrieval.

Finally, robust search engines would track every user's impression, click, purchase, and other relevant business events
to further understand the quality of each piece of content, relevant, and more.
This means computing the all-time, hourly, etc. click-through rate of each search result,
refund-rate, and more. ElasticSearch plays no role in the calculation of these metrics,
and once these metrics are calculated, they can be stored elsewhere to be used during the separate ranking phase
or be inserted into ElasticSearch in its bundled ranking capability.

In short, for simple search engines,
you don't need content analysis,
you don't need complicated ranking,
you don't need user behavior tracking,
so just **dump relevant content to ElasticSearch and have it do everything**
from retrieval and ranking to typo correction and query suggestions.

For complex search engines though, ElasticSearch sits in the exact middle of the long lifecycle of a search engine's workflow
that facilitates content **storage and retrieval**, and everything else is separate code.

### Can't we just use Postgres?

Or, can't we just scan every piece of content and regex match it against the query?

Of course you can. For a simple site with not much content, just scanning everything and do regex match is enough.
ElasticSearch here would be an overkill.
For a medium site that has some content but doesn't require many other functionalities,
using PostgreSQL's built in `LIKE` statement or `ts_vector` is also sufficient.

When there's a lot of data, we cannot afford scanning everything.
When we need efficient search as you type, typo correction, weighted scoring,
complex filtering rules, text analysis, facade search,
and all the features crucial to a complete search experience,
PostgreSQL's `ts_vector` or `LIKE` statements simply do not support these features and are too slow.

Thus the need for a dedicated search database like ElasticSearch.

### Lucene, ElasticSearch, and OpenSearch

Lucene is the java **library** to facilitate text analysis, data structures for storage and retrieval,
and the underlying IO interactions to manifest the data structures.
It also comes with typo correction and other nice features needed in search.
It is just a library, not a standalone server.

ElasticSearch sits on top of Lucene by leveraging Lucene's capability and packaging it as a **standalone server**.
It also exposes a HTTP JSON API, supports replication and sharding, and high-level declarative usage instead of imperative code.

The rest of this article discusses Lucene the library first,
and then discusses how ElasticSearch sits on top of Lucene.
OpenSearch is not discussed but its big ideas are inherited from ElasticSearch anyways.
