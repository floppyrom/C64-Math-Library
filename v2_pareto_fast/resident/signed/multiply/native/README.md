# Native signed multiplication

All `SMUL8`, `SMUL16`, `SMUL24`, and `SMUL32` public paths for this profile own signed executable paths. The canonical source is the profile's relocatable source file. This directory retains hand-authored specialized source artifacts where one exists (notably the V2–V4 executable-ZP `SMUL16` kernel).

Sharing immutable quarter-square/REU tables is allowed; sharing executable unsigned multiply code is not. See `../../SIGNED_LINK_MAP.json` and the signed-layout validator.
