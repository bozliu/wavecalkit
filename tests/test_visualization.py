import runpy
import shutil
import subprocess
import os
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

from wavecal.cli import main


def test_animation_script_imports_as_static_matplotlib_scene():
    namespace = runpy.run_path(
        "scripts/render_workflow_animation.py",
        init_globals={"frame": 0.5},
    )
    fig = namespace["fig"]
    assert len(fig.axes) == 4
    plt.close(fig)


def test_cli_render_figures_from_saved_tables(tmp_path: Path):
    run_dir = tmp_path / "run"
    figure_dir = tmp_path / "figures"
    assert main(["run", "--config", "examples/scilly_jason3.yml", "--out", str(run_dir)]) == 0
    assert (
        main(
            [
                "render-figures",
                "--collocations",
                str(run_dir / "tables" / "collocations.csv"),
                "--metrics",
                str(run_dir / "tables" / "metrics.csv"),
                "--out",
                str(figure_dir),
            ]
        )
        == 0
    )
    figures = list(figure_dir.glob("*.png"))
    assert len(figures) == 4
    assert all(path.stat().st_size > 1000 for path in figures)


def test_cli_animate_renders_gif_with_matplotlib_fallback(tmp_path: Path):
    out = tmp_path / "workflow.gif"
    assert (
        main(
            [
                "animate",
                "--config",
                "examples/scilly_jason3.yml",
                "--out",
                str(out),
                "--frames",
                "8",
            ]
        )
        == 0
    )
    assert out.stat().st_size > 20_000
    with Image.open(out) as image:
        assert image.format == "GIF"
        assert getattr(image, "n_frames", 1) >= 8
        assert image.size[0] >= 900
        assert image.size[1] >= 500


def test_mpl_animator_script_command_if_available(tmp_path: Path):
    if shutil.which("mpl-animator") is None:
        return
    root = Path.cwd()
    out = tmp_path / "mpl_animator.gif"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{root / 'src'}:{root}:{env.get('PYTHONPATH', '')}"
    env["WAVECAL_ANIMATION_CONFIG"] = str(root / "examples" / "scilly_jason3.yml")
    completed = subprocess.run(
        [
            "mpl-animator",
            str(root / "scripts" / "render_workflow_animation.py"),
            "--var",
            "frame",
            "--range",
            "0,2*pi",
            "--frames",
            "4",
            "--out",
            str(out),
        ],
        check=False,
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout
    generated_candidates = [
        tmp_path / "render_workflow_animation_animated.py",
        root / "render_workflow_animation_animated.py",
    ]
    generated = next((path for path in generated_candidates if path.exists()), None)
    assert generated is not None, completed.stdout
    rendered = subprocess.run(
        ["python", str(generated), "--sequential"],
        check=False,
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert rendered.returncode == 0, rendered.stdout
    assert out.stat().st_size > 10_000
