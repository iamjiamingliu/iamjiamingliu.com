---
title: The Evolution of UCSBPlat.com
description: Same mission, but the implementation keeps on getting better
tags: []
category: Tech
created_at: 2026-05-10 15:45:00
updated_at: 2026-05-10 15:45:00
---

## We Love UCSBPlat.com

If you are a student at UCSB,
chances are,
you are already a happy user of UCSBPlat.com yourself,
or you've had at least heard of it,
and likely that many of your friends are happy users of UCSBPlat.com too.

You open UCSBPlat.com, gets greeted with a beautiful, clean UI like this:

![](/static/img/projects/ucsbplat.webp)

Then you go on your business using it,
whether it's looking up the grading trends and enrollment trends of a class you are thinking of taking
or trying to fill your schedule with whichever GE class that satisfy the most areas.

Today, UCSBPlat.com has the pleasure of serving 9,000+ monthly active students,
helping Gauchos find classes with better reviews, grading trends, enrollment trends, and more.
Actually, the Google Analytics page of UCSBPlat.com indicate that there's 17,000 unique visitors of UCSBPlat.com
in a given month. However, for mysterious reasons, around 7,000 of them are from mainland China, Singapore,
and various other countries...
I don't know why someone on the other side of the ocean of UCSB would bother to look at UCSB courses,
so I suspect these are merely automated scraping bots and ignoed them from the 9,000+ monthly active users calculation.

![](/static/img/projects/ucsbplat_google_analytics.png)

> This is a commit-history-based skeleton draft.
> I still need to add the actual story, emotions, mistakes, motivations, launch anecdotes, and hindsight.

## Foreword

UCSBPlat did not emerge all at once as some polished "startup product."
It grew in layers.
First it was data scraping.
Then it became a database.
Then a UI.
Then a search engine.
Then a scheduler.
Then a recommender.
Then a machine learning playground.
Then a real production system with deployment, analytics, login, bot handling, and all the other fun stuff that quietly accumulates behind a website that students casually use.

This article is meant to document that evolution.
Not just what UCSBPlat does now,
but how it got there.

TODO:

- Why I started UCSBPlat in the first place
- Why I thought UCSB GOLD was not enough
- Why I named it "Platinum"
- What the first public reactions were like
- What building this taught me technically and personally

## The one-line timeline

- November 2023: initial scraping, professor data, grades data, early database, first course pages
- December 2023: large database redesign, blueprints, richer class/professor pages, GE pages, trends, caching, search and autocomplete groundwork
- Late December 2023 to January 2024: schedule builder, dark mode, major pages, recent views, quarter filters, mobile polish
- Late January 2024: transcript parsing, major requirements, and the first recommender / "what classes should I take" direction
- February 2024: analytics and PDF export after launch
- Mid to late 2024: performance work, passtimes, professor images, UI polish, documentation, indexes, and a more serious recommender push
- December 2024: major search overhaul, Elasticsearch-style search stack, GE search, autocomplete, map view
- January to February 2026: repo reorganization, grades prediction / A-rate prediction, feature engineering, training and inference
- March 2026: Dagster scraping pipeline
- April 2026: Google OAuth, profile page, tracking, privacy policy, bot handling, live user counts, and stronger production instrumentation

## Phase 0: Before there was a website

The commit history starts on November 1, 2023,
but the real beginning obviously predates the first commit.

Before the code,
there was the frustration.
The problem statement.
The "why does this workflow suck so much?" moment.

TODO:

- What exact pain points existed with GOLD, RMP, Daily Nexus / Labyrinth, and course discovery in general
- What the original MVP in my head was
- Whether I imagined a simple aggregator or something much bigger
- Whether I thought this would become a long-term project or just a quick build

## Phase 1: Scraping-first chaos

The earliest commits from November 1 to November 2, 2023 read like a raw build sprint:

- `init`
- `started selenium scrape`
- `scraper ready`
- `all professors data ready`
- `started DB`
- `data loaded succesfully`

This phase was very clearly about one thing:
get the raw data.

Before there could be a platform,
there first had to be a pipeline for collecting professor pages, rating data, grades data, and course-related information.
The earliest system looks much closer to "scraping project" than "product."

What was already present surprisingly early:

