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
the lifecycle of a search engine boils down to **ingestion, indexing, searching, and tracking.**

For vertical search engine, ingestion means bulk loading or listening for changes of domain data (ex. Amazon product items)
so that they can be indexed next.
For horizontal search engine, ingestion is a magnitude more complicated, as it means crawling the world wide web.

For indexing, search engines would normalize, distill, and derive analyzed / inferred insights from the original content.
For example, Amazon product search might first normalize the HTML description to raw string,
distill the information by extracting brand names mentioned in the description and converting the information to ML embeddings,
and infer how popular this product might become given the seller's past sales volume.
For Google search, the derived insights would include page rank, page quality score, to name a few.

Then, all the original, normalized, distilled, and analyzed information will be stored to a search database aka engine
to facilitate fast retrieval.
Google has its own storage and retrieval engine,
Amazon shopping builds theirs on top of Lucene, and Github directly uses ElasticSearch.
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
and do many more things outside ElasticSearch.

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

For complex search engines though, ElasticSearch sits in the middle phase of the long lifecycle of a search engine
to facilitate just content **storage and retrieval**; everything else would be separate code on their own.

### Can't we just use Postgres?

If the original data like Amazon product items is already stored in PostgreSQL, why a separate ElasticSearch?

If we are a simple blog site and our articles are just markdown files, can't we just scan every piece of content and regex match it against the query?

Of course we can. For a simple site with not much content, just scanning everything and do regex match is enough.
ElasticSearch here would be an overkill.
For a medium site that has some content but doesn't require many other functionalities,
using PostgreSQL's built in `LIKE` statement or `ts_vector` is also sufficient.

When there's a lot of data, we cannot afford scanning everything.
When we need efficient search as you type, typo correction, weighted scoring,
complex filtering rules, text analysis, facade search,
and all the features crucial to a complete search experience,
PostgreSQL's `ts_vector` or `LIKE` statements simply do not support these features and are too slow.

Thus the need for a dedicated search database like ElasticSearch.

And it is a common practice to sync data that needs to be indexed from PostgreSQL into ElasticSearch
via a PostgreSQL change capture middle ware like Debezium and apply that change to ElasticSearch.

### Lucene, ElasticSearch, and OpenSearch

The rest of the articles discusses 2 things: Lucene and ElasticSearch.

Lucene is the java **library** to facilitate text analysis, data structures for storage and retrieval,
and the underlying IO interactions to manifest the data structures.
It also comes with typo correction and other nice features needed in search.
It is just a library, not a standalone server.

ElasticSearch sits on top of Lucene by leveraging Lucene's capability and packaging it as a **standalone server**.
It also exposes a HTTP JSON API, supports replication and sharding, and high-level declarative usage instead of imperative code.

OpenSearch is ElasticSearch's complicated twin.
Long story short, the company behind ElasticSearch "Elastic" tried to close-source ElasticSearch,
people got worried, and forked ElasticSearch into a permanently open source project called "OpenSearch".
OpenSearch is not discussed here but since it's the twin to ElasticSearch, we at least have to drop the name here.

That was a very long writing just to give you the context. Let's finally dive in.

## Lucene

At the top level, the Lucene library does 3 things:

1. Models any searchable item as document, and models a search query as a Query object
2. Breaks down fulltext field in a document or a query into a list of tokens
3. Stores documents to disk and retrieve documents based on query

Lucene implements each of the above phase of the life cycle with these java classes:

1. `Document`, `Field`, and `Query` class
2. `Analyzer` and `QueryParser`
3. `IndexWriter`, `IndexSearcher`, `Codec`, `Directory`, and `DirectoryReader`

Let's look into each of them.

### Document and fields

Document is simply a data holder to store searchable fields each with different types.
For ecommerce, a "product item" is a document with fields like product name (fulltext), category (keyword), price (double).
For Github, a "git repo" is a document with fields like repo name, stars, etc.

Analogous to relational databases like PostgreSQL,
each document would be the "row" in a table.
The difference is that Lucene does not require a strict table schema,
thus each document could have completely different fields and Lucene can handle that just fine.
This boils down to the fact that PostgreSQL is designed with strict data consistency philosophy,
while Lucene doesn't care about data consistency as long as they are searchable.
At the lower level it's because Lucene's data ingestion is on a per-segment basis (more on this later)
instead of row by row basis,
so the metadata with what fields exist and what's their types is on a per-segment basis instead of globally.
ElasticSearch wraps on top of Lucene and can be configured to ensure data schema consistency though.

