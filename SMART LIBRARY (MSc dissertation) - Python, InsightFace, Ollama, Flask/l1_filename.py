"""Filename parsing + canonical filename construction.

Three input shapes are recognized at ingest:

  1. DJI raw          DJI_YYYYMMDDHHMMSS_NNNN_D.MP4
  2. LosslessCut      <base>-HH.MM.SS.mmm-HH.MM.SS.mmm.MP4   (HHMMSS form)
                      <base>-segN.MP4                         (segN form)
  3. Anything else    recovered (no structured fields)

Canonical filename:  {YYYYMMDD}_{HHMMSS}_{shortid}[_{desc-slug}].MP4

Spec references: "Canonical naming contract", "Filename parsing (during normalize)".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

import l1_config as config

# ── Patterns ──────────────────────────────────────────────────────────────────
DJI_RAW_RE = re.compile(r"^DJI_(\d{14})_(\d+)_D", re.IGNORECASE)
LC_HHMMSS_RE = re.compile(
    r"^(?P<base>.+?)-(?P<start>\d{2}\.\d{2}\.\d{2}\.\d{3})-(?P<end>\d{2}\.\d{2}\.\d{2}\.\d{3})\.[Mm][Pp]4$"
)
LC_SEGN_RE = re.compile(r"^(?P<base>.+?)-seg(?P<n>\d+)\.[Mm][Pp]4$", re.IGNORECASE)
CANONICAL_RE = re.compile(
    r"^(?P<date>\d{8})_(?P<time>\d{6})_(?P<shortid>[0-9a-f]{6})(?:_(?P<slug>[a-z0-9-]+))?\.[Mm][Pp]4$",
    re.IGNORECASE,
)

# Filename shape labels
SHAPE_DJI_RAW = "dji_raw"
SHAPE_LC_HHMMSS = "lc_hhmmss"
SHAPE_LC_SEGN = "lc_segn"
SHAPE_CANONICAL = "canonical"
SHAPE_RECOVERED = "recovered"


@dataclass
class ParsedFilename:
    """Structured parse result for a clip filename.

    Fields populated depend on the shape; unfilled fields stay None.
    `cut_start_s` / `cut_end_s` are used during normalize only and not persisted.
    """

    shape: str
    original_filename: str
    is_cut: bool | None = None
    camera_brand: str | None = None
    camera_seq: int | None = None
    source_clip_name: str | None = None
    cut_start_s: float | None = None
    cut_end_s: float | None = None
    # Parsed from canonical filename (re-runs / already-canonical inputs)
    canonical_date: str | None = None      # YYYYMMDD
    canonical_time: str | None = None      # HHMMSS
    canonical_shortid: str | None = None
    canonical_slug: str | None = None


def classify(filename: str) -> str:
    """Return the shape label for a filename.

    Order matters: a LosslessCut cut of a DJI raw matches both DJI_RAW_RE and
    one of the LC patterns. The LC shape wins because the cut-ness is the more
    specific fact.
    """
    if CANONICAL_RE.match(filename):
        return SHAPE_CANONICAL
    if LC_HHMMSS_RE.match(filename):
        return SHAPE_LC_HHMMSS
    if LC_SEGN_RE.match(filename):
        return SHAPE_LC_SEGN
    if DJI_RAW_RE.match(filename):
        return SHAPE_DJI_RAW
    return SHAPE_RECOVERED


def _hhmmss_ms_to_seconds(token: str) -> float:
    """Convert "HH.MM.SS.mmm" → seconds (float)."""
    parts = token.split(".")
    if len(parts) != 4:
        raise ValueError(f"bad HH.MM.SS.mmm token: {token!r}")
    h, m, s, ms = parts
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse(filename: str) -> ParsedFilename:
    """Parse a filename into structured metadata. Never raises on unknown shapes."""
    shape = classify(filename)

    if shape == SHAPE_CANONICAL:
        m = CANONICAL_RE.match(filename)
        assert m is not None
        return ParsedFilename(
            shape=shape,
            original_filename=filename,
            canonical_date=m.group("date"),
            canonical_time=m.group("time"),
            canonical_shortid=m.group("shortid").lower(),
            canonical_slug=m.group("slug"),
        )

    if shape == SHAPE_LC_HHMMSS:
        m = LC_HHMMSS_RE.match(filename)
        assert m is not None
        try:
            start_s = _hhmmss_ms_to_seconds(m.group("start"))
            end_s = _hhmmss_ms_to_seconds(m.group("end"))
        except ValueError:
            start_s = end_s = None
        base = m.group("base")
        # Guess source extension — the cut is always .MP4, source is typically
        # the same. Spec stores `source_clip_name` as a filename (with ext).
        source_name = f"{base}.MP4"
        out = ParsedFilename(
            shape=shape,
            original_filename=filename,
            is_cut=True,
            source_clip_name=source_name,
            cut_start_s=start_s,
            cut_end_s=end_s,
        )
        # If the base is itself a DJI raw stem, also recover camera fields.
        dji_m = DJI_RAW_RE.match(base + ".MP4")
        if dji_m:
            out.camera_brand = "DJI"
            try:
                out.camera_seq = int(dji_m.group(2))
            except ValueError:
                pass
        return out

    if shape == SHAPE_LC_SEGN:
        m = LC_SEGN_RE.match(filename)
        assert m is not None
        base = m.group("base")
        source_name = f"{base}.MP4"
        out = ParsedFilename(
            shape=shape,
            original_filename=filename,
            is_cut=True,
            source_clip_name=source_name,
        )
        dji_m = DJI_RAW_RE.match(base + ".MP4")
        if dji_m:
            out.camera_brand = "DJI"
            try:
                out.camera_seq = int(dji_m.group(2))
            except ValueError:
                pass
        return out

    if shape == SHAPE_DJI_RAW:
        m = DJI_RAW_RE.match(filename)
        assert m is not None
        try:
            seq = int(m.group(2))
        except ValueError:
            seq = None
        return ParsedFilename(
            shape=shape,
            original_filename=filename,
            is_cut=False,
            camera_brand="DJI",
            camera_seq=seq,
        )

    # SHAPE_RECOVERED
    return ParsedFilename(
        shape=shape,
        original_filename=filename,
        is_cut=None,
    )


def dji_filename_local_datetime(filename: str) -> datetime | None:
    """Parse the YYYYMMDDHHMMSS embedded in a DJI raw filename as a naive
    (camera-local) datetime. Returns None if the filename is not DJI-shaped or
    the timestamp is not parseable. Used as a low-confidence fallback when the
    container `creation_time` is unreadable.
    """
    m = DJI_RAW_RE.match(filename)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%d%H%M%S")
    except ValueError:
        return None


def build_canonical(date_str: str, time_str: str, shortid: str, desc_slug: str | None = None) -> str:
    """Construct a canonical filename.

    Args:
      date_str:  "YYYYMMDD"
      time_str:  "HHMMSS"
      shortid:   first SHORTID_LEN hex chars of clip_id
      desc_slug: optional, already slugified (call `identity.slugify()` first)
    """
    if not (len(date_str) == 8 and date_str.isdigit()):
        raise ValueError(f"bad date_str: {date_str!r}")
    if not (len(time_str) == 6 and time_str.isdigit()):
        raise ValueError(f"bad time_str: {time_str!r}")
    if not (len(shortid) == config.SHORTID_LEN and all(c in "0123456789abcdef" for c in shortid.lower())):
        raise ValueError(f"bad shortid: {shortid!r}")
    stem = f"{date_str}_{time_str}_{shortid.lower()}"
    if desc_slug:
        stem = f"{stem}_{desc_slug}"
    return f"{stem}.MP4"


def canonical_parts_from_datetime(dt: datetime) -> tuple[str, str]:
    """Return (YYYYMMDD, HHMMSS) strings for a datetime."""
    return dt.strftime("%Y%m%d"), dt.strftime("%H%M%S")
