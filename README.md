# pensieve-config

Custom configs for experiments analyzed in [pensieve](https://github.com/mozilla/pensieve). 

## Adding Custom Configurations

Custom configuration files must be written in the [TOML file format](https://github.com/toml-lang/toml) and must follow the specification defined in [Configuring mozanalysis](https://docs.google.com/document/d/1rEpmUUtfN1f3xWKe3G0GI7ek2fq49W99-Li3YTtnH68).
The name of the configuration file must match the **Normandy slug** of the experiment it is targeting.

A new pull-request needs to be opened for new or updated configuration files. The pull-request can be merged after CI checks verify that the provided configuration files are valid.

Once new config files are pushed, pensieve will automatically re-run the analysis for affected experiments.