For each field within a document, we have numeric field types that exist everywhere: double, float, and int.
Boolean doesn't exist natively so it is achieved with int or string instead.

But for string family of fields, we have something interesting here:
Lucene exposes two types of string family fields, `Text` and `Keyword`. What's the difference?

`Keyword` is the type of string we expect normally.
We can filter it by `=`, `>`, `<`, `IN`, `LIKE`.
It's like a normal string you see in Python, C++, etc.

`Text` is not "normal" in the sense that it doesn't behave as a normal string you see in Python, C++.
Instead, `Text` field is meant to be tokenized, retrieved, and scored with BM25 or TF-IDF or any other full text matching methods.
And `Text` is the backbone of classical search that Lucene provides.

Here's a concrete example. Suppose we have a `Document` with the following fields, their types TBD:

```python
# Psuedocode
news_article = Document(
   id=12345,
   title='Donald Trump visited Canada',
   description='Today, our President Donald Trump visited Canada and talked to their prime minister, talked about trade, etc.',
   category='Politics',
   timestamp='2026-02-23'
)
```

And you can imagine that, when a user types a query like _"trump's official visit to Canada"_ with a hard filter on category = politics, document 12345 should come up.

So what type should we give to field `category`? It should be a `Keyword` field.
Because we need to perform `=` on it. It should behave like a normal string in Python and C++.

What about `title` and `description`? It should be a `Text` field.
We should not perform `=` on it. Instead, we would be performing partial text match like BM25 on it.
This is because a user would almost never type the exact title, but a few relevant keywords,
and defining our field as `Text` tells Lucene to break it down as tokens and perform partial match instead of strict `=`.
The process of breaking down a `Text` field into tokens is called text analysis and will be discussed soon.

Traditionally, `Text` is what powered search.
In recent years, with the rise of transformers embeddings,
cosine vector similarity search has become another pillar to search.
In response, recent updates to Lucene supports the `KNNFloatVector` field type
to facilitate embeddings and cosine similarity match.

Embeddings are basically, given a text like "trump visiting canada" as input , the transformer model can spit out a vector of size 768 (or 368 or however large it needs to be)
of floats, like, `[0.23234, -0.9, 0.22, 0.001, ...]`.
And, when we search a query, we use the model to convert it to an embedding, and retrieve documents based on the
cosine similarity between the query vector and the document vector.

Compared to traditional search, embedding allows semantic match, multilingual search, typo tolerance, and more.
However, BM25 absolutely still shine when the user searches something specific.
Thus, modern search retrieval uses both BM25 and embedding vector KNN.

What's BM25? Discussed in the next section. Along with text tokenization analysis.

### Analyzer

In previous section, we dropped jargon like BM25 and TF-IDF to convey the idea that,
search databases don't simply do exact equality match,
but on partial string match and scoring.

Let's zoom in to BM25 and TF-IDF.
The entirety of Lucene's architecture is designed around BM25 and TF-IDF text matching,
and we need to understand them first, otherwise all the text analysis tokenization, codec data structures, and text scoring would be nonsense.

Suppose a user searches, _"Trump's official VISIT to Canada"_,
out of the millions of documents in Lucene that represent news articles,
which ones should we return? Aka which ones are relevant?

At a bare-minimum, we should return documents that mention one of:

1. trump
2. official
3. visit
4. to
5. canada

And this is where tokenization comes in, which is the job of `Analyzer`.
`Analyzer` allows us to define a pipeline that converts a raw document field or query string a like to a list of tokens.
It does it in 3 customizable phases one after another:

1. Characters filtering and transformations
2. Tokenizer
3. Tokens filtering and transformations

Back to the example of _"Trump's official VISIT to Canada"_. To illustrate each of the above bullet points
( for sake of simplicity, the following explanation is not 100% correct):

