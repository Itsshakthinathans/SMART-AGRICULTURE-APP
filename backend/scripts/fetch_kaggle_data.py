import os
import shutil
import zipfile
from pathlib import Path

import kaggle

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_and_extract(dataset: str, out_zip: Path, extract_to: Path):
    print(f"Downloading {dataset} ...")
    kaggle.api.dataset_download_files(dataset, path=str(out_zip.parent), quiet=False)

    guessed_zip = out_zip.parent / (dataset.split("/")[-1] + ".zip")
    if guessed_zip.exists() and guessed_zip != out_zip:
        shutil.move(str(guessed_zip), str(out_zip))

    print(f"Extracting {out_zip} -> {extract_to}")
    extract_to.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "r") as zf:
        zf.extractall(str(extract_to))


def main():
    crop_zip = DATA_DIR / "crop-recommendation-dataset.zip"
    disease_zip = DATA_DIR / "plantdisease.zip"

    download_and_extract("atharvaingle/crop-recommendation-dataset", crop_zip, DATA_DIR)
    download_and_extract("emmarex/plantdisease", disease_zip, DATA_DIR / "plantvillage_raw")

    print("Done. Move/rename extracted disease classes into backend/data/plantvillage if needed.")


if __name__ == "__main__":
    main()
