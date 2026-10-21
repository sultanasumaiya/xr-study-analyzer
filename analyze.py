"""Summarize XR target-selection trial logs without third-party dependencies."""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

REQUIRED = {'session_id', 'participant_code', 'trial', 'movement_time_ms', 'input_mode'}


def load_trials(paths: list[Path]) -> list[dict]:
    trials = []
    for path in paths:
        with path.open(newline='', encoding='utf-8-sig') as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
                raise ValueError(f'{path}: required columns: {", ".join(sorted(REQUIRED))}')
            for line, row in enumerate(reader, start=2):
                try:
                    ms = float(row['movement_time_ms'])
                    trial = int(row['trial'])
                    if not math.isfinite(ms) or ms <= 0 or trial <= 0:
                        raise ValueError('time and trial must be positive and finite')
                    if not row['session_id'] or not row['input_mode']:
                        raise ValueError('session_id and input_mode are required')
                except (TypeError, ValueError) as exc:
                    raise ValueError(f'{path}:{line}: invalid trial: {exc}') from exc
                trials.append({**row, 'movement_time_ms': ms, 'trial': trial})
    if not trials:
        raise ValueError('No trials found')
    return trials


def percentile(sorted_values: list[float], q: float) -> float:
    at = (len(sorted_values) - 1) * q
    lo = math.floor(at)
    hi = math.ceil(at)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (at - lo)


def summarize(trials: list[dict], seed: int = 42, iterations: int = 2000) -> list[dict]:
    if iterations < 100:
        raise ValueError('iterations must be at least 100')
    groups = defaultdict(list)
    for trial in trials:
        code = trial['participant_code'].strip() or 'anonymous'
        groups[(code, trial['input_mode'])].append(trial['movement_time_ms'])
    rng = random.Random(seed)
    result = []
    for (code, mode), values in sorted(groups.items()):
        n = len(values)
        boot = None
        if n > 1:
            estimates = sorted(statistics.median(rng.choices(values, k=n)) for _ in range(iterations))
            boot = [round(percentile(estimates, .025), 2), round(percentile(estimates, .975), 2)]
        result.append({'participant_code': code, 'input_mode': mode, 'n': n,
                       'median_ms': round(statistics.median(values), 2),
                       'mean_ms': round(statistics.mean(values), 2),
                       'sd_ms': round(statistics.stdev(values), 2) if n > 1 else None,
                       'median_ci95_ms': boot})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_files', nargs='+', type=Path)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--iterations', type=int, default=2000)
    parser.add_argument('--json', type=Path, metavar='OUTPUT')
    args = parser.parse_args()
    try:
        result = summarize(load_trials(args.csv_files), args.seed, args.iterations)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    payload = json.dumps({'groups': result, 'method': 'percentile bootstrap of median',
                          'seed': args.seed, 'iterations': args.iterations}, indent=2)
    if args.json:
        args.json.write_text(payload + '\n', encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
