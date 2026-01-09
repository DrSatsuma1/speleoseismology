# Paleoseismic Cave Research: Gaps and Priorities

See `COMPLETED_TASKS.md` for archive of tasks.

## HIGH PRIORITY - Multivariate Model Data Gaps (2026-01-03)

| # | Task | Notes |
|---|------|-------|
| **MV0** | **Review multivariate compilation data** | See `CAVE_MULTIVARIATE_MODEL.md` and `data/multivariate/*.csv`. Compiled 2026-01-03: noise levels, correlations, thresholds for 6 caves. Gejkar only full-panel cave in SISAL. |
| **MV1** | **Get δ13C for Bàsura** | Missing critical seismic/volcanic discriminator - contact Drysdale or Hu et al. |
| **MV2** | **Get Mg/Ca for Crystal Cave** | Need multi-proxy confirmation - reanalyze samples or contact authors |
| **MV3** | **Get U/Ca for more caves** | Gejkar showed z=+6.87σ for 1304 Tabriz - may be superior to δ18O in some settings |
| ~~**MV4**~~ | ~~Test Gejkar 1304 Tabriz with detection algorithm~~ | ✅ COMPLETE 2026-01-03. Algorithm validated: 2/2 known events passed. 7 HIGH confidence events discovered including 5 with historical correlates. See `regions/turkey/GEJKAR_MULTIPROXY_VALIDATION.md` |
| ~~**MV5**~~ | ~~Research ~967 CE and ~979 CE Zagros events~~ | ✅ COMPLETE 2026-01-03. **958 CE Ray-Taleghan Ms 7.7 CONFIRMED** within 947-967 CE window (0 yr offset). Distance 572 km, Chiodini 14.9% CO₂. ~979 CE = NEW CANDIDATE (no historical match). Algorithm now 3/3 validation passes. See `regions/turkey/GEJKAR_MULTIPROXY_VALIDATION.md` |
| **MV6** | **Research 17th century Zagros events (~1651, ~1688 CE)** | HIGH confidence U/Ca signals (z=+4.92σ, +3.99σ). Cross-reference Ambraseys & Finkel (1995). |

## 🚨 CRITICAL: Blind Validation Required (2026-01-03)

**Problem identified**: All validation to date was post-hoc (we knew earthquakes occurred, then checked caves). True validation requires BLIND prediction.

| # | Task | Cave | Notes |
|---|------|------|-------|
| **BV1** | Blind validate Dos Anas 1708 CE detection | Dos Anas | HIGH conf (z=-2.03σ). No NOAA match. Check Guane Fault local records. |
| **BV2** | Blind validate Dos Anas 1790 CE detection | Dos Anas | HIGH conf (z=-2.16σ). No NOAA match. 1785/1787 Caribbean EQs nearby in time. |
| **BV3** | Investigate 1769 detection distance problem | Dos Anas | Attributed to 1766 Santiago M7.6 at **917 km** - violates 50 km threshold. Alternative: undocumented Guane Fault event? |
| **BV4** | Explain 1880 San Cristóbal M6 non-detection | Dos Anas | Only 106 km away but NOT detected. Why? |
| **BV5** | Blind validate Crystal Cave untested detections | Crystal Cave | 11 HIGH conf events not yet researched |
| **BV6** | Blind validate Bàsura untested detections | Bàsura | 5 HIGH conf events not yet researched |
| **BV7** | Blind validate Gejkar untested detections | Gejkar | 24 HIGH conf events not yet researched |

**Preliminary Dos Anas results (2026-01-03)**: 1/3 post-catalog detections matched documented EQ, but with severe distance problem. Model validation INCONCLUSIVE pending BV1-BV4.

---

## 🔍 DATABASE VERIFICATION (2026-01-03)

**Lesson learned**: Simple web searches found that Crystal Cave ~1745 and Yok Balum ~620 CE were KNOWN events, not discoveries. Must search databases BEFORE claiming "dark earthquake."

| # | Task | Database | Notes |
|---|------|----------|-------|
| **DB1** | Download CPTI15 v4.0 | https://emidius.mi.ingv.it/CPTI15-DBMI15/ | Italian parametric catalog 1000-2020 |
| **DB2** | Download CFTI5Med | https://cfti.ingv.it | Strong earthquakes Italy + Mediterranean |
| **DB3** | Download ASMI | https://emidius.mi.ingv.it/ASMI/ | Italian historical earthquake archive |
| **DB4** | Search for 1394 Liguria earthquake | CPTI15/CFTI5Med | Verify if Bàsura ~1394 is truly "dark" |
| **DB5** | Search for 1285 Liguria earthquake | CPTI15/CFTI5Med | Verify if Bàsura ~1285 is truly "dark" |
| **DB6** | Search for 1676 Utah earthquake | USGS paleoseismic | Verify Minnetonka ~1676 vs Wasatch record |

---

## Validation & Cross-Reference Tasks

