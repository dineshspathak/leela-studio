# LEELA Studios Repository Audit

**Audit date:** 04 July 2026  
**Scope:** Entire repository, excluding version-control internals  
**Method:** Read-only structure inspection, reference checks, filename review, empty-folder review, and SHA-256 content comparison  
**Source-of-truth files reviewed first:** `README.md`, `LEELA_CONTEXT.md`, `00_MASTER/MASTER_INDEX.md`

## 1. Repository Health Score (/100)

**52/100 — Requires Attention**

The master registry's five named canonical documents all exist, and V001 has substantial research, scripting, storyboard, validation, EDL, and approved hero-motion work. However, the repository has three incompatible structure definitions, two required top-level folders are absent, one context-designated canonical master document is absent, V001 references many unavailable production assets, and naming conventions are not being applied consistently.

Score basis:

| Area | Score | Maximum |
|---|---:|---:|
| Canonical/master document availability | 15 | 20 |
| Folder structure compliance | 8 | 20 |
| Reference integrity | 7 | 20 |
| Naming consistency | 8 | 15 |
| Duplicate/version control hygiene | 7 | 10 |
| Asset organization and archive hygiene | 7 | 15 |
| **Total** | **52** | **100** |

## 2. Folder Structure Review

### Present and correctly placed

- `00_MASTER/`, `01_EPISODES/`, `02_ASSETS/`, and `09_ARCHIVE/` exist at repository root.
- All seven master files described by `README.md` and `PROJECT_STRUCTURE.md` exist in `00_MASTER/`.
- V001 is correctly isolated under `01_EPISODES/V001/`.
- The five approved hero-motion renders are centralized under `02_ASSETS/Approved/`.
- Rejected media and superseded documentation are separated under `09_ARCHIVE/`.

### Structural non-compliance

- `03_OUTPUT/` and `04_TOOLS/`, required by `LEELA_CONTEXT.md`, do not exist.
- `00_MASTER/PRODUCTION_SYSTEM.md` defines a completely different canonical tree (`00_BRAND`, `01_SCRIPTS`, `02_VOICEOVER`, `03_VISUALS`, `04_PROJECTS`, `05_EXPORTS`, `06_SEO`, `07_ANALYTICS`, `08_ASSETS`, `09_ARCHIVE`). The live repository instead uses the structure in `README.md` and `PROJECT_STRUCTURE.md`.
- `LEELA_CONTEXT.md` prescribes episode folders such as `V001_KRISHNA_BIRTH`; the live folder is `V001`.
- The episode model in `LEELA_CONTEXT.md` requires Research, Architecture, Script, Storyboard, Production Plan, Asset Plan, Voice, Images, Hero Motion, Edit, Thumbnail, SEO, Final Export, and Analytics. V001 contains several planning equivalents, but has no organized Voice, Images, Edit, Final Export, or Analytics area.
- `PROJECT_STRUCTURE.md` reflects the live tree more accurately than the canonical `PRODUCTION_SYSTEM.md`, creating ambiguity over which structure is authoritative.
- Four archive folders (`Final`, `SEO`, `Shorts`, `Thumbnails`) are empty. This is not harmful, but their purpose should be confirmed.

## 3. Missing Files

### Canonical or explicitly required

- `00_MASTER/MASTER_ASSET_LIBRARY.md` — listed twice as the character-continuity reference and as a canonical master document in `LEELA_CONTEXT.md`; absent.
- `AUDIO_LOCK_CHECKLIST` — required by `README.md`; no file with this name exists.

### Missing V001 production deliverables or dependencies

- `VOICE_PACKAGE_V001_v2.mp3`, referenced by `01_EPISODES/V001/EDL_V001.md`.
- `02_ASSETS/Approved/LEELA_Intro_v1.mp4` and `02_ASSETS/Approved/LEELA_Outro_v1.mp4`.
- `LEELA_Intro_5sec.mp3`.
- All 33 `IMG-V001-*.png` scene images referenced by the EDL.
- Seven overlay clips referenced by the EDL: monsoon rain, god rays, golden particles, golden flare, falling marigold petals, drifting fog, and divine particles.
- The named storyboard sound-effect files are absent from the repository.
- No final V001 export, thumbnail image, analytics report, or edit-project file is present.

