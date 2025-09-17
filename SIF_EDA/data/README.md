# Data directory

This directory contains Git LFS pointers for the three CSV parts created
from the original `traders.csv`. The actual data is not stored in the
repository because the files are large (≈90 MB each). To obtain the
complete datasets you have two options:

1. **Git LFS pull.** If you cloned this repository using `git clone`,
   make sure Git LFS is installed (`git lfs install`) and then run
   `git lfs pull` to download the LFS objects. The three files
   (`traders_part_01.csv`, `traders_part_02.csv`, `traders_part_03.csv`)
   will then appear in this directory.

2. **Manual download.** If you cannot use Git LFS, ask the repository
   owner to provide the CSV files via another channel. Once you have
   downloaded them, place them in this `data/` folder with the exact
   filenames used above.

After the CSVs are available locally you can run the ETL script in
`backend/etl.py` to ingest them into Postgres.