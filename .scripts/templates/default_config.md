Metrics and statistics that get computed for every `{{ platform }}` experiment.

[Source](https://github.com/mozilla/jetstream-config/blob/main/defaults/{{ platform }}.toml)  |  [Edit](https://github.com/mozilla/jetstream-config/edit/main/defaults/{{ platform }}.toml)

## Metrics

{% for metric in metrics %}

### `{{ metric.name }}` 

{% if metric.friendly_name %}**{{ metric.friendly_name }}**{% endif %}

{% if metric.description -%}
{{ metric.description | trim }}
{%- endif %}

Analysis Periods: {% for period in metrics_analysis_periods[metric.name] %} `{{ period }}` {% if not loop.last %}, {% endif %} {% endfor %}

Data Source: [`{{ metric.data_source.name }}`](#{{ metric.data_source.name }})

Statistics: {% for statistic in statistics[metric.name] %}`{{ statistic }}`{% if not loop.last %}, {% endif %}{% endfor %}

<details>
<summary>Definition:</summary>

```sql
{{ metric.select_expression | trim }}
```
</details>


---
{% endfor %}

{% if data_sources %}
## Data Sources

{% for datasource in data_sources %}

### [`{{ datasource.name }}` {%- if datasource.friendly_name -%}- {{ datasource.friendly_name }}{%- endif -%}](#{{ datasource.name }})

{% if datasource.description %}
{{ datasource.description | trim }}
{% endif %}

<details>
<summary>Definition:</summary>

```sql
{{ datasource._from_expr | trim }}
```
</details>

---
{% endfor %}
{% endif %}