### Master registry gap

- All five documents explicitly registered in `MASTER_INDEX.md` exist. However, `VISUAL_QC_MANUAL.md` exists in `00_MASTER/` and is declared canonical by `README.md` and `LEELA_CONTEXT.md`, but is omitted from the Master Index document registry and hierarchy.

## 4. Broken References

- `MASTER_INDEX.md` repeatedly refers to `BRAND_IDENTITY.md`; the actual file is `KRISHNA_BRAND_IDENTITY.md`.
- `MASTER_INDEX.md` refers to `CHANNEL_STRATEGY.md`; the actual file is `KRISHNA_CHANNEL_STRATEGY.md`.
- `README.md` refers to `AUDIO_LOCK_CHECKLIST`, which does not exist.
- `LEELA_CONTEXT.md` refers to missing `MASTER_ASSET_LIBRARY.md`.
- `EDL_V001.md` points to missing intro/outro, voice, image, overlay, and audio assets. The five approved hero-shot paths in the same document are valid.
- `STORYBOARD_V001.md` references the same missing intro/outro assets and numerous unavailable sound effects.
- Relative references such as `PRODUCTION_PACKAGE.md` and `RENDERING_ORDER.md` are valid only when interpreted from their local hero-shot directories; they are not linked with explicit repository paths.
- The line counts in `MASTER_INDEX.md` are stale: `PRODUCTION_SYSTEM.md` is listed as 1,144 lines but currently contains 1,201 lines. The other five registered document counts match.

## 5. Duplicate Files

SHA-256 comparison found five exact duplicate pairs:

| Working render | Approved duplicate |
|---|---|
| `01_EPISODES/V001/Hero_Shots/Hero_01_Vishnu/Generated Video July 04, 2026 - 4_47PM.mp4` | `02_ASSETS/Approved/Hero_01_Vishnu_APPROVED_20260704.mp4` |
| `01_EPISODES/V001/Hero_Shots/Hero_02_Sheshnag/Generated Video July 04, 2026 - 3_51PM.mp4` | `02_ASSETS/Approved/Hero_02_Sheshnag_APPROVED_20260704.mp4` |
| `01_EPISODES/V001/Hero_Shots/Hero_03_Yamuna/Generated Video July 04, 2026 - 5_15PM.mp4` | `02_ASSETS/Approved/Hero_03_Yamuna_APPROVED_20260704.mp4` |
| `01_EPISODES/V001/Hero_Shots/Hero_04_Yashoda/Generated Video July 04, 2026 - 3_36PM.mp4` | `02_ASSETS/Approved/Hero_04_Yashoda_APPROVED_20260704.mp4` |
| `01_EPISODES/V001/Hero_Shots/Hero_05_Yogamaya/Generated Video July 04, 2026 - 4_25PM.mp4` | `02_ASSETS/Approved/Hero_05_Yogamaya_APPROVED_20260704.mp4` |

These appear to be intentional source-to-approved copies, not accidental content collisions. They consume roughly 170 MB of duplicate storage and make it unclear which copy should be retained long-term. No duplicate Markdown files were found by content hash.

## 6. Naming Issues

- The repository uses three competing conventions: the date/category/version convention in `PRODUCTION_SYSTEM.md`, the `*_V001_FINAL` convention in `LEELA_CONTEXT.md`, and the live mixed convention.
- `V001` does not follow the context-prescribed folder name `V001_KRISHNA_BIRTH`.
- Raw video names such as `Generated Video July 04, 2026 - 4_47PM.mp4` contain spaces, punctuation, a locale-style date, and no episode ID.
- Episode planning files `IMAGE_PROMPT_PLAN.md`, `SEO_PLAN.md`, `THUMBNAIL_PLAN.md`, and `MASTER_PRODUCTION_CHECKLIST.md` omit `V001`, unlike most neighboring files.
- `QC_REVIEW_ATTEMPT2.md` and `QC_REVIEW_ATTEMPT3.md` use attempt numbering, while approved assets use status plus compact dates. Version vocabulary is inconsistent.
- `Hero_Shots` and `Approved` use mixed title case while most document names use uppercase snake case.
- `IMG-V001-*` references use hyphens while the documented master filename patterns use underscores.
- `BRAND_IDENTITY.md`/`CHANNEL_STRATEGY.md` shorthand in the Master Index does not match actual canonical filenames.
- `.DS_Store` files exist at repository root and inside `Hero_Shots/`; these are operating-system metadata, not LEELA assets.

