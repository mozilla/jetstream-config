Pre-defined data sources for `{{ platform }}` that can be used across all experiments. These data sources are defined in [mozanalysis](https://github.com/mozilla/mozanalysis/tree/main/src/mozanalysis/metrics)

{% for datasource in datasources %}
## [{{ datasource.name }}](#{{ datasource.name }})

Client ID column: `{{ datasource.client_id_column }}`

Submission Date column: ``{{ datasource.submission_date_column }}``

<details>
<summary>Definition:</summary>

```sql
{{ datasource._from_expr | trim }}
```
</details>

---
{% endfor %}
