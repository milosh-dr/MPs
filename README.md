### Title

The idea behind this project bla bla bla

### Gathering data

The oficial API of Polish's Parliament doesn't make it possible to download vote results. One needs to parse them from website's HTML. The amount of data, unknown server limits and some other factors made me create a cron task to get this job done as a multistage process. In my case only two days were enough to gather data from the beginning of 2022 up to now.

I run  bash script, but could be trigerred

```sh
(crontab -l 2> /dev/null; echo "0 20 * * * python3 *YOUR_LOCAL_PATH*/sample_main.py >> *YOUR_LOCAL_PATH*/log.txt") | crontab -
```


Table | skdjs | skdj
sdsa | dsasd | dsdfsd

