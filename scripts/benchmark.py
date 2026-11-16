"""Scale benchmark for the rule engine and interaction screen.

Runs a synthetic queue orders of magnitude larger than the deployed
16-event roster and reports throughput and per-event latency. The
deployed queue stays at 16; this is a script, not a deploy change.

    python3 scripts/benchmark.py
"""

import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_synthetic import generate_events
from src.rules import evaluate_event
from src.rules.interactions import attach_interaction_alerts, screen_interactions

BENCHMARK_SIZES = (1000, 10000, 100000)
BENCHMARK_SEED = 42


@dataclass(frozen=True)
class BenchmarkResult:
    """One run's throughput and per-event latency, in milliseconds."""
    count: int
    total_seconds: float
    events_per_second: float
    p50_ms: float
    p95_ms: float
    p99_ms: float


def percentile(sorted_values: "list[float]", fraction: float) -> float:
    """Takes sorted values and a fraction. Returns that percentile."""
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1,
                int(round(fraction * (len(sorted_values) - 1))))
    return sorted_values[index]


def run_benchmark(n: int, seed: int = BENCHMARK_SEED) -> BenchmarkResult:
    """Takes an event count. Returns throughput and p50, p95, and p99
    per-event latency for the full rule engine plus interaction screen."""
    events = generate_events(n, seed)
    latencies = []
    start = time.perf_counter()
    evaluated = []
    for event in events:
        event_start = time.perf_counter()
        evaluated.append(evaluate_event(event))
        latencies.append((time.perf_counter() - event_start) * 1000.0)
    screen = screen_interactions(evaluated)
    attach_interaction_alerts(evaluated, screen)
    total = time.perf_counter() - start

    latencies.sort()
    return BenchmarkResult(
        count=n,
        total_seconds=total,
        events_per_second=n / total if total else 0.0,
        p50_ms=percentile(latencies, 0.50),
        p95_ms=percentile(latencies, 0.95),
        p99_ms=percentile(latencies, 0.99),
    )


def print_table(results: "list[BenchmarkResult]") -> None:
    """Takes benchmark results. Prints a small fixed-width table."""
    header = (f"{'events':>10}  {'seconds':>9}  {'events/sec':>12}  "
              f"{'p50 ms':>8}  {'p95 ms':>8}  {'p99 ms':>8}")
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r.count:>10}  {r.total_seconds:>9.3f}  "
              f"{r.events_per_second:>12,.0f}  {r.p50_ms:>8.4f}  "
              f"{r.p95_ms:>8.4f}  {r.p99_ms:>8.4f}")


def main() -> None:
    """Runs the benchmark at every configured size and prints the table."""
    results = [run_benchmark(n) for n in BENCHMARK_SIZES]
    print_table(results)


if __name__ == "__main__":
    main()
