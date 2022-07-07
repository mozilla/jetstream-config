"""Generates documentation for outcomes and default metrics and datasets."""

from argparse import ArgumentParser
from os import stat_result
import statistics
from mozanalysis.metrics import Metric, DataSource
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

    generate_metrics_docs(out_dir / "docs")
    generate_datasource_docs(out_dir / "docs")
    generate_outcome_docs(out_dir / "docs")
    generate_default_config_docs(out_dir / "docs")


def generate_metrics_docs(out_dir: Path):
    """Generates docs for default metrics."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    metrics_template = env.get_template("metrics.md")

    for app_name, platform in config.PLATFORM_CONFIGS.items():
        metric_names = [
            metric
            for metric in dir(platform.metrics_module)
            if not metric.startswith("__")
            and metric != "Metric"
            and metric != "DataSource"
        ]
        metrics = [getattr(platform.metrics_module, metric) for metric in metric_names]
        metrics = [metric for metric in metrics if isinstance(metric, Metric)]

        metrics_doc = out_dir / "metrics" / (app_name + ".md")
        metrics_doc.parent.mkdir(parents=True, exist_ok=True)
        metrics_doc.write_text(
            metrics_template.render(
                metrics=metrics,
                platform=app_name,
            )
        )


def generate_datasource_docs(out_dir: Path):
    """Generates docs for default data sources."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    datasources_template = env.get_template("datasources.md")

    for app_name, platform in config.PLATFORM_CONFIGS.items():
        datasource_names = [
            datasource
            for datasource in dir(platform.metrics_module)
            if not datasource.startswith("__")
            and datasource != "Metric"
            and datasource != "DataSource"
        ]
        datasources = [
            getattr(platform.metrics_module, datasource)
            for datasource in datasource_names
        ]
        datasources = [
            datasource
            for datasource in datasources
            if isinstance(datasource, DataSource)
        ]

        datasources_doc = out_dir / "data_sources" / (app_name + ".md")
        datasources_doc.parent.mkdir(parents=True, exist_ok=True)
        datasources_doc.write_text(
            datasources_template.render(
                datasources=datasources,
                platform=app_name,
            )
        )


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


def generate_default_config_docs(out_dir: Path):
    """Generates docs for default configs."""
    file_loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=file_loader)
    default_config_template = env.get_template("default_config.md")

    for default_config_file in DEFAULTS_DIR.glob("*.toml"):
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
            app_id=config.PLATFORM_CONFIGS[default_config_file.stem].app_id
            if default_config_file.stem in config.PLATFORM_CONFIGS
            else "firefox_desktop",
            app_name=default_config_file.stem,
        )

        spec = config.AnalysisSpec.from_dict(toml.load(default_config_file))
        conf = spec.resolve(dummy_experiment)

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
                summary.statistic.name()
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


if __name__ == "__main__":
    generate()
