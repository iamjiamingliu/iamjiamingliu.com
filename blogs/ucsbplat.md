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

Actually one more thing: the 9,000+ is the number on a low month, where there isn't an active course registration period happening.
For months with active course registration that everyone would go on Plat and look around courses information,
I think the number would range from 10K to 15K.

![](/static/img/projects/ucsbplat_google_analytics.png)


## The Other Side of the Story

My name is Jiaming Liu, UCSB Computer Science Class of 2027.
I created UCSBPlat.com as my freshman year winter break hobby project and have maintained it ever since.
In this blog, I want to show you the other side of the story:
how Plat was built, how it evolved, and how it might go in the future.

While you read, I want to draw your attention to these themes I experienced:

1. It's okay to feel like giving up, as long as you come back to it
2. It's okay and natural to feel burned out. The good news is that passion will bounce back
3. What a playground!
4. Like Warren Buffet said, "Our favorite holding period is... forever."

What do I mean by these themes? Well, keep on reading. Here we go!

## The Birth of Plat: the mission and name

When I started my undergrad at UCSB back in fall 2023,
I was just thoroughly disgusted by the difficulty of use and ugly UI of GOLD (Gaucho Online Data),
the official curriculum registration platform of UCSB.

I love building websites. Especially websites with beautiful UI.
I've been building websites since high school.
So I thought,
_why not build a GOLD wrapper website with the same data, but just prettier UI?_

But then I realized, no one would want to use a website like that.
Sure, it looks prettier than GOLD, but so what?
Do I want to open another tab just to see the same information as GOLD?
Being a pretty wrapper doesn't seem to give a compelling enough benefit for users to use it.
Thus, that was the end of UCSBPlat before it was even called UCSBPlat.

Thankfully, as I was wandering around the UCSB lagoon one day,
I realized what could become a compelling enough reason for users to use website:
_what if in addition to having all the catalog data from GOLD,
we also aggregate and present it together with Rate My Professor reviews and Daily Nexus grading trends, all with a really gorgeous UI?_
After all, I see friends with GOLD, RMP, and Daily Nexus open in browser tabes whenever they are signing up for a course.
Given that a tiny bit less of user friction would result in a significantly better user experience,
surely having one site for them all would justify a compelling enough benefit for users.

The same data as GOLD. With a better UI. And aggregated with additional information too.
It's better than Gold. It's gotta be Platinum.
Thus, the name and vision for UCSB Platinum, UCSBPlat.com, was born.

## Giving up before a line of code

A lesson I learned from my previous website projects was,
before any line of code is written, start with a plan first.
Sure, software engineering is an iterative, discovery, and evolving process,
but you gotta start with a plan first.
Without a plan, the code would go nowhere,
and you would just be wasting time trying to inefficiently juggle between coding and implicitly planning it while you code.

So I went out to sketch out the plan:
the user story, the UI, the domain design, the scraping workflow, architecture, and the database table design.
And I realized, oh boy, what the hell of a mess UCSBPlat was gonna be.

Sure, today when you look at UCSBPlat,
everything is clean: the UI is intuitive, you search for a class, click it, and see the aggregated data.
But nothing is clean in the beginning.
In the beginning everything was mayhem.
Only through so much brain power drainage and iterations would mayhem slowly morph into being clean.

I realized to make UCSBPlat happen, I had to wrestle with a monster with this many arms in front of me:

1. 13 database tables needed to store all the courses, professors, reviews, section, enrollment trends, grading trends, etc.
2. An enormous Python script needed to scrape courses from GOLD. And do it again with rate my professors. And do it again with Daily Nexus grading trends.
3. Extra complicated joining logic needed to correctly resolve "Bob Anderson" on rate my professor to the abbreviation "R W Anderson" listed on in GOLD
4. God knows how many SQL lines are needed to JOIN all the related data together

And many more...

