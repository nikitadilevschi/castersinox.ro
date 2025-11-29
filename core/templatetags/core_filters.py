# python
# File: `core/templatetags/core_filters.py`
import ast
import re
from django import template

register = template.Library()

def _strip_quotes(s):
    return s.strip().strip("'\" ")

@register.filter
def parse_features(value):
    """
    Parse product.features into a list of dicts: [{'k': key, 'v': value}, ...]
    Handles Python-list string, newline separated, or comma separated input.
    If a line has no ':' then the whole line becomes `k` and `v` is ''.
    """
    if not value:
        return []

    # If already a list/tuple, use it directly
    if isinstance(value, (list, tuple)):
        seq = value
    else:
        s = str(value).strip()
        seq = None
        try:
            if s.startswith('[') and s.endswith(']'):
                parsed = ast.literal_eval(s)
                seq = parsed if isinstance(parsed, (list, tuple)) else [s]
            else:
                if '\n' in s:
                    seq = s.splitlines()
                else:
                    seq = re.split(r'\s*,\s*', s) if ',' in s else [s]
        except Exception:
            seq = s.splitlines()

    out = []
    for item in seq:
        if item is None:
            continue
        it = _strip_quotes(str(item))
        if not it:
            continue
        if ':' in it:
            k, v = it.split(':', 1)
            k = k.strip()
            v = v.strip()
        else:
            k = it.strip()
            v = ''
        out.append({'k': k, 'v': v})
    return out

@register.filter
def has_any_value(parsed_list):
    """
    Expect a list returned by parse_features (list of dicts with 'k' and 'v').
    Return True if at least one item has a non-empty 'v'.
    Also tolerates raw strings or lists of strings.
    """
    if not parsed_list:
        return False

    # If it's a string or list of strings, parse it first
    if isinstance(parsed_list, (str,)):
        parsed = parse_features(parsed_list)
    else:
        parsed = parsed_list

    if isinstance(parsed, (list, tuple)):
        for item in parsed:
            if isinstance(item, dict):
                if item.get('v'):
                    return True
            else:
                # fallback: treat item as raw string
                it = _strip_quotes(str(item))
                if ':' in it:
                    v = it.split(':', 1)[1].strip()
                    if v:
                        return True
    return False


