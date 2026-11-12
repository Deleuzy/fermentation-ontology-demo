"""Each query's answer is recomputed from the CSV with plain Python and compared."""

from collections import Counter, defaultdict

import pytest

from ferm_demo.paths import QUERIES
from ferm_demo.queries import run_all


@pytest.fixture(scope="module")
def results(onto, good):
    return run_all(onto + good.data, QUERIES)


def test_runs_per_organism(results, rows):
    expected = Counter(r["organism_name"] for r in rows)
    got = {r["organism"]: r["runs"] for r in results["01_runs_per_organism"]}
    assert got == dict(expected)


def test_mean_titre_per_carbon_source(results, rows):
    titres = defaultdict(list)
    for r in rows:
        if r["titre_g_per_L"]:
            titres[r["carbon_source"]].append(float(r["titre_g_per_L"]))
    got = {r["carbon_source"]: (r["n_with_titre"], r["mean_titre"]) for r in results["02_mean_titre_per_carbon_source"]}
    assert got.keys() == titres.keys()
    for source, values in titres.items():
        assert got[source][0] == len(values)
        assert got[source][1] == pytest.approx(round(sum(values) / len(values), 2))
    assert {r["unit"] for r in results["02_mean_titre_per_carbon_source"]} == {"gram per liter"}


def test_runs_missing_titre(results, rows):
    expected = [f"fermentation run {r['run_id']}" for r in rows if not r["titre_g_per_L"]]
    assert (
        [r["run_label"] for r in results["03_runs_missing_titre"]]
        == expected
        == [
            "fermentation run R06",
            "fermentation run R10",
        ]
    )


def test_runs_using_methanol(results, rows):
    expected = [(f"fermentation run {r['run_id']}", r["organism_name"]) for r in rows if r["carbon_source"] == "methanol"]
    got = [(r["run_label"], r["organism"]) for r in results["04_runs_using_methanol"]]
    assert got == expected


def test_titre_by_mode(results, rows):
    by_mode = defaultdict(list)
    for r in rows:
        if r["titre_g_per_L"]:
            by_mode[r["mode"]].append(float(r["titre_g_per_L"]))
    got = {r["mode"]: r for r in results["05_titre_by_mode"]}
    for mode, label in (("batch", "batch fermentation run"), ("fed-batch", "fed-batch fermentation run")):
        values = by_mode[mode]
        assert got[label]["n_with_titre"] == len(values)
        assert got[label]["mean_titre"] == pytest.approx(round(sum(values) / len(values), 2))
        assert got[label]["max_titre"] == pytest.approx(max(values))
