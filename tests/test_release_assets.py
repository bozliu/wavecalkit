from pathlib import Path

from PIL import Image

from wavecal.release_audit import audit_release


def test_release_audit_tracked_files_pass():
    result = audit_release(".", mode="tracked")
    assert result.passed, result.findings
    assert result.checked_files > 0


def test_hero_gif_exists_and_is_animated():
    for path in [
        Path("docs/assets/wavecalkit_hero.gif"),
        Path("docs/assets/wavecalkit_workflow.gif"),
        Path("docs/assets/wavecalkit_mpl_animator.gif"),
    ]:
        assert path.exists()
        assert path.stat().st_size > 50_000
        with Image.open(path) as image:
            assert image.format == "GIF"
            assert getattr(image, "n_frames", 1) >= 8
            assert image.size[0] >= 900
            assert image.size[1] >= 500


def test_readme_embeds_tracked_gifs():
    readme = Path("README.md").read_text(encoding="utf-8")
    for asset in [
        "docs/assets/wavecalkit_hero.gif",
        "docs/assets/wavecalkit_workflow.gif",
        "docs/assets/wavecalkit_mpl_animator.gif",
    ]:
        assert asset in readme
        assert Path(asset).exists()
