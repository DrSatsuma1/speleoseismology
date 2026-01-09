# Independent Verification Request: USGS Fault Database Gap Analysis

## Claim to Verify

The USGS Quaternary Fault and Fold Database contains an ~85 km unmapped gap in the Newport-Inglewood-Rose Canyon fault zone between:
- **South end**: south Los Angeles Basin section (ends ~33.62°N)
- **North end**: San Diego section (starts ~32.85°N)

This gap represents approximately 40% of the total 209 km fault system.

## Data Sources for Verification

1. **USGS Quaternary Fault and Fold Database**
   - Interactive Map: https://earthquake.usgs.gov/static/lfs/nshm/qfaults/
   - Download: https://earthquake.usgs.gov/nshmp/qfaults.zip
   - Fault ID: 127 (Newport-Inglewood-Rose Canyon fault zone)

2. **USGS Fault Summary Report**
   - https://earthquake.usgs.gov/cfusion/qfault/show_report_AB_archive.cfm?fault_id=127

3. **Published Literature**
   - CGS FER 265 (2021): "Point Loma and La Jolla Fault Evaluation Report"
   - Sahakian et al. (2017): "Seismic reflection imaging of subsurface deformation in the northern Newport‐Inglewood/Rose Canyon fault zone" - https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2016JB013467

## Questions to Answer

1. **Database Section Count**: How many sections of the Newport-Inglewood-Rose Canyon fault zone are in the USGS database? What are their names?

2. **Geographic Extent**: For each section, what are the latitude boundaries (northernmost and southernmost points)?

3. **Gap Identification**: Is there a geographic gap between any sections? If so:
   - What is the latitude range of the gap?
   - Approximately how many kilometers is this gap (use ~111 km per degree of latitude)?

4. **Fault System Length**: What is the total documented length of the Newport-Inglewood-Rose Canyon fault system according to:
   - USGS database sections (sum of mapped segments)
   - Published literature (total system length including offshore)

5. **Offshore vs Onshore**: Does the USGS database include offshore portions of this fault system, or only onshore segments?

## Methodology Suggestions

- Download the USGS shapefile and examine it in GIS software OR use the interactive web map
- Extract section boundaries and calculate gaps
- Cross-reference with published fault length estimates
- Look for any fault naming variations (e.g., is the gap mapped under a different fault name?)

## Expected Output

Please provide:
1. Clear yes/no answer: Is there an ~85 km gap in the USGS database between sections?
2. Your calculated gap size (if gap exists)
3. Percentage of total fault system that is unmapped in the USGS database
4. Any alternative explanations (e.g., gap mapped under different name, intentional exclusion, etc.)

## Context (Do Not Let This Bias Your Analysis)

This analysis arose from overlaying microseismicity (1980-2025) on the USGS fault database and finding that 47.6% of earthquakes occurred in a region where no faults are mapped in the database. We want to verify whether this represents:
- A real gap in the database (offshore segments not included)
- A data processing error on our part
- Fault segments mapped under different names

Please conduct your analysis independently before comparing to these expectations.