I was living in the Anacapa dorm in my freshman year.
For a whole week straight,
I would spend afternoon and late nights there sketching out UCSBPlat UI drafts, database design, and scraping workflow outline
with pencil and letter paper I grabbed from downstairs printer tray.
I don't know Figma or anything complicated, just pencil and paper.
I still use pencil and paper.
The more I sketched, the more I realized what kind of monster lies in front of me.

Maybe the best way to deal with a bottomless pit is to just don't go into it.
So, on the seventh day, I decided I'm out.
UCSBPlat was dead again before a single line of code was written.
My mental mayhem had dragged me down.

While I was planning, I saw that, the idea of UCSBPlat was not _that_ original at all.
There are already many course catalog wrapper and scheduler at UCSB:
gauchocourses.com, GoGaucho iOS app, and more.
After the release of UCSBPlat, these sites all have silently shut down now,
or aren't as popular as before Plat came and zeized the market.
But still, when I was planning, I thought,
_if all the giants before me already exist, why am I qualified enough to wrestle them?_
In hindsight, the reason is clear:
the emphsis on existing sites are schedule planning,
while the emphasis on UCSBPlat is the aggregation with professor reviews, grading trends, and more.
Plus, UCSBPlat have a much cleaner, intuitive, and prettier UI.
But the freshman year version of me couldn't tell what my edge was.
It's important to know your edge.

Really, if you think about many of the great internet software out there,
they weren't the first. They are just better.
Before Facebook there was myspace. Before Google there was Yahoo and many search engines.
Before Amazon there were many ecommerce sites.
Ideas may be important, but execution is the killer.
As my other blog article said, [idea is cheap, but execution is gold](/blogs/problem-solution-execution.md).
People today only know UCSBPlat, but UCSBPlat wasn't the first.
It's just better.

## But I have to shoot this shot

You know, I'm a busy person.
Not in the sense that I get overwhelmed by too much work,
but rather in the sense that, I just can't afford being not busy.
I can't spend a long period of time not working on something big.
If I'm not working on something big, I feel sad.
I have to keep myself busy.

I just started freshman year back then.
All those accomplishments I did in high school got reset to zero.
I'm now a nobody freshman rookie in a big university without any titles or anything to hold on to.
I tried to join the UCSB ICPC competition, but I didn't make the cut.
I tried to join CoderSB and got rejected
<small>(I think I got rejected? But I definitely tried to join UCSB ACM a year later, the direct successor of CoderSB club, and got rejected. Ironically I later became the President of UCSB ACM. You never know what could happen in life).</small>
I tried to replicate my TV newscast experience back in high school here at UCSB,
and that didn't work either.
I applied for UCSB TV, never heard back, until I emailed them to which they replied "huh? we didn't see your application".
I joined The Bottom Line News, which also was lame.
Really, it just felt that in the first 2 months of college, I was trying this and that and got nowhere in everything I tried.

Maybe UCSBPlat would become one more thing I tried and get nowhere.
And become a joke.
You can't afford being a joke when everything isn't working.

But I just can't do nothing. I'm a busy person. I have to be working on something.
Out of all the things I thought of, Plat is the one last thing I could try.
Sure, it could fail, but I assured myself that,
at least I could learn new technologies (ORM, Scrapy, etc.) from this experience,
and it can go on my resume no matter what.

So, let's just go for it and see where it goes.
You really can't tell.
There are many software projects I built before Plat, and after Plat,
that were meticulously planned and well executed.
Some of them became lasting and loved by many,
but many also faired in anonymity.
But you never know. You just have to try it.
Shoot the shot.

## The Winter Break