- professor data
- Daily Nexus grades data
- JSON result saving
- multithreading
- a first database load

TODO:

- What was the first source I scraped
- Which data source was the most annoying
- What broke the most in this phase
- Whether I had any idea what schema I wanted at first
- What the first "it actually works" moment felt like

## Phase 2: From raw data to actual pages

By November 2 to November 7, 2023,
the repo moved beyond scraping into actual product surface area:

- first course pages
- grades UI and grade charts
- professor UI
- professor-course linking
- search bar UI
- major filter UI
- enrollment info
- professors-per-major views

Important commits in spirit:

- `started each course page`
- `grade charts ready`
- `search is ready`
- `each page ready`
- `professor rating browse ready`
- `added enrollment info for each section and course`

This was the first time UCSBPlat started to resemble something a student could actually browse.

The key conceptual jump here was:
the problem was no longer just "collect data,"
but "present it in a way that is actually useful."

TODO:

- What the first usable version looked like
- What the first pages were
- Which feature felt most magical at the time
- Whether I launched anything to real users at this point or still kept it private

## Phase 3: The first big schema rethink

The commit history in early December 2023 shows a major data-modeling phase.

Some representative commits:

- `succesfully connected to postgres`
- `prerequisite is now its own table`
- `renamed course_group to course, course to class_`
- `moved grade under course`
- `moved GE under courses`
- `use enrollment code as class pk, rmp id as instructor pk`

This part deserves a real section in the final essay because it reflects an important truth of serious software projects:
the first schema is usually not the real schema.

As the project grew,
the domain model had to become much more precise:

- what exactly is a course?
- what exactly is a class?
- what exactly is a section?
- what belongs historically to a course versus a particular quarterly offering?
- how should prerequisites, grades, GE areas, reviews, and enrollment relate?

This seems to be the phase where UCSBPlat stopped being a hacky aggregator and started becoming a genuine domain model of UCSB curriculum data.

TODO:

- Explain the `course` vs `class` vs `section` distinction
- Explain the modeling mistakes I made initially
- Explain which redesign decision mattered the most later
- Mention whether this redesign was painful or satisfying

## Phase 4: Architecture starts to matter

Mid to late December 2023 contains another major shift:
the codebase started organizing itself like a real web application.

Representative commits:

- `added blueprints`
- `migrated code to blueprints`
- `reorganized templates`
- `added cache`
- `cache is now correct`
- `reorganized flask files`

At some point,
the bottleneck of a project is no longer "can I build the next feature?"
It becomes:
"can I keep building features without the repo collapsing?"

That is what this phase looks like.
UCSBPlat moved toward:

- blueprint-based Flask organization
- reusable templates and macros
- caching
- stronger loader logic
- clearer separation between scraping, web, and data concerns

TODO:

- What the repo structure looked like before this cleanup
- What felt the most unmaintainable
- Whether there was a specific feature that forced this refactor

## Phase 5: Richer academic product surface

Around December 21 to December 30, 2023,
the product surface widened a lot.

Features appearing in this era include:

- grading trends pages
- enrollment trends pages
- GE blueprint and GE displays
- richer instructor pages
- prerequisites and allowed majors
- "you might also like"
- quarter dropdowns
- recent views
- search and autocomplete improvements

This phase matters because UCSBPlat was no longer only answering:
"What is this class?"

It was starting to answer broader questions like:

- How has this class graded historically?
- How fast does it fill up?
- What requirements does it satisfy?
- What else is similar?
- Who teaches in this area?

That is the moment where a data site starts becoming a decision-making tool.

TODO:

- Which of these features students used the most
- Which features I personally was most proud of
- Which features nobody cared about as much as I expected

## Phase 6: Scheduler and planning

Late December 2023 into January 2024 introduced the scheduler.

The commit messages are very explicit:

- `started scheduler module`
- `schedule is now a blueprint`
- `implemented has conflict`
- `calendar is now a macro`
- `oop scheduler`
- `generate sections button`

This was an important product expansion.
UCSBPlat was no longer just for passive browsing.
It was becoming interactive planning software.

The site now had to reason about:

- time conflicts
- sections
- schedule storage
- calendar UI
- adding / removing classes
- generating viable combinations

TODO:

