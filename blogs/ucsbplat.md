---
title: The Story of UCSBPlat.com
description: Same mission, but the implementation keeps on getting better
tags: []
category: Tech
created_at: 2026-05-10 15:45:00
updated_at: 2026-05-10 15:45:00
---

## We Love UCSBPlat.com

If you are a student at UCSB,
chances are,
you have used UCSBPlat.com yourself,
or at least heard of it from a friend.

You open UCSBPlat.com and get greeted with a clean UI like this:

![](/static/img/projects/ucsbplat.webp)

Then you go on your way,
whether that means checking grading trends and enrollment trends for a class you are thinking of taking,
or hunting for a GE that satisfies the most areas with the least pain.

Today, UCSBPlat.com has the pleasure of serving 9,000+ monthly active students,
helping Gauchos find classes with better reviews, grading trends, enrollment trends, and more.
Actually, the Google Analytics page of UCSBPlat.com indicates that there are around 17,000 unique visitors
in a given month. However, for mysterious reasons, around 7,000 of them are from mainland China, Singapore,
and various other countries...
I don't know why someone on the other side of the ocean would care that much about UCSB courses,
so I suspect those are just scraping bots and ignore them from the 9,000+ monthly active users calculation.

One more thing:
the 9,000+ is a low-month number,
when there isn't an active registration period going on.
During the months when everyone is scrambling to figure out classes,
I think the number is more like 10K to 15K.

![](/static/img/projects/ucsbplat_google_analytics.png)


## The Other Side of the Story

I created UCSBPlat.com as my freshman year winter break hobby project and have maintained it ever since.
In this blog, I want to show you the other side of the story:
how Plat was built, how it evolved, and what it ended up meaning to me.

While you read, I want to draw your attention to these themes I experienced:

1. It's okay to feel like giving up, as long as you come back to it
2. It's okay and natural to feel burned out. The good news is that passion will bounce back
3. What a playground!

What do I mean by these themes?
Well, keep on reading.
Here we go.

## The Birth of Plat: the mission and name

When I started my undergrad at UCSB back in fall 2023,
I was thoroughly disgusted by the ugly UI and difficulty of use of GOLD (Gaucho Online Data),
the official curriculum registration platform of UCSB.

I love building websites. Especially websites with beautiful UI.
I've been building websites since high school.
So I thought,
_why not build a GOLD wrapper website with the same data, but just prettier UI?_

But then I realized, no one would want to use a website like that.
Sure, it looks prettier than GOLD, but so what?
Do I want to open another tab just to see the same information as GOLD?
Being a prettier wrapper did not seem like a compelling enough reason for anyone to switch.
Thus, that was the end of UCSBPlat before it was even called UCSBPlat.

Thankfully, as I was wandering around the UCSB lagoon one day,
I realized what might actually make the product worth using:
_what if, in addition to the catalog data,
we aggregated Rate My Professors and Daily Nexus grading trends too,
all in one place, with a really gorgeous UI?_
After all, I kept seeing friends with GOLD, RMP, and Daily Nexus all open in separate tabs whenever they were signing up for classes.
If a tiny bit less friction could make course planning materially easier,
then one site for all of it might actually be useful.

The same data as GOLD. With a better UI. And aggregated with additional information too.
It's better than Gold. It's gotta be Platinum.
Thus, the name and vision for UCSB Platinum, UCSBPlat.com, was born.

## Giving up before a line of code

A lesson I learned from my previous website projects was,
before any line of code is written, start with a plan first.
Sure, software engineering is iterative and evolving,
but you gotta start with a plan first.
Without a plan, the code would go nowhere,
and you would just be wasting time juggling coding with half-baked planning in your head.

So I went out to sketch out the plan:
the user story, the UI, the domain design, the scraping workflow, architecture, and the database table design.
And I realized, oh boy, what the hell of a mess UCSBPlat was gonna be.

Sure, today when you look at UCSBPlat,
everything is clean:
the UI is intuitive, you search for a class, click it, and see the aggregated data.
But nothing is clean in the beginning.
In the beginning everything was mayhem.
Only through so much brain power drainage and iterations would mayhem slowly morph into being clean.

I realized to make UCSBPlat happen, I had to wrestle with a monster with this many arms in front of me:

