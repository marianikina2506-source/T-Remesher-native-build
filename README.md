# T-Remesher Native Backend

Build repository for the experimental **T-Remesher 0.8 Native Density** backend.

This repository patches GPL-3.0 `cgg-bern/quadwild-bimdf` so `quad_from_patches` can accept a per-patch density multiplier file instead of using one global target edge size for every patch.

## Density file format

```text
PATCH_COUNT
multiplier_patch_0
multiplier_patch_1
...
```

- `< 1.0` → smaller target edge / more quads
- `1.0` → default target edge
- `> 1.0` → larger target edge / fewer quads

The Windows GitHub Actions workflow checks out upstream QuadWild Bi-MDF, applies the T-Remesher patch, builds `quad_from_patches.exe`, and uploads the runtime as an artifact.

## License

Patch and integration code: GPL-3.0-or-later. Upstream QuadWild Bi-MDF: GPL-3.0.
