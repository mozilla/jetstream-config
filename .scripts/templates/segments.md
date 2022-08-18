Pre-defined segments for `{{ platform }}` that can be used across all experiments. These segments are defined in [mozanalysis](https://github.com/mozilla/mozanalysis/tree/main/src/mozanalysis/metrics)

{% for segment in segments %}
## {{ segment.name }}

{% if segment.friendly_name %}
**{{ segment.friendly_name }}**
{% endif %}

{% if segment.description -%}
{{ segment.description | trim }}
{%- endif %}

Data Source: [`{{ segment.data_source.name }}`](https://mozilla.github.io/jetstream-config/data_sources/{{ platform }}/#{{ segment.data_source.name }})

<details>
<summary>Definition:</summary>

```sql
{{ segment.select_expression | trim }}
```
</details>

---

{% endfor %}
