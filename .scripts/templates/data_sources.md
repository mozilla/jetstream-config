Pre-defined data sources for `{{ platform }}` that can be used across all experiments. These data sources are defined in [jetstream-config](https://github.com/mozilla/jetstream-config/blob/main/definitions/{{ platform }}.toml)

{% for data_source in data_sources %}
## [{{ data_source.name }}](#{{ data_source.name }})

Client ID column: `{{ data_source.client_id_column }}`

Submission Date column: ``{{ data_source.submission_date_column }}``

<details>
<summary>Definition:</summary>

```sql
{{ data_source.from_expression | trim }}
```
</details>

---
{% endfor %}
