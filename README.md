# Lab 04: Indexing and Retrieval — student workbook

Open `Lab04_Students.ipynb`. Complete exercises E1–E8 and the written responses. This edition contains intentional `NotImplementedError` gaps, hints, and unchanged tests; it contains no instructor solution cells or teacher notes. The initial status table is incomplete by design. The saved index is created after the required exercises are completed.

## Opening the lab

Extract the entire ZIP to a short local path, such as `Documents/Lab04`. Do not run the notebook from inside a ZIP preview. Keep the notebook, `lab_support.py`, and `data` folder together.

Use Python 3.10 or later. Install the dependencies in the environment used by the notebook kernel:

```bash
python -m pip install -r requirements.txt
python -m jupyter lab
```

In Anaconda, run these commands in the prompt for the selected environment. If packages are installed but imports fail, check that the notebook is using that environment's Python kernel. The validated environment used Python 3.13, NLTK 3.9.2, Beautiful Soup 4.14.3, and Requests 2.32.5. Other environments were not separately tested.

After packages are installed, all required exercises run offline. No NLTK corpus download, Selenium browser, account, or API key is needed. The HTML reading copy also opens offline, with mathematics already rendered. It is not an editable or executable notebook.

## Contents

- The `.ipynb` file is the editable notebook.
- The `.html` file is a read-only rendering of that edition.
- `lab_support.py` provides checks, snapshot loading, index validation, and JSON persistence; exercise algorithms remain in the notebook.
- `live_fetch.py` is an optional bounded HTTP adapter. The live example is commented out, and real network behavior is not part of validation.
- `requirements.txt` lists dependencies.
- `data/manifest.json` maps short local filenames to canonical URLs, original filenames, and checksums.
- `data/docs_collection` preserves 100 main snapshots; `data/test_collection` preserves 28 additional snapshots, including the empty file.

## Data and reproducibility

All 128 source HTML byte streams are preserved without edits. The filenames are shortened to avoid long-path problems; the original names remain in the manifest. The two sets contain overlapping content and duplicate canonical URLs. The second collection is not a held-out relevance benchmark.

The main build keeps the first snapshot for each normalized canonical URL, then applies the stated URL, extraction, and preprocessing policy. In the validated run, its 100 files yield 76 indexed documents: 4 duplicate URLs, 5 rejected URLs, and 15 unsupported article extractions are excluded. The test collection yields 21 indexed documents. These are historical pages, not current news; some original subject matter is sensitive.

The default URL policy accepts only the exact `https://www.nbcnews.com` origin. Five main snapshots have canonical URLs outside that policy. They remain in the package and are counted as rejected, not silently discarded.

Saving creates `outputs/saved_index` with the three dictionaries and metadata. Read and write access to the extracted directory is required. Do not change the saved JSON to force a check to pass. Rebuild after changing the analysis policy.

## Troubleshooting

**INCOMPLETE or BLOCKED:** these labels indicate unfinished exercises or missing prerequisites, not passing tests. Implement the specified methods, then restart and run all cells.

**An old implementation still seems active:** class definitions do not update existing instances. Restart the kernel and run from the top.

**A path or import cannot be found:** extract the complete ZIP and keep the supplied folder structure. Start Jupyter from the extracted folder.

**An equation appears as LaTeX text:** run the Markdown cell. For a software-independent reading copy, open the accompanying HTML file.

**A live page fails:** use the required offline material. Live permission, robots rules, site layout, and network responses can change independently of the indexing algorithms.

## Sources and rights

The lab is based on the supplied `lab04.zip` notebooks and saved pages. The notebook references the information-retrieval textbook and official library documentation used for its definitions and implementation notes. News content remains the property of its respective owners; this package does not grant broader redistribution rights.