Thus the grind has begun.
If I remembered correctly,
during weeks leading up to the freshman year fall quarter finals,
I was just sketching all the time away with pencil and paper about Plat.
I just had to swallow the fact that, I'm about to fight a monster,
I might fail, but I have to shoot this shot, and no matter what, I will grow from this journey.
I wrote a few scripts and concluded that it's technically feasible to crawl and index UCSB catalog, rate my professors, and daily nexus grades.
I didn't crawl GOLD, because as a rule of thumb in crawling, you don't crawl logged-in content.
Instead, I crawled the [Student Affairs Public Catalog](https://my.sa.ucsb.edu/public/curriculum/coursesearch.aspx)
for the course information, which is public and doesn't require login.
For rate my professor, I simply crawled the top 6 reviews per professor as overview so that it's fair use,
and "see more" would link the user directly to rate my professor.
Finally, for grading trends from Daily Nexus,
they publish their data as a CSV file on Github anyways, so I just used that.
You reciprocate favors:
later on, Daily Nexus asked Plat to use some of Plat's data, to which I generously gave.

In a way, it's like building a mini-Google, but limited to 3 sites about UCSB courses.

Winter break came, I had nothing else to do, so I went all in to build out the actual UCSBPlat.com guided by the prior planning.
There wasn't Claude Code nor Codex, ChatGPT was pretty shitty back then,
so I just manually coded out everything.
I used Python Flask and HTML and Bootstrap 5 for the frontend,
Selenium + Scrapy + Requests for scraping,
and at first just PostgreSQL for data storage.
I would wake up, quickly eat breakfast, and just start coding.
I was so freaking locked in.
My eyes would get a bit blurry and dry, my stamina would get exhausted,
but I just kept going because I believed I was building something big.
I was happy that I found my calling.

Nowadays whenever I add a new feature or bug fix to Plat,
I would use Codex and ChatGPT to assist the process,
but I always steer and code the important stuff myself.
I believe there's something irreplaceable about human intelligence,
and AI assitants are called assitants because they are good at telling you what's wrong and doing the straightforward stuff,
but they can't steer the ship yet.
If AI can steer the ship, why are AI companies still hiring humans?
At the moment, humans matter, and AGI isn't here yet.

I later on tried to build a Plat for UCLA, and all the coding tools failed hilariously,
and I concluded it's not worth my time to build another Plat for a school I don't even go to.
I will leave this gem idea to whoever next can execute effectively on it at UCLA.
I guarantee you, there will be a heck ton of users.

God knows how many challenges I ran into while building Plat...
Professor name abbreviation mismatch, SQL JOIN issues,
and just mysterious bugs everywhere.
And which ever issues comes up,
I just gotta Google search and click through all the StackOverflow and Youtube and blogs to find a solution.
If none exist already, I just had to try many things out myself.
Good old times before AI slop came along.
It felt like 过五关斩六将, the classic Chinese lore of a general having to fight through all the castles before reaching the destination.
Well, isn't that how every meaningful journey goes? No journey is a journey without challenges.
You just gotta push through them all.

I'm glad all the previous projects I built in high school prepared me for this moment.
When everyone was Senioritus-ing the last semester of high school away,
I leveled up my SQL skills and learned about SQLAlchemy the ORM,
and they came so clutch for UCSBPlat.
SQL is already complicated, ORM like SQLAlchemy adds another layer of abstraction and complexity on top,
so I really struggled to grapple SQLAlchemy at first,
but thankfully I figured it out eventually and SQLAlchemy saved me so much effort later on.

I proudly showed off my progress to my dad, an iOS veteran developer.
But he didn't seem to understand what I was doing nor the implication of Plat's possible signifiance.
I also told many friends about Plat.
Some courteously said "wow this is great" while most just said "ok cool".
I mean, I guess when you are trying to innovate and build something new,
people won't get it at first.
They shouldn't get it.
If something is so easily understood by everyone, it won't be waiting for you to build.
You get the opportunity to build it because only you know it could be a gem when everyone just thinks it's another stone, or doesn't see it exist at all.
You may be horribly wrong, but if you are right, it pays.

There's so many more moments like UCSBPlat where my idea or proposal gets ignored or scolded,
and eventually it turns out I'm right and a meaningful innovation is brought forth,
and occasionally I'm wrong and let it be.
There are also a few times my friends proposed some strange, seemingly nonsense endeavors that I ignored.
Sometimes they turn out to be wrong, and other times they are right, make a hit, and I was wrong.
After all, good innovation ideas should be non-obvious, counter intuitive, and bold.
It should be surprising.

## The Reddit Post, with typo

Time to launch.

But where to launch?

Well I got lazy,
so I just dropped one post on Reddit and called it a day.
I thought, _if this reaches enough users, I think it's sufficient and I can just not do other promo._
So, on January 1st 2024,
I posted [this Reddit Post](https://www.reddit.com/r/UCSantaBarbara/comments/1aegcjn/introducing_ucsb_platinum_usbplatcom_its_gold_but/)
in r/UCSantaBarbara and just prayed it would go well.
And luckily, it did.
The post gained 29,000 views within 48 hours of its posting,
although I was afraid to measure how many of them actually clicked to UCSBPlat from the post.
I made a typo in the post title: "Introducing UCSB Platinum **usbplat**.com - It's GOLD, but Better."
Oops, USBPlat instead of UCSBPlat.

My friend strongly encouraged me to set up Google Analytics for Plat,
to which I refused, because I worried the number of visitors might look bad.
Then I was like fuck nah let's just add it and see the truth,
and thankfully, the numbers were fine.
And according to Google Analytics, UCSBPlat organically grew, through word of mouth after the initial Reddit post,
from 0 to 9,000+ users since then.

If you look at the OG Reddit post,
there was a feature that no longer exist:
course recommendation.
I thought course recommendation would be a hit,
only to realize that almost no one used it.
I later tried to use some complicated DAG logic and retrieval pipeline to improve the recommedation,
but that didn't strike the users too.
So I just took it down the recommendation feature.
Nowadays people occasionally say "why don't you add a recommendation feature",
and I reply "well I did, and no one used it."
I suspect the failure is because the user would need to upload their transcript PDF,
which is quite a hassle to do and would raise privacy eyebrows.
If Plat has a Google login that just knows all the courses automatically so that course recommendation can be shown
without having to take an extra step of uploading the transcript,
I'm guessing the feature could be very popular instead of fairing badly in anonymity.
After all, any extra friction in the user experience would kill the usage.
Imagine Amazon shopping recommendation would require you to upload all of your shopping receipts from the past;
I doubt anyone would use that.
But if Amazon just tracks all the stuff you've browsed and purchased so far automatically
and show recommendation without you having to ask for it first,
then people will use it.
Friction kills.

The person who created gauchocourses.com saw the Reddit post and reached out to me to build a feature on Plat.
I thought he was trying to scam me or hack into UCSBPlat.
After all, GauchoCourses.com is a competitor.
But after we got on a Discord call and introduced ourselves, I saw he meant no harm.
He's just another Gaucho technologist who likes building things, so I let him built the feature.
We've become good friend since then, he's an officer on the SBHacks organizing team,
so I stayed on the SBHacks organizing team for the next 2 years because of him.

Two years later, the alumni from 7 years ago who GoGaucho iOS app reached out to me on Instagram.
I was shocked to see how he found me, and he said it's because the current maintainers of GoGaucho was talking about Plat,
which is how he heard.
He was an international Chinese student just like me, so, we conversed in Mandarin and had a good time.
I then became VP of UCSB ACM and interviewed this guy for the ACM Alumni Spotlight Series.

I reached out to UC Berkeley's Plat equivalent BerkeleyTime.com.
I got on a call with their project manager,
talked about Plat,
discussed issues that apparently both BerkeleyTime and Plat face,
and had a good time.
But I can't help but laugh at the fact that,
BerkeleyTime has a team of 10 to 20 students just to maintain the site.
Plat was all me, built and maintained.
To be precise, my friends added a few lines of code here and there, but 99% of the commits are from me.
No way BerkeleyTime needs 20 people just to maintain their site.
And their site is actually shittier than UCSBPlat:
the grading trends and enrollment trends require separate lookup on different pages,
and it doesn't even have professor reviews.

Great. I didn't build a failure. People started using Plat.
It was the first Reddit post I ever made, and I'm glad my first Reddit post was about UCSBPlat.

## Off To China

Ever since Plat's release,
my life seemed to be back on track again,
at least for the time being.
In the surrounding months,
I won the SBHacks student life category,
achieved Gold in USACO,
and in April 2024,
I was offered to intern on the Tiktok Shop's backend engineering team from April to August,
which I happily gapped a quarter away from UCSB and went to TikTok.

To be exact, it wasn't TikTok, but its Chinese sibling app called Douyin.
Douyin have the same logo as TikTok, is under the same parent company Bytedance,
and is just as strong in engineering as TikTok if not stronger,
because Bytedance is the Google aura of China.
For an intern level role, the interview was brutal,
with Leetcode medium and hard and deep dive questions into the internals of MySQL and TCP.
Thankfully, whenever they asked me about my resume,
I always told them about UCSBPlat.com,
which would put a smile on their face and a bigger smile on my face in response.

Everyone at the office checked in at 10 am and left at... 10 pm.
There's tons of break though.
And people just stay until 10 pm because that's when corporate Uber (or DiDi to be exact, that's the Chinese Uber) becomes free.
I grew a lot from this experience, and if you can read or ask ChatGPT to translate Mandarin,
I wrote about my time at TikTok shop [here](/blogs/jiaming-at-bytedance.md).

While I was in China,
I temporarily passed off the maintenance role of Plat to a friend of mine who was still in SB.
because while TikTok Shop does have VPN, it's really slow for scraping, so it's just easier to do it within the U.S.
From user feedback and my own thinking,
I still managed to add a few features and improvements to Plat:
the passtime timeline for the current quarter,
better professor abbreviation matching logic,
and various UI improvement.
It was really refreshing from all the business of work.

The significance of my time in China was that,
from this period of tremendous growth,
I saw how large scale software systems are built and operated,
and then I went on to apply the takeaways into UCSBPlat right after the internship concluded.

## The Evolving Playground

To start off,
I thought that it's boring when every course just have a professor name.
Why not give them a face?
Then I realized that it's totally possible to give each professor an image alongside their name
by simply crawling the UCSB department pages recursively and matching
images by the alt tag to professor names, and that feature was born.

Then I realized, from my TikTok shop experience,
that the database tables in UCSBPlat had no index at all,
so I added relevant indexes and sometimes compound indexes too to make data retrieval more efficient.

And I realized that Plat's searchbar is really rudimentary,
so, borrowing what I saw at TikTok,
I integrated the ElasticSearch engine into UCSBPlat to facilitate more powerful searching capabilities.

I also realized I should have a separate searchbar for searching GE courses.
Because ElasticSearch already existed, that feature was easily implemented,
and now, GE search is the most visited page on UCSBPlat.

The UI improvements never stopped.
The GE searchbar was overhauled 3 times.
The course grid was fine-tuned a couple times too.
Many improvements here and there.

Just recently,
I wanted to learn about machine learning and apply it hands on.
So, I learned about all the linear regression and decision trees,
realized that gradient boosted decision trees might be able to predict a class's grade based on its previous grading and factors like professor's review, time and location of the class, etc.,
and implemented this feature using LightGBM and Feast features store.

And I wanted to learn about data engineering too.
I bumped into this concept of "workflow orchestration framework"
and realized, Plat's scraping is a workflow, and up until then,
the scraping is done using a somewhat messy Python script and might be the perfect target for a refactoring using some workflow orchestration framework.
So I explored around Apache airflow, prefect, and dagster,
settled on Dagster,
and refactored the scraping workflow to the framework.
Scraping is so much cleaner now,
with a web control panel for scheduling, retry, dependency, and more.

Plat kept on evolving.
It's been the same mission, just with better features and better implementations.
It's a playground for whatever technical takeaways I got from the relic of my TikTok internship and wherever the later technical curiosity took me.

## The Future