1. For each character, we want to lowercase them and remove apostrophes. Now it becomes _trump official visit to canada_
2. Now, tokenizer breaks down the string into a list of strings. We might just break it down by word boundary which is how we normally think, so it becomes `[trump, official, visit, to, canada]`. It's also common practice to break down not just per word, but also do something called "ngram". It's a strange name but this example should illustrate the point of ngram=up to 3: `[t, r, u, m, p, tr, um, mp, tru, rum, ump, o, f, of, off...]`. The benefit is typo tolerance at the cost of extra storage. For foreign languages like Chinese, tokenization becomes harder because there's no clear whitespace separating things, so the practice is to use probability based tokenization algorithm like "jieba" or ML based partitioning
3. Now we have a list of tokens, we apply one final round of filtering and transformation. Common practices include
   - Removing stopwords like "to", "and", "a". They usually do not indicate relevance and only bloat up our storage
   - Stemming verbs to their root forms. So "running" becomes "run", "visited" becomes "visit"
   - Expanding common or custom defined synonyms. So one "iphone" might be expanded into `[iphone, cellphone, smartphone]`
   - Adding shingles. Previously we had "ngram" that groups at letter level. Shingle is the same idea but at the token level. So [trump, visit, canada] with a shingle <= 3 would become [trump, visit, canada, trump visit, visit canada, trump visit canada]. Previously, we said that letter level ngram help with typo and typeahead; shingle doesn't help in these, instead, shingles capture the relative position ordering of neighboring tokens

At the end of this process, `Analyzer` gives us a list of tokens and their original positions.

Lucene have a `StandardAnalyzer` that comes with lowercasing and word boundary splitting out of the box,
and we have the option to add and custom as needed too.

With our document `Text` fields tokenized (but not `Keyword` fields),
upon search time, we just need to tokenize the search query with the same `Analyzer` pipeline we used to tokenize documents,
and any document whose tokenized text fields overlap the tokenized query are considered relevant.

However, simply telling which documents are relevant is not enough.
We must also be able to tell which documents are more relevant than the other.

This is where BM25 or TF-IDF comes in.
TF-IDF stands for "term frequency - inverse document frequency".
The idea is, we can rank which documents are more relevant to a query by weighting each token based on:

1. How frequently that token appeared in that document
2. How rare that token is across all documents. So "visit" might appear in 1 million documents, "trump" might be in 100,000, so the term "trump" gets weighted more.

And BM25 is an improvement over TF-IDF by punishing long document length and normalizing too many same tokens in 1 doc.

Lucene uses BM25 by default.
And `Analyzer` is the first step to using BM25 for text retrieval: breaking down a query string or document field into tokens.

Soon, we will see the rest of the picture where Lucene organizes tokens in efficient data structures to facilitate
fast lookup and scoring.

### Directory

Great. We have some documents with text, keyword, and numeric fields.
And we have an analyzer configured to tokenize the text fields.
It's time to finally save these documents to disk.

We need to tell Lucene where on disk to store the documents.
`Directory.open(filepath)` lets us to that.
That's it. Super simple. And all the data structures, metadata, etc. will be saved there.

The significance is that, `Directory` can be not just an actual disk directory,
but it could also be a `MMAPDirectory` that is also on disk, but leverages the OS mmap mechanism to speedup IO reads.
It could also be a `ByteBuffersDirectory` that lives only in RAM,
which would be a lot faster than the on disk directories at the cost of using RAM.
And from what I remember, Amazon shopping does use the RAM directory for searching popular product items.

### IndexWriter

With directory and analyzer specified, we can finally throw documents to `IndexWriter`,
which will coordinate the process of saving documents to disk.

`IndexWriter` would first batch newly added documents before flushing them to disk.
We can configure max number of documents in the staging area before a flush would be triggered,
or by max RAM of staging documents.
We can also just explicitly call `.flush()`.
The reason for batching is about throughput and less IO overhead:
if we flush documents to disk one by one,
we would be doing too much IO, so we flush in batch instead.

Upon flush, `IndexWriter`:

1. Builds the important data structures like inverted index, BKDTree, HNSW graph. More on this in the next section "Codec"
2. Adds other metadata
3. Serializes data structures and metadata to bytes and writes them to a file to `Directory`

The flushed data on disk is logically called a "segment".

