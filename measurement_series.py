"""Read-only reconstruction of recorded columnar measurements for safe charting.

A source group can contain several distinct observations for one timestamp.
Series identity may be in per-row dimension_5qi, dimension_cause or
other dimension columns rather than in group-level static metadata.
Never join such observations into a single line and never aggregate silently.
"""
import json
from collections import Counter
import pandas as pd


def _value(v):
    if v is None: return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True, separators=(',', ':'))
    return str(v)


def measurement_frame(group):
    """Return all source rows with all per-row columns; no aggregation or sampling."""
    timestamps = group.get('timestamps') or []
    n = len(timestamps)
    data = {'interval_start_utc': list(timestamps)}
    for key, vals in (group.get('series') or {}).items():
        if isinstance(vals, list):
            if len(vals) != n:
                raise ValueError(f'Invalid source column length: {key}: {len(vals)} != {n}')
            data[key] = list(vals)
    # Source may store one value as static when invariant across all rows.
    static = group.get('static') or {}
    for key in ('value_int', 'value_float', 'value_bool', 'value_text'):
        if key not in data and static.get(key) is not None:
            data[key] = [static[key]] * n
    return pd.DataFrame(data)


def _dimensions(row, static):
    dims = {}
    for obj in (static, row):
        for key, value in obj.items():
            if key.startswith('dimension_') and value is not None and str(value).strip():
                k = key[10:].lower()
                v = _value(value)
                if k in dims and dims[k] != v:
                    raise ValueError(f'Conflicting recorded dimension values for {k}')
                dims[k] = v
        value = obj.get('dimensions_json')
        if value:
            try:
                decoded = json.loads(value) if isinstance(value, str) else value
            except (json.JSONDecodeError, TypeError):
                decoded = {'raw_dimensions_json': _value(value)}
            if isinstance(decoded, dict):
                for k, v in decoded.items():
                    if v is not None and str(v).strip():
                        normalized = str(k).lower()
                        converted = _value(v)
                        if normalized in dims and dims[normalized] != converted:
                            raise ValueError(f'Conflicting recorded dimension values for {normalized}')
                        dims[normalized] = converted
    # Names "5QI" and "5qi" map to the same normalized identity key.
    return tuple(sorted((k.lower(), str(v)) for k, v in dims.items()))


def _label(key):
    if not key:return 'Undimensioned observations'
    friendly = {'5qi':'5QI', 'cause':'Cause', 'snssai':'S-NSSAI'}
    return ' · '.join(f'{friendly.get(k,k)} {v}' for k,v in key)


def partition_measurements(group):
    """Return source frame, identities and chart-safety map for every source row.

    Duplicate timestamps within one fully identified series are *not* guessed
    away: that subset is flagged unsafe until source identity is resolved.
    """
    frame = measurement_frame(group)
    static = group.get('static') or {}
    keys = [_dimensions(row, static) for row in frame.to_dict('records')]
    # No index coercion (avoids indistinguishable pandas MultiIndex tuples).
    identities = {}
    for idx, key in enumerate(keys):
        identities.setdefault(key, []).append(idx)
    partitions = []
    for key, indices in sorted(identities.items(), key=lambda x: _label(x[0])):
        part = frame.iloc[indices].copy().reset_index(drop=True)
        counts = Counter(part['interval_start_utc'].tolist())
        duplicates = {k:v for k,v in counts.items() if v > 1}
        partitions.append({'key':key,'label':_label(key),'frame':part,
                           'safe_to_plot':not duplicates, 'duplicate_timestamps':duplicates})
    return frame, partitions
