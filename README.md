# XR Study Analyzer

A dependency-free Python command-line tool for summarizing trial logs from [XR Target Lab](https://github.com/sultanasumaiya/xr-target-lab). It calculates descriptive movement-time statistics by participant and input mode, and a seeded percentile bootstrap interval for the median.

## Use

Python 3.10+:

```bash
python analyze.py examples/trials.csv --seed 42 --iterations 2000
python analyze.py examples/trials.csv --json results.json
python -m unittest discover -s tests -v
```

The example is **synthetic** and exists only to exercise the tool. Pass multiple CSV paths to combine sessions. The analyzer rejects missing fields, nonpositive times, and empty data. Each group reports `n`, median, mean, sample standard deviation when `n ≥ 2`, and a 95% percentile bootstrap interval for the median. Single observations have no interval. The interval describes sampling variability under resampling assumptions, not a treatment effect or a significance test. No personal identifiers are required.

## License

MIT; see [LICENSE](LICENSE).
