"""Generates documentation for outcomes and default metrics and datasets."""

from argparse import ArgumentParser
from os import stat_result
import statistics
from jetstream import config, experimenter, AnalysisPeriod
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
import shutil
import toml


ROOT = Path(__file__).parent.parent
OUTCOME_DIR = ROOT / "outcomes"
DEFAULTS_DIR = ROOT / "defaults"
DOCS_DIR = ROOT / ".docs"
TEMPLATES_DIR = Path(__file__).parent / "templates"

parser = ArgumentParser(description=__doc__)
parser.add_argument(
    "--output_dir",
    "--output-dir",
    required=True,
    help="Generated documentation is written to this output directory.",
)


def generate():
    """Runs the doc generation."""
    args = parser.parse_args()
    out_dir = Path(args.output_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(DOCS_DIR, out_dir)

    generate_outcome_docs(out_dir / "docs")


def generate_outcome_docs(out_dir: Path):
    """Generates docs for existing outcomes."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    outcome_template = env.get_template("outcome.md")

    for platform_dir in OUTCOME_DIR.iterdir():
        dummy_experiment = experimenter.Experiment(
            experimenter_slug="dummy-experiment",
            normandy_slug="dummy_experiment",
            type="v6",
            status="Live",
            branches=[],
            end_date=None,
            reference_branch="control",
            is_high_population=False,
            start_date=datetime.now(),
            proposed_enrollment=14,
            app_id=config.PLATFORM_CONFIGS[platform_dir.name].app_id,
            app_name=platform_dir.name,
        )

        for outcome_file in platform_dir.glob("*.toml"):
            spec = config.AnalysisSpec.from_dict({})
            outcome_spec = config.OutcomeSpec.from_dict(toml.load(outcome_file))
            spec.merge_outcome(outcome_spec)
            conf = spec.resolve(dummy_experiment)

            default_metrics = [m.name for m in outcome_spec.default_metrics]
            summaries = [summary for summary in conf.metrics[AnalysisPeriod.OVERALL]]
            metrics = [
                summary.metric
                for summary in summaries
                if summary.metric.name not in default_metrics
            ]
            # deduplicate metrics
            deduplicated_metrics = []
            for metric in metrics:
                if metric not in deduplicated_metrics:
                    deduplicated_metrics.append(metric)
            metrics = deduplicated_metrics

            data_sources = {m.data_source for m in metrics}

            statistics_per_metric = {}
            for metric in metrics:
                statistics = [
                    summary.statistic.name()
                    for summary in summaries
                    if summary.metric.name == metric.name
                ]
                statistics_per_metric[metric.name] = statistics

            outcome_doc = (
                out_dir / "outcomes" / platform_dir.name / (outcome_file.stem + ".md")
            )
            outcome_doc.parent.mkdir(parents=True, exist_ok=True)
            outcome_doc.write_text(
                outcome_template.render(
                    slug=outcome_file.stem,
                    platform=platform_dir.name,
                    outcome_name=outcome_spec.friendly_name,
                    outcome_description=outcome_spec.description,
                    metrics=metrics,
                    data_sources=data_sources,
                    statistics=statistics_per_metric,
                )
            )


if __name__ == "__main__":
    generate()
