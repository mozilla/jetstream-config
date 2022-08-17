Pre-defined functions that can be used in select expressions across all metrics and segment definitions. These functions are defined in [jetstream-config](https://github.com/mozilla/jetstream-config/blob/main/definitions/functions.toml)

{% for function in functions %}
## {{ function.name }}

<details>
<summary>Definition:</summary>

```sql
{{ function.definition | trim }}
```
</details>

---

{% endfor %}