As we flush more and more batches, more segments are created on disk.
When we update a document, we have to add it to `IndexWriter` to replace it in full.
This means, the same document would be in an older segment and a newer segment.
Upon search time, we need to search every segment and use the latest one.
Thus, for search efficiency and reducing redundant storage,
`IndexWriter` has a background thread to periodically and conditionally merge segments together
by pooling together their documents, resolving the latest documents,
building a new segment around the merged documents, and deleting the old segments.

We see this recurring theme of flushing in batch and merging them later in Clickhouse, RocksDB, and so many other data storage solutions.
This is commonly used when point lookup is less important than bulk lookup and bulk ingestion.
PostgreSQL is update one by one than batching though, as point lookup and transactional update is critical to Postgres.

Now, in theory, `IndexWriter` can literally just write the documents to disk as-is without any data structures;
aka it would be dumping a segment as a big JSON file.
But that means upon search, we need to check every document and compute their relevancy score which is inefficient.

Thus, we need data structures to support efficient retrieval. This is where Codec comes in.

### Codec

For a batch of documents to be inserted, `IndexWriter` checks each field type against `Codec`
to resolve what data structures and metadata needs to be created, and use Codec to serialize them to disk.
Here are the most important data structures.

#### Inverted Index

The core of Lucene is BM25 retrieval that performs partial match on tokenized query and document fields.
How to design a data structure to avoid scanning every document?

What if we have a hashmap that records, for every token, which field / documents it appeared in. As an example:

```python
title_index = {
   'trump': [
      Doc(id=123, positions_appeared_in=[1, 40, 80], frequency=3),
      Doc(id=456, positions_appeared_in=[20, 562], frequency=2),
      ...
   ],
   'canada': [
      Doc(id=123, positions_appeared_in=[70], frequency=1),
      ...
   ],
   ...
}

description_index = ...

# An index like this for every TEXT field
```

And that is exactly what inverted index is.
It's a mapping from token to what documents it appears in.
To explain the name, forward index would store for every document, what tokens appear in that document.
Inverted index, as we see here, stores stuff inverted: for every token, which documents contains that token.

With inverted index, now, suppose the user's tokenized query is [trump, official, visit, canada] and we want to BM25 match it against the title,
then, instead of having to scan every document,
we can narrow it down to the documents that are in `title_index['trump']` or `title_index['official']` or `title_index['visit']` or `title_index['canada']`.

Of course, Lucene `Codec` would need to serialize the logical inverted index to disk,
plus some statistics for BM25 scoring,
plus skiplist to facilitate docID jumping.
Let's take a closer look.

When serialized to disk, the inverted index would be manifested into multiple physical files, each with a specific role:

1. `.tip` file: uses finite-state-transducer (FST) data structure that maps a term to a file offset in the `.tim` file
2. `.tim` file: given a term's file offset in `.tim` file, we get a few more file pointers to `.doc` `.pos` and `.pay`. We also get the global frequency of this term across all documents in the segment, as it is needed for BM25 scoring
3. `.doc` file: given a term's file offset in `.doc` file, we get the list of document IDs that term appear in, and the frequency this term appears in each document. Look at the earlier pseudocode, this corresponds to `id` and `frequency` for the docs
4. `.pos` file: given a term's file offset in `.pos` file, we get the list of positions that term appear in for each document. This is `positions_appeared_in` in the earlier pseudocode. Why is this in a separate file? Because it can be configured to be turned on and off. And even when positions are enabled, it's not used in the actual BM25 scoring, it's only used for queries like PHRASE query and for text highlighting.
5. `.pay` file: given a term's file offset in `.pay` file, we get a list of custom payloads. This is used a lot less and it's not in our pseudocode.

That's 2 pointer chasing in `.tip` first and then `.tim`, then we finally read the actual data of which documents the term appear in, at what frequency, at what positions, and other payloads.

Let's look at `.doc` even closer, because this is the most important data used for BM25.

The most important thing in `.doc` is what docIDs do each term appear in. There are two important mechanisms in-place:

