# Analyzing outcomes of all parliament votings in Poland using different clustering methods

## Background

[Parliament in Poland](https://www.sejm.gov.pl/) consists of 460 members, from which 456 are currently affiliated with 10 political parties. 4 members remain unaffiliated. The ruling party has currently 238 members in parliament.

We have certain expectations from MPs' voting principles based on public appearances, social media activity and interviews. Are these expectations met? Does the voting strategy mirror their beliefs? What groups do they actually form if we consider voting outcomes only? Can we suggest any original alliances in there based on those outcomes? These and more questions crossed my mind going through the process of this project.



## Gathering and transforming data

The oficial API of Polish Parliament doesn't make it possible to download voting results. One needs to parse them from website's HTML. The amount of data, unknown server limits and some other factors made me create a cron task to get this job done as a multistage process. In my case only two days were enough to gather data from the beginning of 2022 up to now.

The process can be trigerred from a shell:

```sh
(crontab -l 2> /dev/null; echo "0 20 * * * python3 YOUR_LOCAL_PATH/sample_main.py >> YOUR_LOCAL_PATH/log.txt") | crontab -
```

This line simply adds a task between quotation marks to the crontab of current user.

Crontab will be cleared from this task automatically using script *stop.sh* attached to this repository.

Going through log.txt file lets us understand errors if occured. There are some inconsistencies on the website that disturbed the process, but since it happened with only two votings decided not to take them into consideration during analysis.

To keep it clear, I broke this part of the project into three separate files:

- [sample_main.py][1]
- [collect.py][2]

    Functionality needed to gather data.
- [transform.py][3]

    Functionality needed for data processing.

Please take a look if you're curious about the implementation. Here we keep things simple.

In short, the idea was to gather all the data, not only voting outcomes, but the actual subject of it, date it happened along with parliament session id as well.

This way we got enough information to be able to make some reasonable choices.

Members of parliament can either vote for, against or abstain from voting. I mapped these outcomes to numeric values of respectively 1, 0 and  0.5. Fourth scenario is the absence.

Questions arising here are:
- Do any votings matter more than others?
- If so, shall we reduce dimensionality or come up with a certain weighting system compensating those differences?
- How to deal with MP's absences?
- Do all absences mean the same for the sake of this project?

Since more than **70%** of votings refered to numerous amendments and less than **15%** to fully ready legislations, I decided to keep only the latter for the analysis. This way we might introduce less bias into it. It feeled unnecessary to weight those votings differently to me.

There were quite a few absences. Those could be either due to unforseen events or could mean intentional disapprovement. I wanted to be cautious about it and took such criteria for the absence being intentional:
- more than **75%** of a party MP belongs to needs to be absent,
- this party needs to have more than **5** members.

This way I hope to avoid imputing meaning myself. The criteria were met with only one party at only one voting and I decided to treat it as voting against legislation (value of 0).

Other absences were filled with the prevalent value of the party MP belongs to (interpreted as party's voting strategy).
In few cases were the party was too small and majority feeled two week to me, I gave the value of 0.5.

Interesting addition would be subject modelling, but this I kept for future.


[1]: https://github.com/milosh-dr/MPs/blob/main/sample_main.py
[2]: https://github.com/milosh-dr/MPs/blob/main/collect.py
[3]: https://github.com/milosh-dr/MPs/blob/main/transform.py