# FD001 source and local file provenance

The FD001 turbofan histories are simulated data from NASA's Prognostics Center of Excellence. NASA's [dataset repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/) identifies the **Turbofan Engine Degradation Simulation** dataset and its source archive. Citation: A. Saxena and K. Goebel (2008), Turbofan Engine Degradation Simulation Data Set, NASA Prognostics Data Repository, NASA Ames Research Center.

On **9 November 2026**, the archive was retrieved from the link on NASA's repository:

`https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip`

The download contains a nested `CMAPSSData.zip`. Only the three FD001 files were extracted, byte-for-byte, into this clone's `data/raw/` directory. Git ignores their contents; each teammate needs their own copy. The raw files must not be edited. The separate RUL file contains test answers; its contents must not be used for training or tuning.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `train_FD001.txt` | 3,515,356 | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` |
| `test_FD001.txt` | 2,228,855 | `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851` |
| `RUL_FD001.txt` | 429 | `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca` |

For provenance, the downloaded outer ZIP has SHA-256 `c9c5dec12a945a82e8bb4446589d7fb3cc057b5e5d81fa1a12e25ee9912ad3b2`; the nested ZIP has SHA-256 `74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f`. These are observed local hashes, not checksums published by NASA.

To verify an existing Windows checkout without printing test answers:

```powershell
Get-FileHash data/raw/train_FD001.txt, data/raw/test_FD001.txt, data/raw/RUL_FD001.txt -Algorithm SHA256
```

Compare the hashes with the table. If a file differs, preserve it and investigate its provenance before replacing anything. This record does not establish loader correctness, data quality, model training, or evaluation results; those are separate tasks.