1. First, all the docIDs are sorted
2. Then, every 128 docIDs are logically grouped into a "block"
3. For each block, the docIDs within it are compressed by their neighbor delta. So [982342, 982346, 982368...] will become start=982342 and deltas = [0, 4, 22]. Delta compression massively saves storage and IO as each docID uses 6 bits instead of like 24 bits, and it is a well-known technique within the search engine domain. This is due to docID distribution locality for a given term. Somewhat analogous to cache locality for CPU and caching in general.
4. Now, we also build a SkipList data structure on top of the docID blocks. This is because for a given term, we need to support the first docID after, say, docID=10000, and then skip until the next docID > 20000. As each the docIDs within each block had already been compressed, we must have a separate SkipList data structure on top of the blocks to facilitate this docID skipping mechanism.

With these techniques, we save storage and facilitate docID jumping for a given term. This comes in handy during search, which will be explained in that later section.

`Text` fields first go through `Analyzer` you configured to become tokens and be stored in the inverted index.
`Keyword` fields do not go through any tokenization and goes straight to the inverted index.

#### BKDTree

Inverted index stores the two types of string columns: text and keyword.
BKDTree stores numeric scalar or vector with dimension < 8 types of columns: int and float.

To illustrate with a Yelp restaurant example, these fields will each go to a BKDTree:

```python
restaurant = Document(
   avg_price=123.99,
   coordinate=(57.9, 23.1),       # longitude, latitude
   price_range=(20, 100),
)
```

Note that:

1. We could store longitude and latitude as two separate fields, but BKDTree allows more efficient filtering mechanism if we store them together
2. The max size of the vector is 8. This is because BKDTree performs well when the vector dimension is small and becomes horrible for large dimension vectors.
3. For large dimension vectors like embeddings, Lucene offers the HNSW data structure, which will explained in a future section

But what exactly is a BKDTree tree? Let's first understand binary search tree, then KDTree, and finally BKDTree.

Binary search tree is a tree data structure that has the following properties:

1. Every node has a value
2. The left subtree's values must all be smaller than the parent node's value
3. The right subtree's values must all be greater or equal to the parent node's value
4. Thus, to build a balanced binary search tree, we pick the median as the root, and recursively build and left and right nodes from the values left and right of median
5. Upon search time, we can traverse the node left and right to find the relevant range of values we are looking for

Here's the Python pseudocode:

```python
class BinarySearchTree:
    class Node:
        value: int | float
        left_child: Node | None
        right_child: Node | None

    def __init__(self, values: list[int | float]):
        def build(vals):
            if len(vals) == 0:
                return None
            mid = len(vals) // 2
            return Node(value=vals[mid], left_child=build(vals[:mid]), right_child=build(vals[mid + 1:]))
        values.sort()
        self.root = build(values)

    def find_between(self, small: int | float, big: int | float):
        def traverse(node):
            if small <= node.val <= big:
               yield node.val
            if small < node.val:
               yield from traverse(node.left)
            if node.val <= big:
               yield from traverse(node.right)
        yield from traverse(self.root)

# Usage example
tree = BinarySearchTree([1, 345, 35434, 24234234...])
print(len(tree.find_between(345, 345)) > 0)     # Does 345 exist
print(list(tree.find_between(100, 10000)))      # Which values are between 100, 10000
```

Geometrically, we can interpret the behavior of binary search tree like this:

1. All the sorted values correspond to points on a line
2. The root of partitions that line into left and right line segments
3. And each recursive root partitions recursively into small line segments
4. When we want to find all points between a range, to traverse the root cursively to touch on all line segments that intersect with the query (left, right) to some extent until we spit out the actual points

Binary search tree lets us efficiently store and query on range of scalar int and float values.
In the yelp restaurant example earlier, binary search tree could store the `avg_price` perfectly.
But it only supports 1D scalar value, so it can't handle `coordinate`.

KDTree stands for K-dimensional tree. And guess what it does?
It generalizes binary search tree to any higher dimension of values.
So KDTree can handle 2D values like `coordinate` as well as `avg_price` alike.

Binary search tree partitions on a line segment in half.
KDTree partitions a KDSpace in half along a coordinate and a split value.
It sounds abstract, but lemme show you the pseudocode, and it would make sense easily:

