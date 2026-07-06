# 🔍 VISUAL QUALITY CONTROL MANUAL — LEELA Studios

## Post-Production Supervisor's Permanent Standard
## Applies to: Every rendered clip, every episode, forever.
## Minimum Score to APPROVE: 95/100

---

## HOW TO USE THIS MANUAL

```
1. Render a clip using the Production Package prompt
2. Open this manual
3. Fill in the REVIEW SHEET (copy the template below)
4. Score each of the 20 criteria: PASS (5) / WARNING (3) / FAIL (0)
5. Calculate total score out of 100
6. If score ≥ 95 → APPROVE → move to LEELA/Approved/
7. If score 85-94 → CONDITIONAL (fix in post if possible, re-render if not)
8. If score < 85 → REJECT → move to LEELA/Rejected/ → re-render
```

---

## SCORING SYSTEM

| Rating | Points | Meaning | Action |
|--------|--------|---------|--------|
| **PASS** | 5 | Meets or exceeds standard. No issues. | Accept as-is |
| **WARNING** | 3 | Minor issue. Fixable in post-production OR acceptable for this clip. | Note for fix OR accept with documentation |
| **FAIL** | 0 | Breaks continuity, violates brand rules, or is visually unacceptable. | MUST re-render. Cannot ship. |

**Maximum score:** 20 criteria × 5 points = **100**
**Minimum to approve:** **95** (allows maximum 1 WARNING among 20 criteria)
**Auto-reject:** Any single FAIL = automatic rejection regardless of total score

---

## THE 20 QC CRITERIA (Detailed Standards)

---

### 1. CHARACTER CONSISTENCY

**What to check:**
- Does the character match their locked Character ID from PRE_PRODUCTION_VALIDATION_V001.md?
- Is the body proportions, height ratio, and build correct?
- Would a viewer recognize this as the SAME character from other scenes?

**PASS:** Character is instantly recognizable. Matches reference completely.
**WARNING:** Character is recognizable but one feature is slightly off (nose shape, chin). Acceptable if not in close-up.
**FAIL:** Character looks like a different person. Wrong body type, wrong proportions, unrecognizable.

---

### 2. FACE CONSISTENCY

**What to check:**
- Does the face match the established reference for this character?
- Are facial proportions consistent (eye spacing, nose shape, jaw line)?
- Is the face symmetric (unless intentionally lit asymmetrically)?
- Is the face rendering realistic (not uncanny valley)?

**PASS:** Face matches reference perfectly. Realistic rendering. No uncanny valley.
**WARNING:** Face is 90% match. Slight deviation in one feature (e.g., nose slightly different). Not noticeable at normal viewing speed.
**FAIL:** Different face entirely. Uncanny valley. Distorted features. Asymmetric in wrong way. AI "melted face" artifact.

---

### 3. EYE QUALITY

**What to check:**
- Are eyes proportionally correct (not too large/small for face)?
- Is catchlight present (per Visual Bible §20 — MANDATORY for living characters)?
- Are both eyes looking in the same direction?
- Is the iris/pupil rendering realistic?
- For Krishna/Vishnu: is the golden fleck in iris present?
- For dead/unconscious characters: is catchlight correctly ABSENT?

**PASS:** Eyes are alive, expressive, correctly directed, with clear catchlight.
**WARNING:** Eyes are acceptable but slightly unfocused or one catchlight missing.
**FAIL:** Cross-eyed. Dead stare on living character. No catchlight. Unrealistic iris. Different colored eyes. Wrong eye size.

---

### 4. HAND QUALITY

**What to check:**
- Correct number of fingers (5 per hand — THE most common AI failure)
- Natural finger proportions and positioning
- No merged or extra fingers
- For Vishnu: are all 4 hands correct with 5 fingers each (20 total)?
- For Durga: are all 8 hands correct (40 total fingers)?
- Are objects held naturally (not floating or phasing through fingers)?

**PASS:** All fingers correct count. Natural positioning. Objects held convincingly.
**WARNING:** Fingers correct but slightly stiff/unnatural positioning. Acceptable in wide shots.
**FAIL:** Wrong finger count (6, 4, or merged). Objects phasing through hand. Distorted/melted hands.

---

### 5. CLOTHING CONTINUITY