## 7. Archive Recommendations

No files should be moved without approval. Candidates for review are:

- Move `QC_REVIEW_ATTEMPT2.md` and `QC_REVIEW_ATTEMPT3.md` to an episode-specific rejected/review-history archive after confirming `QC_REVIEW.md` is the active record.
- After choosing a retention policy, archive or remove one side of each exact render/approved duplicate pair. Prefer preserving the approved canonical filename and retaining provenance through metadata or a manifest.
- Remove `.DS_Store` files from tracked/project content and exclude them from future repository intake.
- Confirm whether the three files in `09_ARCHIVE/Audio/` are truly historical. `VOICEOVER_SCRIPT_V001_FINAL.md` is named “FINAL” but is archived while the active episode lacks a voice package, creating status ambiguity.
- Retain `09_ARCHIVE/LEELA_STUDIO_V2_PRODUCTION.md` and the rejected Yogamaya render in the archive; their placement is appropriate.
- Keep the four empty archive category folders only if they are intentional placeholders.

## 8. Risks

- **High — Production blockage:** V001 cannot be assembled from repository contents because voice, scene images, overlays, intro/outro, and sound assets are missing.
- **High — Authority ambiguity:** Three incompatible structures are each described as canonical or locked. Future contributors may create assets in different trees.
- **High — Character continuity:** The designated `MASTER_ASSET_LIBRARY.md` does not exist, despite a permanent rule requiring locked character appearances.
- **High — False readiness signal:** `MASTER_INDEX.md` says the studio is ready for V001 production, while essential dependencies are absent.
- **Medium — Quality-gate bypass:** The README mandates an audio lock checklist that cannot be found.
- **Medium — Asset provenance:** Exact approved copies have no manifest linking them to source renders, QC decision, version, or approval authority.
- **Medium — Incomplete master index:** `VISUAL_QC_MANUAL.md` is authoritative elsewhere but absent from the supreme registry.
- **Medium — Reference fragility:** Plain-text filenames and shorthand aliases are easy to break and cannot be automatically navigated like explicit relative links.
- **Low — Repository hygiene:** `.DS_Store`, mixed filename casing, and space-heavy generated filenames reduce portability and automation reliability.
- **Low — Version-control visibility:** No usable Git worktree metadata was available at the audited root, so tracked/untracked status and history integrity could not be verified.

## 9. Recommended Actions (Priority High / Medium / Low)

### High

1. Select and formally declare one repository structure as canonical; reconcile `PRODUCTION_SYSTEM.md`, `LEELA_CONTEXT.md`, `README.md`, and `PROJECT_STRUCTURE.md` only after approval.
2. Create or restore `MASTER_ASSET_LIBRARY.md`, or explicitly remove it from the canonical requirements after confirming the intended character-continuity source.
3. Restore or generate the V001 voice package, 33 scene images, overlays, intro/outro, and required audio assets; then re-run the EDL dependency check.
4. Create or identify the required audio lock checklist before image generation or final assembly.
5. Add `VISUAL_QC_MANUAL.md` to the Master Index registry and hierarchy, or explicitly classify it as non-canonical.

### Medium

1. Replace Master Index shorthand aliases with exact filenames and explicit relative paths.
2. Adopt one naming convention for episode folders, plans, media, versions, approval states, and dates.
3. Add an asset manifest recording source file, approved copy, content hash, QC status, approval date, and reuse scope.
4. Decide whether working hero renders remain active, move to episode archives, or are represented only by approved-library copies.
5. Resolve the archived “FINAL” voice script versus the missing active voice deliverable.
6. Update the stale `PRODUCTION_SYSTEM.md` line count in the Master Index when documentation changes are authorized.

### Low

1. Exclude and remove `.DS_Store` metadata after approval.
2. Confirm whether empty archive folders are intentional placeholders.
3. Convert document and asset references into explicit relative Markdown links where appropriate.
4. Add a repeatable, read-only repository validation check for missing paths, duplicate hashes, naming rules, and orphan assets.

🔴 Repository Requires Attention
