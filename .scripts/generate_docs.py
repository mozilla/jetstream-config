"""Generates documentation for outcomes and default metrics and datasets."""

from argparse import ArgumentParser
from jetstream_config_parser.analysis import AnalysisSpec
from jetstream_config_parser.config import entity_from_path, ConfigCollection
from jetstream_config_parser.experiment import Experiment
from jetstream_config_parser.metric import AnalysisPeriod
from jetstream_config_parser.outcome import OutcomeSpec
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
import shutil
import toml


ROOT = Path(__file__).parent.parent
OUTCOME_DIR = ROOT / "outcomes"
DEFAULTS_DIR = ROOT / "defaults"
DEFINITIONS_DIR = ROOT / "definitions"
FUNCTIONS_FILE = DEFINITIONS_DIR / "functions.toml"
DOCS_DIR = ROOT / ".docs"
TEMPLATES_DIR = Path(__file__).parent / "templates"

parser = ArgumentParser(description=__doc__)
parser.add_argument(
    "--output_dir",
    "--output-dir",
    required=True,
    help="Generated documentation is written to this output directory.",
)

_ConfigCollection = ConfigCollection.from_github_repo()


def generate():
    """Runs the doc generation."""
    args = parser.parse_args()
    out_dir = Path(args.output_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(DOCS_DIR, out_dir)

    generate_metrics_docs(out_dir / "docs")
    generate_data_source_docs(out_dir / "docs")
    generate_segment_data_sources_docs(out_dir / "docs")
    generate_segment_docs(out_dir / "docs")
    generate_outcome_docs(out_dir / "docs")
    generate_default_config_docs(out_dir / "docs")
    generate_function_docs(out_dir / "docs")


def generate_metrics_docs(out_dir: Path):
    """Generates docs for default metrics."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    metrics_template = env.get_template("metrics.md")

    for app_config in DEFINITIONS_DIR.iterdir():
        if app_config.suffix != ".toml":
            continue
        if app_config.name == "functions.toml":
            continue

        config = entity_from_path(app_config)
        metrics = [metric for _, metric in config.spec.metrics.definitions.items()]

        metrics_doc = out_dir / "metrics" / (app_config.stem + ".md")
        metrics_doc.parent.mkdir(parents=True, exist_ok=True)
        metrics_doc.write_text(
            metrics_template.render(
                metrics=metrics,
                platform=app_config.stem,
            )
        )


def generate_data_source_docs(out_dir: Path):
    """Generates docs for default data sources."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    data_sources_template = env.get_template("data_sources.md")

    for app_config in DEFINITIONS_DIR.iterdir():
        if app_config.suffix != ".toml":
            continue
        if app_config.name == "functions.toml":
            continue

        config = entity_from_path(app_config)
        data_sources = [
            data_source
            for _, data_source in config.spec.data_sources.definitions.items()
        ]

        data_sources_doc = out_dir / "data_sources" / (app_config.stem + ".md")
        data_sources_doc.parent.mkdir(parents=True, exist_ok=True)
        data_sources_doc.write_text(
            data_sources_template.render(
                data_sources=data_sources,
                platform=app_config.stem,
            )
        )


def generate_segment_docs(out_dir: Path):
    """Generate docs for existing segments."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    segments_template = env.get_template("segments.md")

    for app_config in DEFINITIONS_DIR.iterdir():
        if app_config.suffix != ".toml":
            continue
        if app_config.name == "functions.toml":
            continue

        config = entity_from_path(app_config)
        segments = [segment for _, segment in config.spec.segments.definitions.items()]
        if len(segments) == 0:
            continue

        segments_doc = out_dir / "segments" / (app_config.stem + ".md")
        segments_doc.parent.mkdir(parents=True, exist_ok=True)
        segments_doc.write_text(
            segments_template.render(
                segments=segments,
                platform=app_config.stem,
            )
        )


def generate_segment_data_sources_docs(out_dir: Path):
    """Generate docs for existing segment data sources."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    data_sources_template = env.get_template("segment_data_sources.md")

    for app_config in DEFINITIONS_DIR.iterdir():
        if app_config.suffix != ".toml":
            continue
        if app_config.name == "functions.toml":
            continue

        config = entity_from_path(app_config)
        data_sources = [
            segment for _, segment in config.spec.segments.data_sources.items()
        ]
        if len(data_sources) == 0:
            continue

        data_sources_doc = out_dir / "segment_data_sources" / (app_config.stem + ".md")
        data_sources_doc.parent.mkdir(parents=True, exist_ok=True)
        data_sources_doc.write_text(
            data_sources_template.render(
                data_sources=data_sources,
                platform=app_config.stem,
            )
        )


def generate_outcome_docs(out_dir: Path):
    """Generates docs for existing outcomes."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    outcome_template = env.get_template("outcome.md")

    for platform_dir in OUTCOME_DIR.iterdir():
        dummy_experiment = Experiment(
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
            app_name=platform_dir.name,
        )

        for outcome_file in platform_dir.glob("*.toml"):
            spec = AnalysisSpec.from_dict({})
            outcome_spec = OutcomeSpec.from_dict(toml.load(outcome_file))
            spec.merge_outcome(outcome_spec)
            conf = spec.resolve(dummy_experiment, _ConfigCollection)

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
                    summary.statistic.name
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


def generate_default_config_docs(out_dir: Path):
    """Generates docs for default configs."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    default_config_template = env.get_template("default_config.md")

    for default_config_file in DEFAULTS_DIR.glob("*.toml"):
        dummy_experiment = Experiment(
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
            app_name=default_config_file.stem,
        )

        spec = AnalysisSpec.from_dict(toml.load(default_config_file))
        conf = spec.resolve(dummy_experiment, _ConfigCollection)

        metric_summaries = [
            summary for _, summaries in conf.metrics.items() for summary in summaries
        ]

        metrics_analysis_periods = {}

        for period, summaries in conf.metrics.items():
            for summary in summaries:
                if summary.metric.name not in metrics_analysis_periods:
                    metrics_analysis_periods[summary.metric.name] = {
                        period.mozanalysis_label
                    }
                else:
                    metrics_analysis_periods[summary.metric.name].add(
                        period.mozanalysis_label
                    )

        # deduplicate metrics
        metrics = []
        for metric in metric_summaries:
            if metric.metric not in metrics:
                metrics.append(metric.metric)

        data_sources = {m.data_source for m in metrics}

        statistics_per_metric = {}
        for metric in metrics:
            statistics = [
                summary.statistic.name
                for summary in metric_summaries
                if summary.metric.name == metric.name
            ]
            statistics_per_metric[metric.name] = set(statistics)

        default_config_doc = (
            out_dir / "default_configs" / (default_config_file.stem + ".md")
        )
        default_config_doc.parent.mkdir(parents=True, exist_ok=True)
        default_config_doc.write_text(
            default_config_template.render(
                platform=default_config_file.stem,
                metrics=metrics,
                data_sources=data_sources,
                statistics=statistics_per_metric,
                metrics_analysis_periods=metrics_analysis_periods,
            )
        )


def generate_function_docs(out_dir):
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    functions_template = env.get_template("functions.md")

    function_defintions = toml.load(FUNCTIONS_FILE)
    functions = [
        {"name": function_name, "definition": f["definition"]}
        for function_name, f in function_defintions["functions"].items()
    ]

    functions_docs = out_dir / "functions.md"
    functions_docs.parent.mkdir(parents=True, exist_ok=True)
    functions_docs.write_text(functions_template.render(functions=functions))


if __name__ == "__main__":
    generate()
