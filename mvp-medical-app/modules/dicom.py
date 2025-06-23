from __future__ import annotations

from pathlib import Path
from typing import List

import pydicom
from pydicom.dataset import FileDataset


def load_series(directory: str | Path) -> List[FileDataset]:
    """Load all DICOM files in a directory."""
    path = Path(directory)
    datasets = []
    for f in sorted(path.glob("*.dcm")):
        datasets.append(pydicom.dcmread(str(f)))
    return datasets


def save_series(directory: str | Path, datasets: List[FileDataset]) -> None:
    """Save a list of DICOM datasets into a directory."""
    dest = Path(directory)
    dest.mkdir(parents=True, exist_ok=True)
    for i, ds in enumerate(datasets):
        ds.save_as(dest / f"{i:04d}.dcm")


