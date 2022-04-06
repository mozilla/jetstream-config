Pre-defined metrics for `{{ platform }}` that can be used across all experiments. These metrics are defined in [mozanalysis](https://github.com/mozilla/mozanalysis/tree/main/src/mozanalysis/metrics)

{% for metric in metrics %}
## {{ metric.name }}

{% if metric.friendly_name %}
**{{ metric.friendly_name }}**
{% endif %}

{% if metric.description -%}
{{ metric.description | trim }}
{%- endif %}

Data Source: [`{{ metric.data_source.name }}`](https://mozilla.github.io/jetstream-config/data_sources/{{ platform }}/#{{ metric.data_source.name }})

<details>
<summary>Definition:</summary>

```sql
{{ metric.select_expr | trim }}
```
</details>

{% endfor %}
