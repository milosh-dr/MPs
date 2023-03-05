# Analyzing outcomes of all parliamentary votes in 2022 Poland using different clustering methods

## Background

[Parliament in Poland](https://www.sejm.gov.pl/) consists of 460 members, from which 456 are currently affiliated with 10 political parties, while 4 members remain unaffiliated. The ruling party currently has 238 members in parliament.

Based on public appearances, social media activity, and interviews, we have certain expectations of the MPs' voting principles. Do these expectations align with their actual voting behavior? Do the MPs' voting strategies reflect their beliefs? If we consider only voting outcomes, what groups do they form, and can we suggest any original alliances based on these outcomes? What topics could these alliances be formed over? These are some of the questions that motivated me to undertake this project.

In this file, I will provide a high-level overview of my analysis. For more details and implementation, please follow the links and see the source code.

## Data Gathering and Transformation

The oficial API of the Polish Parliament does not make the download of voting results possible. Therefore, we need to parse the data from the website's HTML. However, the amount of data, unknown server limits, and other factors make it challenging to gather all the data in one go. Hence, I decided to create a cron task to perform this task as a multistage process.

The following line can be run from the shell to add the task to the crontab of the current user and trigger the process:

```sh
(crontab -l 2> /dev/null; echo "0 20 * * * python3 YOUR_LOCAL_PATH/sample_main.py >> YOUR_LOCAL_PATH/log.txt") | crontab -
```

### To keep it organized, I broke down this part of the project into three separate files:

- [sample_main.py][1]
- [collect.py][2]

    This file contains the functionality needed to gather the data.
- [transform.py][3]

    This file contains the functionality needed for data processing.

I have also attached a script, [stop.sh][5], to this repository to clear the crontab from previously added task automatically. The main program *sample_main.py* checks the current status of the process at the beginning of each iteration and stops it when it is finished. It also reports all errors by saving them to *log.txt* file.

By going through this file, we can understand any errors that may have occurred during the process, as there are inconsistencies on the website that may have disrupt it. However, as it happened only twice during my analysis, I decided not to take those votings into account.

If you're curious about the implementation, please take a look at the files. We will keep things simple in this overview.

In short, the program gathers all the data, including not only voting outcomes but also the actual topic of the vote, the date it happened, and the parliament session ID.

This way we got enough information to be able to make some reasonable choices.

Members of parliament can either vote for, against or abstain from voting. I mapped these outcomes to numeric values of 1, 0 and 0.5 respectively. The fourth scenario is the absence.

Questions that arise here are:
- Do any votings matter more than others?
- If so, shall we reduce dimensionality or come up with a certain weighting system that compensates for those differences?
- How shall we deal with MP's absences?
- Do all absences have the same weight for this project?

There were several instances of absence among MPs, which could be attributed to unforeseen circumstances or intentional disapproval. To ensure accuracy, I established specific criteria for intentional absences, including that more than 75% of party MPs need to be absent and the party must have more than 5 members. This approach aims to avoid any personal interpretation of the absence meaning. In the end, only one party at one voting met the criteria, and I treated their absence as a vote against the legislation with a value of 0.

For other cases of absence, I filled them with the prevalent value of the party MP belongs to, which I interpreted as the party's voting strategy. In some situations where the party was too small and the majority was not clear to me, I assigned a value of 0.5.

## Clustering and topics analysis

### Unlike the previous stages, I have chosen to keep the clustering part in a Jupyter Notebook, [clustering.ipynb][4], to enhance clarity.<br><br>

### Cleaning vote_info dataframe

I have taken several significant steps in the analysis presented in clustering.ipynb. First, I cleaned up the vote_info dataframe to ensure that vote IDs were consistent across both dataframes and that the time was transformed into a convenient Pandas datetime format.

### Dimensionality reduction

Second, I made an effort to reduce the dimensionality of the data. To reduce bias in the analysis, I decided to exclude votings related to numerous amendments, which accounted for more than **70%** of the total votings, and focus only on fully ready legislations, which represented less than **15%** of the total votings.

### Clustering

To determine the optimal grouping for members of parliament, I took the next step of fitting the KMeans algorithm multiple times with different configurations and evaluated the clusters using the average silhouette score. This helped me identify the most effective way to group the MPs in a meaningful way for the analysis.

### Identifying crucial topics that bind opposition parties

After learning that the best clusters were achieved with only three groups, my next step was to explore the topics that could constitute the big alliance of opposition parties found in one of the clusters. To achieve this, I proposed two different approaches: finding key words that best describe those topics or extracting legislation names directly.

Identifying crucial topics for opposition parties is an important task for understanding their political priorities and strategies. In order to achieve this, I proposed two different approaches.

The first approach involved finding key words that best describe the topics that constitute the possible big alliance of opposition parties found in one of the clusters. To accomplish this, I used natural language processing techniques to analyze the legislative proposals that were voted on by the members of parliament. By identifying the most important words in these proposals, I was able to gain insight into the topics that were most vital to the opposition parties.

The second approach involved extracting the names of the legislative proposals directly, in order to identify the specific issues that the opposition parties were focused on. This approach was particularly useful for understanding the opposition's stance on specific policy areas, such as social welfare or economic reform.

## Important notes and conclussion

**Please ensure that you have updated the path to the sample_main.py file in the stop.sh script as well as the local_path variable in all Python files, especially if you plan to run this project locally on your machine.**

Overall, this project provides a comprehensive analysis of voting patterns among members of parliament, including identifying key topics and groupings. It serves as a useful tool for understanding political dynamics and trends in parliamentary decision-making. The code and data can be easily adapted for use in other countries or contexts. Any feedback is welcome and contributions to improve the project and expand its capabilities.

[1]: https://github.com/milosh-dr/MPs/blob/main/sample_main.py
[2]: https://github.com/milosh-dr/MPs/blob/main/collect.py
[3]: https://github.com/milosh-dr/MPs/blob/main/transform.py
[4]: https://nbviewer.org/github/milosh-dr/MPs/blob/main/clustering.ipynb#topics
[5]: https://github.com/milosh-dr/MPs/blob/main/stop.sh
<!-- [6]: https://github.com/milosh-dr/MPs/blob/main/clustering.ipynb#C7
[7]: https://github.com/milosh-dr/MPs/blob/main/clustering.ipynb#C12
[8]: https://github.com/milosh-dr/MPs/blob/main/clustering.ipynb#C19
[9]: https://github.com/milosh-dr/MPs/blob/main/clustering.ipynb#C29 -->