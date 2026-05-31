import csv
from pathlib import Path

from wavecal.cli import main
from wavecal.pipeline import run_pipeline


def test_pipeline_writes_report_and_metrics(tmp_path: Path):
    outputs = run_pipeline("examples/scilly_jason3.yml", tmp_path / "scilly")
    assert outputs["metrics"].exists()
    assert outputs["collocations"].exists()
    assert outputs["report"].exists()
    assert outputs["provenance"].exists()
    figures = list((tmp_path / "scilly" / "figures").glob("*.png"))
    assert len(figures) == 4
    assert all(path.stat().st_size > 1000 for path in figures)
    with outputs["metrics"].open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4


def test_cli_run(tmp_path: Path):
    status = main(["run", "--config", "examples/scilly_jason3.yml", "--out", str(tmp_path / "run")])
    assert status == 0
    assert (tmp_path / "run" / "report.md").exists()


def test_cli_split_commands(tmp_path: Path):
    alt_out = tmp_path / "alt.csv"
    buoy_out = tmp_path / "buoy.csv"
    pairs_out = tmp_path / "pairs.csv"
    metrics_out = tmp_path / "metrics.csv"
    report_out = tmp_path / "report.md"
    assert main(["ingest-altimeter", "--source", "csv", "--input", "examples/data/scilly_altimeter_sample.csv", "--out", str(alt_out)]) == 0
    assert main(["ingest-buoy", "--source", "csv", "--input", "examples/data/scilly_buoy_sample.csv", "--out", str(buoy_out)]) == 0
    assert main(
        [
            "collocate",
            "--altimeter-csv",
            str(alt_out),
            "--buoy-csv",
            str(buoy_out),
            "--station-lat",
            "49.816667",
            "--station-lon",
            "-6.545167",
            "--out",
            str(pairs_out),
        ]
    ) == 0
    assert main(["fit", "--collocations", str(pairs_out), "--out", str(metrics_out)]) == 0
    assert main(["report", "--metrics", str(metrics_out), "--collocations", str(pairs_out), "--out", str(report_out)]) == 0
    assert report_out.exists()