- Why I decided to add a scheduler
- Whether students had requested it
- How hard schedule conflict logic was
- Whether the scheduler changed traffic / adoption meaningfully

## Phase 7: Launch polish and "students are actually using this"

January to February 2024 reads like the phase when the project had to confront real users.

Representative signals:

- mobile navbar fixes
- caching improvements
- SEO setup
- Google Analytics
- disclaimer / messaging improvements
- PDF export
- all-majors loading refreshes
- graduate-course support

This was not just feature work.
It was operational polish.
The kind of work that appears once something is exposed to real traffic and real expectations.

TODO:

- Insert the actual launch story
- Mention the Reddit post and reaction
- Mention first-day / first-week traffic
- Mention what broke after real people touched the site

## Phase 8: Recommender era, take 1

Late January 2024 already shows the first major recommender push:

- transcript parser
- major requirements loading
- submitting courses taken
- GE recommendation
- courses recommender
- recommender page

Representative commits:

- `started recommender page`
- `basic recommender seems ready`
- `added ges recommendation`
- `export to PDF button`

This is one of the most ambitious conceptual jumps in the whole project.
An aggregator tells you what exists.
A recommender tries to tell you what you should do next.

That is a much harder product question.

TODO:

- Why I thought recommendation was the natural next step
- How naive the first recommender was
- Whether students found it useful or just interesting
- What I learned from trying to go from search to recommendation

## Phase 9: The long middle of polish, documentation, and production reality

A lot of 2024 looks like the mature middle life of a real student product:

- passtime support
- professor profile images
- section enrollment trend pages
- UI polish across mobile and desktop
- database indexes and performance work
- README and production docs
- troubleshooting notes
- local and production run instructions

Some notable commits:

- `added section enrollment trend page`
- `added instruction to run locally`
- `run production instruction ready`
- `added compound indexes`
- `grading trend migrate to integer PK`

This phase probably deserves an essay point of its own:
once a project becomes real,
maintenance and polish start to consume huge amounts of time.

Not because the project has "stopped innovating,"
but because real software accumulates edges:

- performance
- deployment
- docs
- onboarding
- schema migrations
- data freshness
- operations

TODO:

- What it felt like to maintain UCSBPlat once it had real users
- How much time went to glamorous new features vs invisible maintenance
- Whether collaborators entered around this era

## Phase 10: Recommender era, take 2

In fall 2024,
the recommender came back in a much more serious way.

The October 2024 commits suggest a much richer recommendation and progress-check workflow:

- upload-based recommender UX
- major progress checks
- GE progress checks
- prerequisite tree / downstream display
- missing GE display
- "what classes should I take" button

This version seems less like a toy and more like a full planning workflow.

Representative commits:

- `made recommender form into upload`
- `added ges progress check`
- `started class recommendation`
- `course prerequisite`
- `displays missing GEs for ge progress`

TODO:

- Compare this recommender to the January 2024 version
- Explain what was rethought conceptually
- Explain if transcript upload changed adoption a lot

## Phase 11: Search grows up

December 2024 looks like another major inflection point:
search became first-class infrastructure.

Representative commits:

- `install es-dsl`
- `sync professor and majors success`
- `basic autocomplete ready`
- `added autocorrect and modularized search suggestor`
- `started new search endpoint`
- `started ges search`
- `started GE search`
- `department is searchable`
- `added map view to lecture`

This phase seems to mark the transition from earlier search / autocomplete
into a more serious search architecture with:

- indexed search data
- autocomplete tuning
- typo correction
- course / professor / major / department search
- GE search
- map view support
- performance considerations like debounce and caching

This is a good phase to emphasize in the final essay because it reflects a backend lesson:
search is not one feature.
Search is its own subsystem.

TODO:

- Why the old search was not enough
- Why I moved toward this search stack
- Which ranking / autocorrect issues were surprisingly hard
- Whether search quality measurably changed user experience

## Phase 12: Machine learning enters the chat

January 2026 is one of the most technically ambitious phases in the entire repo.

The commit history shows:

- repo reorganization into `infra` and `modules`
- a grades prediction module
- feature engineering
- retrieval
- training dataset construction
- LightGBM training
- inference
- A-rate prediction UI

Representative commits:

