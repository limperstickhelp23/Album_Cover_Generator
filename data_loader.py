import datasets

from datasets import load_dataset

dataset = load_dataset("imagefolder", data_dir ="album-mixed", drop_labels=True)

dataset.push_to_hub("rishthak/albums-mixed")