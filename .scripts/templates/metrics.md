Pre-defined metrics for `{{ platform }}` that can be used across all experiments. These metrics are defined in [jetstream-config](https://github.com/mozilla/jetstream-config/blob/main/definitions/{{ platform }}.toml)

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
{{ metric.select_expression | trim }}
```
</details>

---

{% endfor %}