**What to check:**
- Does clothing match the Character Lock specification for THIS scene?
- Same color? Same draping style? Same wear/damage level?
- If character was wet in previous scene — are they still wet?
- If character was in prison — is it the prison garment (not wedding)?
- Are borders, patterns, and textures correct?

**PASS:** Clothing exactly matches specification and previous approved shots.
**WARNING:** Clothing is 95% correct. Minor color shift from lighting (acceptable physics).
**FAIL:** Wrong garment entirely. Wrong color. Switched from wet to dry without reason. Modern fabric visible.

---

### 6. JEWELRY CONTINUITY

**What to check:**
- Are ornaments present that SHOULD be (per Character Lock)?
- Are ornaments ABSENT that should NOT be (e.g., no jewelry on imprisoned Devaki)?
- Is the peacock feather present where required (Krishna/Vishnu)?
- Are Vishnu's four objects correct?
- Is the Kaustubha gem visible where specified?
- Is Devaki's mangalsutra visible in prison scenes?

**PASS:** All jewelry/objects exactly per specification. Nothing extra, nothing missing.
**WARNING:** One minor piece slightly different in shape (still recognizable).
**FAIL:** Missing mandatory item (no peacock feather on Krishna = instant FAIL). Extra items that shouldn't be there (jewelry on prisoner). Wrong objects in Vishnu's hands.

---

### 7. LIGHTING CONSISTENCY

**What to check:**
- Does light come from the correct source for this scene?
- Is the lighting TYPE correct (per Visual Bible §4)?
- Is the color temperature correct for the time of day?
- Are shadows falling in the correct direction?
- Is there motivated light only (no floating/unmotivated sources)?
- Does Krishna/Vishnu have rim light (MANDATORY per §4 Rule 1)?

**PASS:** Lighting is logical, beautiful, matches specification. Shadows consistent.
**WARNING:** Lighting is mostly correct but one shadow inconsistency or slight color temp shift.
**FAIL:** Light from impossible direction. Wrong time-of-day feel. No rim light on Krishna. Flat lighting (violates §4 Rule 2). Multiple unmotivated sources.

---

### 8. CAMERA MOVEMENT SMOOTHNESS

**What to check:**
- If static shot: is it TRULY static (no AI jitter/drift)?
- If moving shot: is motion smooth and motivated (not jerky)?
- Are there any sudden unexplained camera movements?
- Does the motion match specification (speed, direction)?
- No handheld/shaky motion (per Visual Bible §8 — NEVER)

**PASS:** Camera movement perfectly smooth and matches spec (or perfectly static).
**WARNING:** Very slight jitter (1-2 pixels) that's unnoticeable at normal playback speed.
**FAIL:** Visible jitter. Unexpected motion. Jerky movement. Shaky-cam quality.

---

### 9. PHYSICS REALISM

**What to check:**
- Does fabric move according to gravity (unless divine wind specified)?
- Do objects have appropriate weight and momentum?
- Does hair respond to movement realistically?
- Does water flow downward (unless miracle scene specified)?
- Do characters have physical presence (feet on ground, weight)?

**PASS:** All physics feel natural and grounded. Objects behave correctly.
**WARNING:** One element slightly floats or moves unrealistically (barely noticeable).
**FAIL:** Characters floating without reason. Objects defying gravity incorrectly. Hair frozen mid-air. Fabric moving impossibly.

---

### 10. WATER REALISM

**What to check (when water is present):**
- Does water have correct transparency, reflection, and movement?
- Is turbidity correct for the scene (monsoon = murky, sacred = clearer)?
- Are ripples and currents natural?
- In Yamuna miracle scene: does the held water still MOVE within itself?
- Are reflections present on water surfaces (stars, moonlight, characters)?
- Are puddles reflective?

**PASS:** Water looks photorealistic. Correct physics (or correctly supernatural in miracle scenes).
**WARNING:** Water is 90% convincing. Slight flatness or missing reflections in one area.
**FAIL:** CG-looking water (plastic/glass appearance). No movement. No reflections. Frozen solid appearance. Wrong color entirely.

---

### 11. HAIR REALISM

**What to check:**
- Are individual strands/groups visible (not solid mass)?
- Does hair respond to wind/movement (subtle in most scenes)?
- Is hair color correct (blue-black for Krishna, black with grey for Vasudeva)?
- Is hair WET where it should be (Vasudeva during journey)?
- Is Devaki's greying at temples present (after Scene 07.4)?

