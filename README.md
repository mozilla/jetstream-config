# jetstream-config

Custom configs for experiments analyzed in [jetstream](https://github.com/mozilla/jetstream). 

## Adding Custom Configurations

Custom configuration files are written in [TOML](https://toml.io/en/).
The name of the configuration file must match the **Normandy slug** of the experiment it is targeting.

To add or update a custom configuration, open a pull request. CI checks will verify your configuration.
Once CI completes, you may merge the pull request, which will trigger Jetstream to re-run your analysis.

## Example configuration and syntax

Configuration files have three main sections:
`[experiment]`, `[metrics]`, and `[data_sources]`.

Examples of every value you can specify in each section are given below.
You do not need to specify everything!
Jetstream will take values from Experimenter
and combine them with a reasonable set of defaults.

You should name the file according to the experiment's Normandy slug,
like `bug_12345_my_cool_experiment.toml`.

Lines starting with a `#` are comments and have no effect.

### Experiment section

This part of the configuration file lets you override the values in Experimenter.
Most of the time, you will not have to specify anything here.

```toml
[experiment]
# Nominal length of the enrollment period in days.
# Mozanalysis will consider enrollment_period + 1 "dates" of enrollments.
enrollment_period = 7

# The name of the control branch.
# To compare all branches to each other pairwise, use the value `nan`.
reference_branch = "control"

# Override the "enrollment query" mozanalysis will use.
# See https://github.com/mozilla/mozanalysis/issues/93 for more details about
# what the query needs to contain.
# Jetstream interprets this as a Jinja2 template; an `experiment` object is provided
# that lets you access other details from Experimenter, like a slug.
enrollment_query = """
  SELECT
      client_id,
      branch,
      enrollment_date,
      num_enrollments
  FROM `moz-fx-data-shared-prod`.some_table.name_here
  WHERE
      DATE(submission_timestamp) BETWEEN {{experiment.start_date}} AND {{experiment.enrollment_end}}
      AND mozfun.map.get_key(environment.experiments, "{{experiment.slug}}") IS NOT NULL
"""
```

### Metrics section

The metrics section allows you to specify and define the metrics that you're collecting,
the statistical summaries that you'd like applied to them, and any filters that you need.
See DTMO for more details on the analysis window concept.

You can use the names of metrics defined in mozanalysis without redefining them.

```toml
[metrics]
# Metrics to compute for each daily analysis window.
# Defined as a list of strings. The string should be the "slug" of the metric,
# which is the name of the Metric object defined in mozanalysis, or the name
# of the metric definition section in this config file (see below).
daily = []

# Metrics to compute for each weekly analysis window.
weekly = ["uri_count", "retained"]

# Metrics to compute only for the overall analysis window.
overall = ["uri_count", "search_count"]
```

### Defining metrics

You can define a new metric by adding a new section with a name like

`[metrics.<new_metric_slug>]`

For example, you could define a new metric based on a scalar named
`browser.engagement.cows_clicked` this way:

```toml
[metrics.ever_clicked_cows]
# A clause of a SELECT expression. The expression must contain an aggregation function.
# The expression is evaluated with `GROUP BY client_id, branch` over an analysis window.
# Interpreted as a Jinja2 template. The mozanalysis helper functions are available,
# so you could equivalently write the expression below like:
# select_expression = "{{agg_sum("payload.processes.parent.scalars.browser_engagment_cows_clicked")}} > 0"
# See https://mozilla.github.io/mozanalysis/api/metrics.html for details.
select_expression = "SUM(COALESCE(payload.processes.parent.scalars.browser_engagement_cows_clicked)) > 0"

# The data source to use. You can use the slug of a data source defined in mozanalysis,
# or else define a new data source below.
data_source = "main"
```

You should also add some sections to describe how your new metrics should be summarized for reporting.
You can do this by adding a statistics section to the metric for the statistic you want.

There is a list of statistics in the Jetstream wiki.

This looks like:

```toml
[metrics.ever_clicked_cows.statistics.binomial]
# Sometimes it's useful to specify a "pre-treatment" to drop extreme values
# or perform a transformation. There is a list of these in the Jetstream wiki.
pre_treatments = []

# You can also change the default width of the confidence interval.
ci_width = 0.95
```


To put it all together, the metrics section (without any comments) for this probe could look like:

```toml
[metrics]
weekly = ["ever_clicked_cows"]

[metrics.ever_clicked_cows]
select_expression = "SUM(COALESCE(payload.processes.parent.scalars.browser_engagement_cows_clicked)) > 0"
data_source = "main"

[metrics.ever_clicked_cows.statistics.binomial]
```

### Defining data sources

Most of the regular data sources are already defined in mozanalysis,
but you can define a new one in a similar way to how new metrics are defined.

Add a section that looks like:

```toml
[data_sources.my_cool_data_source]
# FROM expression - often just a fully-qualified table name. Sometimes a subquery.
from_expression = "(SELECT client_id, experiments, submission_date FROM my_cool_table)"

# See https://mozilla.github.io/mozanalysis/api/metrics.html#mozanalysis.metrics.DataSource for details.
experiments_column_type = "native"
```

Then, your new metric can refer to it like `data_source = "my_cool_data_source"`.