```python
import random

class KDTree:
    class Node:
        split_dimension: int
        split_value: float | int
        left_child: Node | None
        right_child: Node | None
        points: list[list[int | float]] | None

    def __init__(self, values: list[list[int | float]], per_node_threshold=16):        # A list of vectors instead of a list of scalars
       dimension = len(values[0])   # For the coordinate example, it would be 2
       def build(vals):
            if len(vals) == 0:
                return None
            if len(vals) < per_node_threshold:
               return Node(points=vals)
            # Pick a random split dimension, as randomness guarantee consistent performance
            split_dimension = random.randint(0, dimension)
            values_in_dimension = [v[split_dimension] for v in vals]
            values_in_dimension.sort()
            median_value_in_dimension = values_in_dimension[len(values_in_dimension) // 2]
            smaller_points_in_dimension = [v for v in vals if v[split_dimension] < median_value_in_dimension]
            greater_points_in_dimension = [v for v in vals if v[split_dimension] >= median_value_in_dimension]
            return Node(
               split_dimension=split_dimension,
               split_value=median_value_in_dimension,
               left_child=build(smaller_points_in_dimension),
               right_child=build(greater_points_in_dimension)
            )
        self.root = build(values)

    def find_between(self, lower_left_point: list[int | float], upper_right_point: list[int | float]):
       def traverse(node):
          if node.points:       # It's a leaf
             for p in node.points:
                if lower_left_point <= p <= upper_right_point:      # This is pseudocode
                    yield p
          else:
             left = lower_left_point[node.split_dimension]
             right = upper_right_point[node.split_dimension]
             if left < node.split_value:
                yield from traverse(node.left_child)
             if node.split_value < right:
                yield from traverse(node.right_child)
       yield from traverse(self.root)

# Usage example on coordinate
points = [
   (234, 3453),
   (232.234, -1324.234)
   ...
]
kdtree = KDTree(points)
print(kdtree.find_between((-200, 2342), (1212, 23342)))     # Which points are between these bounding points?
```

Finally, BKDTree means block optimized KDTree,
which is a variant of KDTree that optimizes KDTree for disk storage.
As we know, disk storage requires fetching 4KB or block of data at once,
and BKDTree is optimized for block IO.

TODO

We can see that, for fields like `avg_price` that is 1d,
BKDTree is in essence a binary search tree serialized to disk
For 2D fields like `coordinate`, then it behaves like KDTree.

#### DocValues

#### Stored Values

#### HNSW

### Let's search!

### Putting it all together

This is the official starter code from Lucene's docs that illustrate all the concepts we talked about.
Note that, "codec" is not directly shown here, as by default, `Text` field would trigger the set of inverted index codec,
int field would use BKDTree codec, KNN would use HNSW, etc. so codec happens automatically.

```java
Analyzer analyzer = new StandardAnalyzer(); // to tokenize query and doc fields alike into tokens

Path indexPath = Files.createTempDirectory("tempIndex"); // create tmp folder on disk for demo

try (Directory directory = FSDirectory.open(indexPath)) {   // open the disk directory
   IndexWriterConfig config = new IndexWriterConfig(analyzer);    // use our analyzer
   try (IndexWriter iwriter = new IndexWriter(directory, config)) {
      Document doc = new Document();   // creates docs
      String text = "This is the text to be indexed.";
      doc.add(new Field("fieldname", text, TextField.TYPE_STORED));
      iwriter.addDocument(doc);
      // add it do writer, which will trigger inverted index codec, etc.
      // flush it to disk eventually into segments
      // fyi there's also a background thread merging the segments together
   }

   // Now search the index:
   try (DirectoryReader ireader = DirectoryReader.open(directory)) {
      IndexSearcher isearcher = new IndexSearcher(ireader);
      // Parse a simple query that searches for "text":
      QueryParser parser = new QueryParser("fieldname", analyzer);
      Query query = parser.parse("text");
      // So this uses inverted index + BM25 scoring
      ScoreDoc[] hits = isearcher.search(query, 10).scoreDocs;
      assertEquals(1, hits.length);
      // Iterate through the results:
      StoredFields storedFields = isearcher.storedFields();
      for (int i = 0; i < hits.length; i++) {
         Document hitDoc = storedFields.document(hits[i].doc);
         assertEquals("This is the text to be indexed.", hitDoc.get("fieldname"));
      }
   }
} finally {
IOUtils.rm(indexPath);
}
```
