"""
Restore diff — pre/post DB snapshots + row-level diff for the restore report.

Why
---
The restore engine already replays each component's PostgreSQL rows from
`component_db.json` (see `component_db.py`). But until now the operator
only sees "5 rules restored" — they cannot tell which specific firewall
rule was deleted, which ZTNA identity reappeared, or which NAT entry the
restore overwrote. That's the gap this module fills.

Strategy
--------
1. **Pre-snapshot** : just before the restore touches the DB, dump the
   *current* state of every component model into an in-memory dict keyed
   by primary key. This is the "before" picture.
2. **Post-snapshot** : right after the restore finishes, take the same
   dump again. This is the "after" picture.
3. **Diff**          : per model, classify each PK as added / removed /
   modified and pick a small set of human-readable fields ("summary") so
   the UI can render "Règle #42 'block_ssh' supprimée" instead of just
   "pk=42".

Design notes
------------
- Reuses `component_db.COMPONENT_MODELS` and `MODEL_LABELS` — no second
  source of truth. The diff is computed for the same set of models the
  backup/restore engine already knows about.
- Pure read-only at snapshot time — never mutates the DB.
- Tolerant of failures: a single broken model never aborts the diff;
  it just gets skipped with an entry in `errors`.
- Summary fields are picked from a curated list of "identifying" model
  field names (name, label, description, daddr, dport, …). If none
  match, falls back to listing all small scalar fields.
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

# Field names worth showing the operator when summarising a row. Tried
# in order; the first that exists on the model wins. Kept short on
# purpose — the UI prints a chip per row.
_PREFERRED_SUMMARY_FIELDS = (
    "name", "label", "title", "description", "rule_description",
    "username", "user", "ifname", "name_interface",
    "rule", "type_rule", "policy",
    "saddr", "daddr", "dport", "sport",
    "destination", "source",
    "subnet", "network",
    "common_name", "cn",
)

# Fields we never want to display (noisy / secret / huge).
_EXCLUDED_SUMMARY_FIELDS = {
    "password", "passwd", "secret", "token", "private_key", "key",
    "config_text", "blob", "content",
}


def _model_field_names(Model) -> list[str]:
    try:
        return [f.name for f in Model._meta.concrete_fields]
    except Exception:
        return []


def _row_to_dict(instance, field_names: list[str]) -> dict:
    """Serialise an ORM instance to a plain dict of scalar field values.
    Keeps FKs as their PK (Django's `*_id` attribute). Skips obvious
    binary / huge fields. Pure best-effort — wrapped in try/except by
    the caller."""
    out: dict = {}
    for name in field_names:
        if name in _EXCLUDED_SUMMARY_FIELDS:
            continue
        try:
            val = getattr(instance, name, None)
        except Exception:
            continue
        if val is None:
            out[name] = None
            continue
        if isinstance(val, (str, int, float, bool)):
            # Truncate long strings — restore reports get rendered in a
            # modal, not a terminal; 200 chars is plenty for an identifier.
            if isinstance(val, str) and len(val) > 200:
                val = val[:200] + "…"
            out[name] = val
        else:
            # Dates, decimals, FKs (already covered by _id) — stringify.
            try:
                out[name] = str(val)[:200]
            except Exception:
                pass
    return out


def _pick_summary(row: dict, field_names: list[str]) -> str:
    """Produce a one-line human label for a row, used as the chip text."""
    for cand in _PREFERRED_SUMMARY_FIELDS:
        if cand in row and row[cand] not in (None, ""):
            return f"{cand}={row[cand]}"
    # Fallback: first 3 non-empty scalar values.
    parts = []
    for fname in field_names:
        if fname in row and row[fname] not in (None, "") and fname != "id":
            parts.append(f"{fname}={row[fname]}")
            if len(parts) >= 3:
                break
    return ", ".join(parts) or "(row)"


def snapshot_db_state(components: list[str]) -> dict:
    """Capture the current rows of every model declared for `components`.

    Returns a dict shaped like::

        {
          "nat": {
            "nat.DNat": {
              "label": "NAT DNAT",
              "rows": {
                "1": {"id":1, "daddr":"10.0.0.5", "dport":"443", ...},
                "7": {...},
              },
            },
            ...
          },
          ...
        }

    Never raises — broken models are skipped with a log warning.
    """
    from backend.backup.component_db import COMPONENT_MODELS, MODEL_LABELS, _resolve_model

    out: dict = {}
    for component in components:
        models = COMPONENT_MODELS.get(component)
        if not models:
            continue
        comp_dump: dict = {}
        for path in models:
            Model = _resolve_model(path)
            if Model is None:
                continue
            field_names = _model_field_names(Model)
            try:
                rows: dict = {}
                for instance in Model.objects.all():
                    pk = getattr(instance, "pk", None)
                    if pk is None:
                        continue
                    rows[str(pk)] = _row_to_dict(instance, field_names)
                comp_dump[path] = {
                    "label": MODEL_LABELS.get(path, path),
                    "rows": rows,
                    "field_names": field_names,
                }
            except Exception as exc:
                logger.warning("restore_diff: snapshot failed for %s (%s)", path, exc)
        if comp_dump:
            out[component] = comp_dump
    return out


def _diff_model(model_path: str, pre_model: dict, post_model: dict) -> dict:
    """Compute added / removed / modified rows for one model.
    Both `pre_model` and `post_model` follow the `snapshot_db_state` shape
    for a single model: ``{"label": str, "rows": {pk: {...}}, "field_names": [...]}``.
    Missing-side defaults to empty so this works for "model only present
    pre" or "only present post" cases too.
    """
    pre_rows = (pre_model or {}).get("rows", {}) or {}
    post_rows = (post_model or {}).get("rows", {}) or {}
    field_names = (
        (post_model or {}).get("field_names")
        or (pre_model or {}).get("field_names")
        or list({*pre_rows.keys(), *post_rows.keys()})
    )

    pre_pks = set(pre_rows.keys())
    post_pks = set(post_rows.keys())

    added_pks = sorted(post_pks - pre_pks)
    removed_pks = sorted(pre_pks - post_pks)
    common_pks = pre_pks & post_pks

    added = []
    for pk in added_pks:
        row = post_rows[pk]
        added.append({
            "pk": pk,
            "summary": _pick_summary(row, field_names),
            "row": row,
        })

    removed = []
    for pk in removed_pks:
        row = pre_rows[pk]
        removed.append({
            "pk": pk,
            "summary": _pick_summary(row, field_names),
            "row": row,
        })

    modified = []
    for pk in sorted(common_pks):
        before = pre_rows[pk]
        after = post_rows[pk]
        changed_fields = {}
        for fname in set(before) | set(after):
            if before.get(fname) != after.get(fname):
                changed_fields[fname] = {
                    "before": before.get(fname),
                    "after": after.get(fname),
                }
        if changed_fields:
            modified.append({
                "pk": pk,
                "summary": _pick_summary(after, field_names),
                "changes": changed_fields,
            })

    return {
        "label": (post_model or pre_model or {}).get("label", model_path),
        "pre_count": len(pre_rows),
        "post_count": len(post_rows),
        "added": added,
        "removed": removed,
        "modified": modified,
    }


def diff_db_states(pre: dict, post: dict) -> dict:
    """Compute the per-component diff between two `snapshot_db_state`
    dumps. Returns a structure ready to be persisted in the restore job
    state file and consumed by the frontend report panel.
    """
    components = sorted(set(pre or {}) | set(post or {}))
    out_components: dict = {}
    tot_added = tot_removed = tot_modified = 0

    for component in components:
        pre_comp = (pre or {}).get(component) or {}
        post_comp = (post or {}).get(component) or {}
        model_paths = sorted(set(pre_comp) | set(post_comp))
        models_diff = {}
        c_added = c_removed = c_modified = 0
        for path in model_paths:
            d = _diff_model(path, pre_comp.get(path), post_comp.get(path))
            # Don't waste payload on models with zero changes — the UI
            # would just render an empty section. Keep them in the
            # summary count though (post_count) so totals stay accurate.
            if d["added"] or d["removed"] or d["modified"]:
                models_diff[path] = d
            c_added += len(d["added"])
            c_removed += len(d["removed"])
            c_modified += len(d["modified"])
        if models_diff:
            out_components[component] = {
                "models": models_diff,
                "summary": {
                    "added": c_added,
                    "removed": c_removed,
                    "modified": c_modified,
                },
            }
        tot_added += c_added
        tot_removed += c_removed
        tot_modified += c_modified

    return {
        "components": out_components,
        "totals": {
            "added": tot_added,
            "removed": tot_removed,
            "modified": tot_modified,
            "changed_components": len(out_components),
        },
    }
