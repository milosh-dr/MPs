### Title

The idea behind this project bla bla bla

### Gathering data

The oficial API of Polish's Parliament doesn't make it possible to download vote results. One needs to parse them from website's HTML. The amount of data, unknown server limits and some other factors made me create a cron task to get this job done as a multistage process. In my case only two days were enough to gather data from the beginning of 2022 up to now.

The process can be trigerred from a shell:

```sh
(crontab -l 2> /dev/null; echo "0 20 * * * python3 YOUR_LOCAL_PATH/sample_main.py >> YOUR_LOCAL_PATH/log.txt") | crontab -
```

It simply adds a task between quotation marks to the crontab of current user.

Going through log.txt file lets us understand errors if occured. There were some inconsistencies on the website that disturbed the process, but since it happened with only two votings I decided not to take them into consideration during analysis.

To keep it clear, I decided to break this part of the project into three separate files:

- [sample_main.py][1]
- [collect.py][2]
- [transform.py][3]


[1]: https://github.com/milosh-dr/MPs/blob/main/sample_main.py
[2]: https://github.com/milosh-dr/MPs/blob/main/collect.py
[3]: https://github.com/milosh-dr/MPs/blob/main/transform.py