**PASS:** Hair looks natural with strand detail, correct color, and appropriate physics.
**WARNING:** Hair is slightly too solid/mass-like but not distracting. Or single strands missing.
**FAIL:** Plastic-looking hair. Completely wrong color. Dry when should be wet. Frozen in place with no life.

---

### 12. CLOTH SIMULATION

**What to check:**
- Does fabric drape naturally on the body?
- Does fabric respond to movement (walking, wind, divine wind)?
- Are folds and creases realistic?
- Is wet fabric clinging correctly (Vasudeva during journey)?
- Is silk catching light at folds (Vishnu's pitambara)?
- Is divine fabric moving in supernatural wind (correctly specified in prompt)?

**PASS:** Fabric is beautiful, natural, correctly responds to forces. Folds are realistic.
**WARNING:** Fabric is mostly natural but one area stiff or unnatural.
**FAIL:** Fabric frozen solid. Wrong draping physics. Paper-like appearance. Phasing through body.

---

### 13. LIP SYNCHRONIZATION

**What to check:**
- N/A for most LEELA clips (narration is voice-over, not on-screen dialogue)
- Only relevant if character is shown SPEAKING (rare in this format)
- When applicable: do lips move naturally to implied speech?

**PASS:** N/A (narrator format) OR lips sync convincingly.
**WARNING:** Slight mismatch between implied speech and mouth movement.
**FAIL:** Completely wrong lip movement. Mouth moving when should be closed. Speaking without movement.

*Note: Most clips will auto-PASS this criterion since LEELA uses voice-over narration.*

---

### 14. EMOTIONAL IMPACT

**What to check:**
- Does this clip make you FEEL the intended emotion (per script/storyboard)?
- Would a viewer pause, rewatch, or screenshot this moment?
- Does the character's expression match the emotional specification?
- Is the composition serving the emotion (intimate vs. epic)?
- Would a devotee feel moved by this image?

**PASS:** The clip delivers the specified emotion powerfully. You FEEL it.
**WARNING:** Emotion is present but at 70% intensity. Needs stronger expression or better lighting to land fully.
**FAIL:** Wrong emotion entirely. Flat affect. Character looks confused when should look awed. No emotional resonance.

---

### 15. SCRIPT ACCURACY

**What to check:**
- Does this clip show what the SCRIPT specifies for this timestamp?
- Is the character doing what the narration describes?
- Is the location correct for this beat?
- Are the correct characters present (and absent)?
- Does the visual match the storyboard specification?

**PASS:** Clip perfectly matches script/storyboard specifications.
**WARNING:** Clip is 90% accurate. Minor deviation (e.g., character facing slightly different direction).
**FAIL:** Wrong scene. Wrong characters. Wrong action. Doesn't match script AT ALL.

---

### 16. VISUAL ARTIFACTS

**What to check:**
- No pixelation, banding, or compression artifacts
- No flickering elements
- No temporal inconsistencies (morphing between frames)
- No sudden color shifts
- No aliasing on edges
- No rendering noise in dark areas

**PASS:** Clean, artifact-free image. Professional broadcast quality.
**WARNING:** Minor artifact in one frame (barely visible). Acceptable if in dark corner.
**FAIL:** Visible flickering. Morphing. Major banding. Pixelation. Temporal glitches.

---

### 17. AI GLITCHES

**What to check:**
- No extra limbs (additional arms, legs appearing)
- No merged body parts (two characters fusing)
- No impossible anatomy (bent wrong way, missing joints)
- No text/lettering appearing in image (AI sometimes generates random text)
- No modern objects (watches, glasses, phones)
- No faces in backgrounds that shouldn't be there
- No distorted/melted features

**PASS:** Zero AI glitches detected. Image appears hand-crafted, not AI-generated.
**WARNING:** Very minor anomaly in far background (e.g., a slightly odd shape in distant crowd). Not noticeable at playback speed.
**FAIL:** ANY visible glitch in subject or mid-ground. Extra fingers. Merged limbs. Random text. Distorted face. Impossible anatomy.

---

### 18. BACKGROUND CONSISTENCY

**What to check:**
- Does the background match the Environment Reference ID?
- Is architecture correct for the location (prison = stone, Gokul = thatch)?
- Are there any anachronisms (modern buildings, power lines)?
- Is background appropriate for time of day?
- Is there LIFE in backgrounds (per Visual Bible §10 — birds, movement)?
- Does background depth match the lens specification?

**PASS:** Background perfectly matches environment spec. Correct architecture. Era-appropriate.
**WARNING:** Background is 90% correct. Minor element slightly off (e.g., vegetation not quite matching).
**FAIL:** Wrong location. Modern elements visible. Anachronisms. Completely empty/sterile background.

---

### 19. SACRED SYMBOLISM ACCURACY

**What to check:**
- Are Hindu symbols depicted correctly (Om, Shrivatsa, etc.)?
- Is the peacock feather correctly placed (per Character Lock)?
- Are deities depicted with appropriate respect and accuracy?
- No accidental mixing of religious iconography (no halos, crosses, etc.)?
- Are the four items in Vishnu's hands correct (conch, disc, mace, lotus)?
- Is Shrivatsa on the RIGHT side of chest?
- Is the number of arms/heads correct per character?

**PASS:** All sacred elements accurate per Hindu scripture and visual tradition.
**WARNING:** One minor symbolic placement issue (fixable in post — e.g., flower garland slightly wrong style).
**FAIL:** Wrong religious iconography (Western angel features on Hindu deity). Incorrect sacred marks. Disrespectful depiction. Wrong number of arms/heads.

---

### 20. THUMBNAIL POTENTIAL

**What to check:**
- Could a frame from this clip work as a thumbnail or social media share?
- Is the image compelling at 168×94 pixels (YouTube mobile search)?
- Is there a clear focal point?
- Are brand colors present (blue + gold)?
- Would this image make someone STOP SCROLLING?

**PASS:** Multiple frames in this clip are screenshot-worthy. Strong thumbnail candidate.
**WARNING:** Clip is good video but lacks a standout single-frame moment.
**FAIL:** No frame in this clip works as a still image. Blurry. Unfocused. No clear subject.

---

# ══════════════════════════════════════════
# REVIEW SHEET TEMPLATE (Copy for Each Clip)
# ══════════════════════════════════════════

```markdown
# 🔍 QC REVIEW SHEET

## Clip ID: [Hero_XX / Scene_XX_Shot_XX]
## Episode: V001
## Render Attempt: #[N]
## Date: [YYYY-MM-DD]
## Reviewer: Post-Production Supervisor

---

| # | Criterion | Rating | Notes |
|---|-----------|--------|-------|
| 1 | Character Consistency | PASS / WARNING / FAIL | |
| 2 | Face Consistency | PASS / WARNING / FAIL | |
| 3 | Eye Quality | PASS / WARNING / FAIL | |
| 4 | Hand Quality | PASS / WARNING / FAIL | |
| 5 | Clothing Continuity | PASS / WARNING / FAIL | |
| 6 | Jewelry Continuity | PASS / WARNING / FAIL | |
| 7 | Lighting Consistency | PASS / WARNING / FAIL | |
| 8 | Camera Movement | PASS / WARNING / FAIL | |
| 9 | Physics Realism | PASS / WARNING / FAIL | |
| 10 | Water Realism | PASS / WARNING / FAIL | |
| 11 | Hair Realism | PASS / WARNING / FAIL | |
| 12 | Cloth Simulation | PASS / WARNING / FAIL | |
| 13 | Lip Sync | PASS / WARNING / FAIL / N/A | |
| 14 | Emotional Impact | PASS / WARNING / FAIL | |
| 15 | Script Accuracy | PASS / WARNING / FAIL | |
| 16 | Visual Artifacts | PASS / WARNING / FAIL | |
| 17 | AI Glitches | PASS / WARNING / FAIL | |
| 18 | Background Consistency | PASS / WARNING / FAIL | |
| 19 | Sacred Symbolism | PASS / WARNING / FAIL | |
| 20 | Thumbnail Potential | PASS / WARNING / FAIL | |

---

## SCORE CALCULATION:

PASS count: [__] × 5 = [__]
WARNING count: [__] × 3 = [__]
FAIL count: [__] × 0 = 0
N/A count: [__] (excluded from total — adjust denominator)

**TOTAL: [__] / [__]**

---

## DECISION:

□ ✅ APPROVED (≥95) — Move to LEELA/Approved/
□ ⚠️ CONDITIONAL (85-94) — Fix in post OR re-render
□ ❌ REJECTED (<85 OR any FAIL) — Move to LEELA/Rejected/

---

## NOTES FOR RE-RENDER (if rejected):
- What specifically needs to change:
- Prompt adjustment suggestion:
- Priority elements for next attempt:

---

## CONTINUITY SIGN-OFF:
□ This clip is consistent with all previously approved clips
□ Character Reference ID matches: [CHAR-XX]
□ Environment Reference ID matches: [ENV-XX]
```

---

# ══════════════════════════════════════════
# SPECIAL RULES & EXCEPTIONS
# ══════════════════════════════════════════

## Auto-PASS Rules (Criteria that auto-pass in specific situations):

| Criterion | Auto-PASS When |
|-----------|---------------|
| 10. Water Realism | Scene has no water present |
| 13. Lip Sync | Voice-over narration (no on-screen speech) |
| 20. Thumbnail Potential | This is a transition/filler shot (not meant to be a highlight) |

**When a criterion is N/A:** Remove from total (score out of remaining applicable × 5).
Example: 19 applicable criteria × 5 = 95 max. Score of 91/95 = 95.8% → APPROVED.

---

## Auto-REJECT Rules (Immediate rejection regardless of total score):

| Condition | Result | No Exceptions |
|-----------|--------|---------------|
| Wrong number of arms on deity | INSTANT REJECT | Even if everything else is perfect |
| Wrong number of serpent heads | INSTANT REJECT | Must be exactly 5 |
| Modern object visible in frame | INSTANT REJECT | No watches, phones, cars, ever |
| AI-generated text visible in image | INSTANT REJECT | Random letters/words = unusable |
| Character with WRONG SKIN COLOR | INSTANT REJECT | Krishna must be blue, always |
| Disrespectful deity depiction | INSTANT REJECT | No mockery, no inappropriate pose |
| Missing peacock feather on Krishna/Vishnu | INSTANT REJECT | Brand-critical element |

---

## WARNING Tolerance:

| Total Warnings | Decision |
|----------------|----------|
| 0 | Perfect score (100). Approve. |
| 1 | Score = 97. Approve (within tolerance). |
| 2 | Score = 94. CONDITIONAL. Assess: are both warnings in non-critical areas? |
| 3+ | Score ≤ 91. Likely REJECT. Re-render. |

---

## POST-APPROVAL Steps:

```
After every APPROVED clip:
1. Rename file: [SceneXX]_[ShotXX]_APPROVED_[date].mp4
2. Move to LEELA/Approved/
3. Log in RENDERING_ORDER.md status tracker
4. Extract best frame → save as reference for continuity checking of FUTURE renders
5. Note the SEED (if available) for consistent character in related shots
```

---

## CROSS-EPISODE Continuity:

This QC Manual applies to ALL future LEELA episodes. When rendering V002, V003, etc.:

```
□ Krishna's baby form in V002 must match V001's approved baby renders
□ Gokul environment in V002 must match V001's approved Gokul renders
□ Yashoda's face in V002 must match V001's approved Yashoda
□ Voice (audio) must be same Sarvam AI Priya in every episode
□ Color grading must match established LEELA look
□ Intro/outro must be identical across all episodes
```

---

## ESCALATION PATH:

```
If a shot CANNOT pass QC after 8 attempts:
1. Document all 8 failures with specific issues
2. Assess: Is the prompt achievable with current AI technology?
3. Options:
   a. Simplify the composition (remove secondary elements)
   b. Split into two shots composited in edit
   c. Accept best attempt with post-production fixes
   d. Replace with alternative angle that achieves same narrative purpose
4. Decision must be documented in shot folder
```

---

# ══════════════════════════════════════════
# QC MANUAL STATUS
# ══════════════════════════════════════════

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  🔍 VISUAL QC MANUAL v1.0 — LOCKED                │
│                                                    │
│  20 criteria. 3 ratings. 100-point scale.          │
│  Minimum to approve: 95/100                        │
│  Any single FAIL: Auto-reject                      │
│  7 auto-reject conditions defined                  │
│  Applies to: Every clip. Every episode. Forever.   │
│                                                    │
│  "If it wouldn't survive pause-and-zoom,           │
│   it doesn't belong in LEELA."                     │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

*Visual Quality Control Manual v1.0*
*Post-Production Supervisor*
*LEELA Studios*
*Date: July 4, 2026*
*Classification: Core Production Document — PERMANENT*