1. 13 database tables needed to store all the courses, professors, reviews, sections, enrollment trends, grading trends, etc.
2. An enormous Python scraping workflow needed to pull data from the UCSB catalog, Rate My Professors, and Daily Nexus
3. Extra complicated joining logic needed to correctly resolve "Bob Anderson" on Rate My Professors to "R W Anderson" in the UCSB catalog
4. God knows how many SQL lines were needed to JOIN all the related data together

And many more...

I was living in the Anacapa dorm in my freshman year.
For a whole week straight,
I would spend afternoons and late nights sketching out UI drafts, database design, and scraping workflow outlines
with pencil and letter paper I grabbed from the downstairs printer tray.
I don't know Figma or anything fancy, just pencil and paper.
I still use pencil and paper.
The more I sketched, the more I realized what kind of monster was sitting in front of me.

Maybe the best way to deal with a bottomless pit is to just not go into it.
So, on the seventh day, I decided I'm out.
UCSBPlat was dead again before a single line of code was written.
My mental mayhem had dragged me down.

While I was planning, I saw that the idea of UCSBPlat was not _that_ original at all.
There were already many course catalog wrappers and schedulers at UCSB:
gauchocourses.com, GoGaucho iOS app, and more.
_If all the giants before me already exist, why am I qualified enough to wrestle them?_
In hindsight, the reason is clear:
the emphasis of many existing tools was schedule planning,
while the emphasis of UCSBPlat was aggregation:
professor reviews, grading trends, enrollment trends, and more, all in one place.
Plus, UCSBPlat had a much cleaner and more intuitive UI.
But the freshman year version of me couldn't tell what my edge was.
It's important to know your edge.

Really, if you think about many of the great internet software out there,
they weren't the first. They are just better.
Before Facebook there was MySpace. Before Google there was Yahoo and many search engines.
Before Amazon there were many ecommerce sites.
Ideas may be important, but execution is the killer.
As my other blog article said, [idea is cheap, but execution is gold](/blogs/problem-solution-execution.md).
UCSBPlat was not the first.
It just had a better wedge.

## But I have to shoot this shot

You know, I'm a busy person.
Not in the sense that I get overwhelmed by too much work,
but rather in the sense that I just can't afford being not busy.
I can't spend a long period of time not working on something big.
If I'm not working on something big, I feel sad.
I have to keep myself busy.

I had just started freshman year back then.
All those accomplishments I had in high school got reset to zero.
I'm now a nobody freshman rookie in a big university without any titles or anything to hold on to.
I tried to join the UCSB ICPC competition, but I didn't make the cut.
I tried to join CoderSB and got rejected
<small>(I think I got rejected? But I definitely tried to join UCSB ACM a year later, the direct successor of CoderSB, and got rejected. Ironically I later became the President of UCSB ACM. You never know what could happen in life).</small>
I tried to replicate my TV newscast experience from high school here at UCSB,
and that didn't work either.
I applied for UCSB TV, never heard back, until I emailed them and they replied "huh? we didn't see your application".
I joined The Bottom Line News, which was also lame.
Really, it just felt like in the first 2 months of college,
I was trying this and that and getting nowhere in everything I tried.

Maybe UCSBPlat would become one more thing I tried and get nowhere.
And become a joke.
You can't afford being a joke when everything isn't working.

But I just can't do nothing.
I'm a busy person.
I have to be working on something.
Out of all the things I thought of, Plat was the one last thing I could try.
Sure, it could fail, but I assured myself that,
at least I could learn new technologies from this experience,
like ORMs and Scrapy and more,
and it could go on my resume no matter what.

So, let's just go for it and see where it goes.
You really can't tell.
There are many software projects I built before Plat, and after Plat,
that were meticulously planned and well executed.
Some of them became lasting and loved by many,
but many also faded into anonymity.
But you never know.
You just have to try it.
Shoot the shot.

## The Winter Break

Thus the grind began.
If I remember correctly,
during the weeks leading up to freshman year fall quarter finals,
I was sketching Plat on pencil and paper nonstop.
I just had to swallow the fact that I was about to fight a monster.
I might fail, but I had to shoot this shot,
and no matter what, I would grow from it.