| # | Task | Notes |
|---|------|-------|
| **VAL6** | Get actual δ13C measurements for Bàsura | Contact Hu et al. or commission new analysis - **BIGGEST DATA GAP** |
| **VAL7** | Design explicit falsification tests | Document what would disprove each claim |
| **VAL8** | Validate temporal shape on n≥5 events | Current n=2 too small for publication claim |
| **VAL9** | Cross-check ²³²Th vs ice core eruptions | Rule out volcanic ash before ANY ²³²Th claims |
| **VAL10** | Review all "CONFIRMED" classifications | Demote anything without multi-proxy to "candidate" |
 **VAL11** The ML candidate file GLOBAL_DARK_EARTHQUAKE_INVENTORY.md has 124 entries - we've deeply analyzed ~60% of them. Need to check the rest
| **IC3** | Compile Maya archaeological destruction chronology | ~620 CE - Quirigua flood + Tikal hiatus |
| **IC6** | Extend tree ring chronology pre-1457 | Fort Ross/Gualala bark-dated stumps |
| **IC8** | Add Mackie 1959 earthquake corroboration to Paper 2 | Xunantunich Structure A11 |
| **IC9** | Obtain MacKie 1985 BAR Int'l Series 251 publication | Primary source for earthquake hypothesis |
| **MS1** | Add microseismicity findings to Paper 2 | Section 7.1.3 - NNW fault as candidate |
| **MS2** | Overlay NNW cluster on TINITALY DEM | ✅ COMPLETE - See DEM_LINEAMENT_FINDINGS.md |
| **MS3** | Review DEM lineament findings | See `regions/italy/DEM_LINEAMENT_FINDINGS.md` - 25+ km unmapped fault identified |
| **MS4** | Verify Italy lineament with InSAR/INGV | Contact INGV, check Copernicus InSAR for ground deformation |
| **MS5** | **Update papers with fault database verification** | ✅ VERIFIED 2026-01-03: NNW (340°) and SW (280-320°) structures NOT in DISS, EFSM20, or GEM. Update THE_1394_DARK_EARTHQUAKE.md, PAPER_2_DARK_EARTHQUAKES.md with this confirmation. See DARK_EARTHQUAKE_AUDIT.md |
| **SD1** | San Diego DEM lineament analysis | See `regions/north_america/SAN_DIEGO_DEM_LINEAMENT_PLAN.md` - Map 1741 Rose Canyon rupture extent |
| **SF1** | Create Figure S2: INGV microseismicity map | |
| **SF2** | Literature search: NNE structure documentation | |
| **U1** | Confirm ~1285/1310 North Coast SAF event | **BLOCKED** - tree rings undated; need bark-dated samples |
| **U2** | Find bark-dated redwood stumps | Contact Save the Redwoods League, CA State Parks |
| **U4** | Cross-reference Pallett Creek lake sediment seismites | Check for ~1285/1310 event |
| **VAL11** | Expand blind test to n≥20 | n=6 insufficient for robust statistics |
| **VAL12** | Find 2nd Central American cave for 620 CE | Single-cave evidence is weak |
| **VAL13** | Request Klapferloch raw δ13C | Verify cross-cave claim independently |
| **VAL14** | Test alternative mechanisms | Hypogene upwelling, karst capture, etc. |
| **FC1** | Find standalone flood calibration event | Need documented flood + cave + NO concurrent earthquake |
| **FC2** | Find additional fire calibration events | Need different geologies (n=1 is provisional) |
| **FC3** | Test if small fires overlap seismic z-score range | Critical for discrimination |
| **TH1** | Review Kennett 2012 SI Table S2 for ²³²Th | Check 620, 700, 827 CE depths |
| **TH4** | Add 232TH_DATA_ARCHAEOLOGY.md to bibliography | |
| **GO-R** | Review Sofular/Lebanon/Romania analysis quality | Verify data products |
| **GO1** | Run orphan analysis on Lebanon microseismicity | Use `global_orphan_analysis.py` |
| **~~GO2~~** | ~~Run orphan analysis on Romania microseismicity~~ | ✅ COMPLETE - See CLOSANI_CAVE_FAULT_DATABASE_VERIFICATION.md |
| **GO3** | Get Jeita Cave (entity 58) data | **BLOCKED** - SISAL NA error |
| **~~GO4~~** | ~~Get Closani Cave (entity 390) data~~ | ✅ COMPLETE - 1541-1543 CE RECLASSIFIED as pre-instrumental on mapped fault |
| **GO8** | Create global orphan rate comparison figure | |
| **GO10** | Cross-validate Sofular 402 CE with Byzantine records | 45 yr before 447 CE Constantinople EQ |

| **IV1** | EGMS InSAR analysis for Italy NNE structure | Strain accumulation on unmapped fault |
| **IV2** | Maya Mountains GPS/InSAR strain analysis | More useful than microseismicity for locked fault |
| **IV3** | Literature search: Ligurian soil gas surveys | Validate Chiodini CO₂ mechanism |
| **SG1** | Download USGS Water Quality data for Kaweah gauges | 11206820, 11208730, 11209900 |
| **SG2** | Check for 1952 Kern County M7.3 signal | 60 km from Crystal Cave |
| **SG4** | Cross-reference with Crystal Cave anomalies | Validate Chiodini mechanism |
regions/turkey/KOCAIN_417CE_VALIDATION.md add to paper?