- `starting grades prediction module`
- `defines actual schema`
- `online retrieval works!`
- `implemented training dataset construction`
- `trains models`
- `adds A rate in many places`
- `displays predicted grades UI`

This is a full step beyond web product engineering.
At this point UCSBPlat became a place where I could explore applied ML on top of my own domain data.

TODO:

- Why I decided to predict grades
- Whether this was more for users or for my own technical curiosity
- What the feature engineering looked like
- Whether the predictions were actually useful or mostly "cool"
- What building this taught me about ML systems in practice

## Phase 13: Scraping becomes a pipeline

In March 2026,
the scraping side seems to have been upgraded with Dagster:

- `dagster is working`
- `creates definitions draft 1`
- `updates readme`
- `Merge branch 'dagster-scraping'`
- `removes old start scrape`

This is important because it marks another maturity step:
when even your internal data refresh workflow becomes a product for yourself.

Instead of "run this script and pray,"
the scraping system appears to have moved toward clearer orchestration and lineage.

TODO:

- What was wrong with the old `python3 start_scrape.py` workflow
- Why Dagster was worth the overhead
- Whether this improved reliability or just observability

## Phase 14: Identity, tracking, and production instrumentation

April 2026 is packed.
This may be the biggest "productionization" burst in the repo's history.

Major themes:

- Google OAuth
- profile page
- anonymous user IDs
- tracking tables
- page view tracking
- enriched analytics
- privacy policy
- bot detection
- Cloudflare adjustments
- robots.txt
- live user tracking and live counters

Representative commits:

- `starting google oauth!`
- `created the profile page`
- `tracks every web page request!`
- `adds privacy policy`
- `starting bots detection module`
- `tracks live users`
- `shows per class live count`
- `moves live user count to the footer`

This phase is interesting because it shows UCSBPlat evolving from a feature site into an instrumented platform.
Now the site was not just serving students;
it was observing usage patterns, handling identity, and defending itself against junk traffic.

TODO:

- Why I decided to add login
- Whether users actually wanted profiles or I wanted the identity layer for future features
- What I learned from building tracking into my own product
- Whether live counters were actually useful or mostly fun

## Phase 15: Constant polishing never ends

Even the most recent commits are still very "alive":

- GE searchbar improvements
- mobile click-area improvements
- retention duration changes
- live count UI changes
- bot filtering refinements
- logic tweaks like `change to AND clause`

This is the eternal truth of software:
there is no final "done."
There is only:

- it works
- it works better
- it works better and cleaner
- wait, users are doing something weird
- okay now it actually works better

TODO:

- End with a reflection on what "finished" means for a project like this
- Mention whether UCSBPlat still feels exciting, burdensome, both, or something else entirely

## Technical evolution summary

At a high level, UCSBPlat seems to have evolved through these technical layers:

1. Data acquisition
2. Database and domain modeling
3. Flask app structure and templates
4. Caching and performance
5. Search and retrieval
6. Interactive planning features
7. Recommendation systems
8. Machine learning predictions
9. Deployment and docs
10. Authentication, analytics, and anti-bot production concerns

TODO:

- Add a paragraph on each layer with what I learned

## Product evolution summary

At a product level, UCSBPlat seems to have evolved like this:

1. Aggregator of scattered academic data
2. Cleaner browsing interface for classes and professors
3. Historical analytics tool for grades and enrollment
4. Planning tool through schedules and quarter-aware views
5. Decision-support tool through GEs and recommendations
6. Personalized platform through login, tracking, and profiles

TODO:

- Add what users likely came for originally
- Add what they stayed for later
- Add what features were "core" versus "nice to have"

## What I still need to add later

- The launch story
- The Reddit post and first traffic wave
- The naming story behind "Platinum"
- Key collaborators and what they contributed
- Biggest production outage / bug story
- Hardest scraper or data integration
- Most surprisingly useful feature
- Feature that took forever but users barely noticed
- What I would redesign if I rebuilt UCSBPlat from scratch
- What UCSBPlat taught me about backend, product, infra, and users

## Closing placeholder

UCSBPlat started as a way to make course discovery less annoying.
Somewhere along the way,
it turned into one of the biggest and most educational engineering projects I have ever built.

TODO:

- Replace this with an actual ending once I add the real voice and story