I wrote a few scripts and concluded that it was technically feasible to crawl and index the UCSB catalog, Rate My Professors, and Daily Nexus grades.
I didn't crawl GOLD, because as a rule of thumb in web crawling, you don't crawl logged-in content.
Instead, I crawled the [Student Affairs Public Catalog](https://my.sa.ucsb.edu/public/curriculum/coursesearch.aspx)
for the course information, since it is public and does not require login.
For Rate My Professors, I only crawled the top 6 reviews per professor as an overview,
and "see more" would link the user directly to Rate My Professors.
For grading trends from Daily Nexus,
they already publish the data as a CSV file on GitHub, so I just used that.
You reciprocate favors:
later on, Daily Nexus asked to use some of Plat's data too, which I gladly gave.

In a way, it's like building a mini-Google, but limited to 3 sites about UCSB courses.

Winter break came, I had nothing else to do, so I went all in and built the actual UCSBPlat.com.
There wasn't Claude Code nor Codex,
and ChatGPT was pretty shitty back then,
so I just coded the thing out manually.
I used Python Flask and HTML and Bootstrap 5 for the frontend,
Selenium + Scrapy + Requests for scraping,
and at first just PostgreSQL for data storage.
I would wake up, quickly eat breakfast, and just start coding.
I was so freaking locked in.
My eyes would get blurry and dry, my stamina would get exhausted,
but I just kept going because I believed I was building something big.
I was happy that I found my calling.

God knows how many challenges I ran into while building Plat...
Professor name abbreviation mismatch, SQL JOIN issues,
and just mysterious bugs everywhere.
And whenever an issue came up,
I would Google search my way through StackOverflow, YouTube, and random blogs to find a solution.
If none existed already, I just had to try many things out myself.
It felt like 过五关斩六将,
the classic Chinese lore of fighting through castle after castle before reaching the destination.
Well, isn't that how every meaningful journey goes?
No journey is a journey without challenges.
You just gotta push through them all.

I'm glad all the previous projects I built in high school prepared me for this moment.
When everyone was senioritis-ing the last semester of high school away,
I leveled up my SQL skills and learned SQLAlchemy the ORM,
and they came in clutch for UCSBPlat.
SQL is already complicated,
and an ORM adds another layer of abstraction on top,
so I really struggled to grapple with SQLAlchemy at first.
But thankfully I figured it out eventually,
and it saved me so much effort later on.

I proudly showed off my progress to my dad, an iOS veteran developer.
But he didn't really understand what I was doing,
nor the possible significance of Plat.
I also told many friends about Plat.
Some courteously said "wow this is great" while most just said "ok cool".
I mean, I guess when you are trying to build something new,
people won't get it at first.
They shouldn't get it.
If something is obvious to everyone,
it usually wouldn't still be waiting around for you to build.
You may be horribly wrong.
But if you are right, it pays.

## The Reddit Post, with typo

Time to launch.

But where to launch?

Well I got lazy,
so I just dropped one post on Reddit and called it a day.
I thought, _if this reaches enough users, I think it's sufficient and I can just not do other promo._
So, on January 31st 2024,
I posted [this Reddit post](https://www.reddit.com/r/UCSantaBarbara/comments/1aegcjn/introducing_ucsb_platinum_usbplatcom_its_gold_but/)
in r/UCSantaBarbara and just prayed it would go well.
And luckily, it did.
The post gained 29,000 views within 48 hours of its posting,
although I was afraid to measure how many of them actually clicked through to UCSBPlat from the post.
I made a typo in the post title:
"Introducing UCSB Platinum **usbplat**.com - It's GOLD, but Better."
Oops.
USBPlat instead of UCSBPlat.

My friend strongly encouraged me to set up Google Analytics for Plat,
to which I refused, because I worried the number of visitors might look bad.
Then I was like, fuck nah, let's just add it and see the truth,
and thankfully, the numbers were fine.
According to Google Analytics, UCSBPlat organically grew through word of mouth after that initial Reddit post,
from 0 to 9,000+ users.

If you look at the OG Reddit post,
there was a feature that no longer exists:
course recommendation.
I thought course recommendation would be a hit,
only to realize that almost no one used it.
I later tried some more complicated DAG logic and retrieval pipeline ideas to improve the recommendation,
but that still didn't strike the users.
So I just took the feature down.
Nowadays people occasionally say "why don't you add a recommendation feature",
and I reply "well I did, and no one used it."
I suspect the failure is because the user would need to upload their transcript PDF,
which is quite a hassle to do and would raise privacy eyebrows.
If Plat had a Google login that already knew your courses automatically,
so that recommendations could show up without asking you to upload anything,
I think the feature could be very popular instead of fading into anonymity.
After all, any extra friction in the user experience kills usage.
Imagine if Amazon recommendations required you to upload all of your shopping receipts from the past.
I doubt anyone would use that.
But if Amazon just tracks all the stuff you've browsed and purchased so far automatically
and shows recommendations without you having to ask first,
then people will use it.
Friction kills.

The person who created gauchocourses.com saw the Reddit post and reached out to me to build a feature on Plat.
I thought he was trying to scam me or hack into UCSBPlat.
After all, GauchoCourses.com was a competitor.
But after we got on a Discord call and introduced ourselves, I saw he meant no harm.
He's just another Gaucho technologist who likes building things, so I let him build the feature.
We've become good friends since then.
He's an officer on the SBHacks organizing team,
so I stayed on the SBHacks organizing team for the next 2 years because of him.

Two years later, the alumni who made the GoGaucho iOS app years before me reached out to me on Instagram.
I was shocked that he even found me.
He said the current maintainers of GoGaucho were talking about Plat,
which is how he heard about it.
He was an international Chinese student just like me,
so we talked in Mandarin and had a good time.

I also reached out to BerkeleyTime.com, UC Berkeley's equivalent.
I got on a call with their project manager,
talked about Plat,
discussed the shared problems both student products face,
and had a good time.
What made me laugh a bit was that BerkeleyTime had a whole team maintaining the site,
while Plat was mostly just me.
To be precise, my friends added a few lines of code here and there,
but 99% of the commits are mine.

Great. I didn't build a failure.
People started using Plat.
It was the first Reddit post I ever made,
and I'm glad my first Reddit post was about UCSBPlat.

## Off To China

Ever since Plat's release,
my life seemed to be back on track again,
at least for the time being.
In the surrounding months,
I won the SBHacks student life category,
achieved Gold in USACO,
and in April 2024,
I was offered an internship on TikTok Shop's backend engineering team from April to August,
which I happily gapped a quarter away from UCSB and went to TikTok.

To be exact, it wasn't TikTok, but its Chinese sibling app called Douyin.
Douyin has the same logo as TikTok, is under the same parent company ByteDance,
and is just as strong in engineering as TikTok, if not stronger,
because ByteDance is kind of the Google aura of China.
For an intern level role, the interview was brutal,
with LeetCode medium and hard plus deep-dive questions into the internals of MySQL and TCP.
Thankfully, whenever they asked me about my resume,
I always told them about UCSBPlat.com,
which would put a smile on their face and a bigger smile on my face in response.

Everyone at the office checked in at 10 am and left at... 10 pm.
There's tons of break though.
And people just stay until 10 pm because that's when corporate Uber
(or DiDi to be exact, that's the Chinese Uber)
becomes free.
I grew a lot from this experience, and if you can read Mandarin, or ask ChatGPT to translate it,
I wrote about my time at TikTok Shop [here](/blogs/jiaming-at-bytedance.md).

While I was in China,
I temporarily passed off some maintenance responsibilities to a friend of mine who was still in Santa Barbara,
because while TikTok Shop does have VPN, it's really slow for scraping,
so it was just easier to keep that stuff in the U.S.
From user feedback and my own thinking,
I still managed to add a few features and improvements to Plat:
the passtime timeline for the current quarter,
better professor abbreviation matching logic,
and various UI improvements.
It was really refreshing from all the business of work.

The significance of my time in China was that,
through that period of tremendous growth,
I got to see how large-scale software systems are built and operated,
and then I went on to apply those takeaways to UCSBPlat after the internship concluded.

## The Evolving Playground

To start off,
I thought it was boring when every course just had a professor name.
Why not give them a face?
Then I realized that it's totally possible to give each professor an image alongside their name
by simply crawling the UCSB department pages recursively and matching
images by the alt tag to professor names, and that feature was born.

Then I realized, from my TikTok Shop experience,
that the database tables in UCSBPlat had no indexes at all,
so I added relevant indexes and sometimes compound indexes too to make data retrieval more efficient.

And I realized that Plat's search bar was too rudimentary,
so, borrowing what I saw at TikTok,
I integrated Elasticsearch into UCSBPlat to make search much more powerful.

I also realized I should have a separate search bar for GE courses.
Because Elasticsearch was already there, that feature was relatively easy to implement,
and now GE search is the most visited page on UCSBPlat.

The UI improvements never stopped.
The GE search bar was overhauled 3 times.
The course grid was fine-tuned a couple times too.
Many improvements here and there.

Just recently,
I wanted to learn about machine learning and apply it hands on.
So I learned the basics,
from linear regression to decision trees,
realized that gradient boosted decision trees might be able to predict a class's grade
based on previous grading plus factors like professor reviews, time, and location,
and implemented that feature using LightGBM and Feast feature store.

And I wanted to learn about data engineering too.
I bumped into this concept of "workflow orchestration framework"
and realized Plat's scraping is a workflow,
and up until then it was being run by a somewhat messy Python script.
That made it the perfect candidate for a refactor.
So I explored Apache Airflow, Prefect, and Dagster,
settled on Dagster,
and refactored the scraping pipeline into it.
Scraping is so much cleaner now,
with a web control panel for scheduling, retries, dependencies, and more.

Plat kept on evolving.
It's been the same mission, just with better features and better implementations.
At some point, Plat stopped being just a course tool and became my technical playground.
Whatever I learned next,
there was a good chance I would bring some piece of it back into Plat.

## The Burnouts

There were multiple moments when I just thought,
"that's it, that's enough Plat for me,"
while I was maintaining it or adding new features to it.

For example,
if Rate My Professors changes its data format,
I have to go adjust my source code to match it.
And it's just super annoying when RMP suddenly breaks,
you go patch that,
and then the next day Daily Nexus changes something too and now you have to deal with that.

And whenever I add a new feature,
my brain just gets overloaded trying to reason out how to make the feature actually good.
I hold every feature I add to Plat to a high standard,
so each feature ends up demanding a lot of brain power.
That burns me out.

I didn't have much magic formula against moments like these.
I just thought, well, this happened before,
it's happening again,
I just gotta take the punch in the face, keep going, and eventually it will be fine.
It's not an elegant solution, but it does work.
If it works, it works.

## Wrapping Thoughts

Well, I'm about to graduate in a quarter or two,
so I've already passed the torch of UCSBPlat to a fellow ACM officer.

A week or two prior to writing this article,
I added what I think would be the one last feature I will ever add to Plat:
Google Login.
It's because some other folks at UCSB ACM want to build on top of UCSBPlat,
and their feature requires login,
so I was like,
"cool, let me add one last touch to this, and then you can build it from there."

But I also just realized,
it's the housing season.
What if UCSBPlat had some housing functionalities?
Like, a forum for subleasing, finding roommates, and reviewing landlords.
Existing websites and Facebook groups already exist,
but what if this could all become more consolidated and structured,
jump started by Plat's existing popularity?

I thought really hard about this possibility,
got burned out a bit in the process,
and concluded that,
it's probably worth doing,
but I'm about to be outta here,
so I'll leave it as a possibility for future builders to explore.
I think I've had enough stress and worries about perfecting new features for UCSBPlat.

I hope after I graduate, UCSBPlat can still survive for a few more years,
until every student product inevitably dies of age.

No matter what,
I've had a great run with Plat.
It's the crown jewel of my personal projects portfolio,
it fueled so much of my technical growth,
it became a playground for whatever new technology I was learning,
and it's something whose impact I am genuinely proud of.

I went to TikTok Shop, saw the tech there,
and added the takeaways to Plat.
I'm interning at ChatGPT Ads this summer.
Will I add ads into Plat after this summer haha?

Nah, I don't wanna monetize Plat.
I think it's already a hassle to keep a product alive from a technical perspective,
and it would be so much more hassle if commercialization gets involved too.
There's other ways to make money.
We don't have to make every issue an issue about money.

At the end of the day,
UCSBPlat started out as a better course tool.
But for me, it became much more than that.
It became proof that if you keep coming back to a meaningful project,
even through the self-doubt, the burnouts, and the random bugs,
the project grows,
and you grow with it.

That's it for now.
It's been a good run.
