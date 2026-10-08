# Repository Structure

```text
data/              Derived analytical tables and compact data products.
gis/               Spatial outputs suitable for GitHub size limits.
tables/            Publication-support tables by module.
figures/           Figures, result visuals, and architecture visuals.
qc/                Quality-control, validation, and audit outputs.
metadata/          Data dictionaries, manifests, and provenance records.
code/              Code availability notes and future analysis scripts.
docs/              Methods, reproducibility notes, and known limitations.
external_data/     Datasets not directly tracked in Git.
```

The repository is not a full hard-drive backup. Large upstream data, raw HDF5 collections, large PBF files, redundant ZIP archives, and local working bundles are referenced through the external data manifest rather than committed as ordinary Git files.