---

## 🟢 LOW: Future Extensions

### Regional Investigations

| # | Task | Notes |
|---|------|-------|
| **7** | Maya Mountains paleoseismic trenching | Southern Boundary Fault test |
| **7b** | Southern Boundary Fault literature search | |
| **7c** | Investigate Lubaantun/Uxbenka for ~700 CE | ~20-30 km from Yok Balum |
| **7d** | Re-examine Caracol excavation reports | Look for structural damage |
| **11** | δ13C measurements for Bàsura | Contact Dr. Shen (Taiwan) |
| **11b** | Lipid biomarker analysis | P(m) microbial % at seismic horizons |
| **MEX1** | Investigate Cacahuamilpa Cave | Central Mexico broken speleothems (Mejean et al. 2014, https://doi.org/10.1016/J.JSAMES.2014.11.002). Physical rupture at 0.95 ka, 28.8 ka, 88 ka. Test if geochemical anomalies correlate with broken speleothem ages. |

### Brazil / Intraplate

| # | Task | Notes |
|---|------|-------|
| **B1** | Contact UnB seismologists | Prof. Assumpção's group |
| **B5** | Investigate Dandak Cave (India) | 672 CE, z=-1.34, 9 yr recovery |
| **B7** | Check if Lapa Grande extends to 2007 | Modern calibration opportunity |

### Literature & Data

| # | Task | Notes |
|---|------|-------|
| **13** | California tree ring download | ITRDB 1800s |
| **16** | Santo Tomas 8,756 BP investigation | Anti-climatic signature |
| **19** | Manual PDF retrieval | Need #21, #37, #42 |
| **20** | Complete 62-paper literature list | 30/62 indexed (48%) |
| **22** | Investigate 1541-1543 Closani | Romanian archives, NIEP |

### Paleoclimate Cross-Reference

| # | Task | Notes |
|---|------|-------|
| **PC1** | Terminal Classic droughts (871-1021 CE) | Yok Balum validation |
| **PC2** | Bond events | All caves |
| **PC3** | CA medieval megadroughts | Tree rings |

### Long-Recovery Event Review

| # | Task | Notes |
|---|------|-------|
| **LR4** | Check if z>2.0 events have SHORT recovery | May need to demote some events |

### ²³²Th Revisit (Deferred)

| # | Task | Notes |
|---|------|-------|
| **TH6** | Revisit ²³²Th for Paper 2 | Premature (n=18, volcanic not ruled out). Resume when VAL9 complete + multi-cave validation. Data in `methodology/232TH_DATA_ARCHAEOLOGY.md` |

### Ridley Paradox Publication (Optional)

| # | Task | Notes |
|---|------|-------|
| **RP2** | Write full Ridley Paradox section in Paper 2 | Use RIDLEY_PARADOX_REBUTTAL.md |
| **RP-PUB1** | Find 7+ more calibration pairs to reach n=20 | GRL short communication if successful |
| **RP-PUB2** | Find caves in 10-20 J/m³ range | Sharpen detection threshold |
| **RP-PUB3** | Verify Jerusalem West Cave 1927 M6.13 coverage | Entity 152, 52 km |

---

## 🔧 BLOCKERS

| Issue | Notes |
|-------|-------|
| **BT3** | SISAL MCP NA parsing issue - Pozzo Cucù (838), Corchia (669), Dandak (278) blocked |
| **23** | Intermediate-depth attenuation model needs calibration data |

---

## ⏸️ ON HOLD

| Task | Notes |
|------|-------|
| Medieval Infrastructure Records (MR1-MW3) | Needs Italy-based collaborator for archival research |
| 1356 Basel Fabric Roll search | Archival access required |
| Trace element analysis (Sofular, Abaco, Lehman) | Pending data access |
| Future regions (Greece, Japan) | After current regions complete |


### Collaborator Outreach

See `publication/COLLABORATOR_OUTREACH.md` for contact list and templates.

| # | Task | Notes |
|---|------|-------|
| **CO1** | Contact Tom Rockwell (SDSU) | **TOP PRIORITY** - SAF paleoseismologist, dates overlap our findings |
| **CO2** | Contact Driscoll/Zunino/Shen | After Rockwell |
| **TH5** | Contact authors for unpublished ²³²Th data | See `publication/TH232_DATA_CONTACTS.md` |
| **IC7** | Request La Jolla Canyon core radiocarbon | ~1741 Rose Canyon - Paull et al. 2013 |
| **OC1** | Contact Ersek (Northumbria) | 1700 M9.0 coverage |
| **OC2** | Contact Wendt/Heimel (OSU) | 8 new cores |
---


