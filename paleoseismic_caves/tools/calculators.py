#!/usr/bin/env python3
"""
Domain calculators for paleoseismic cave research.

Usage from command line:
    python calculators.py pga --mag 6.5 --dist 50 --depth 10
    python calculators.py chiodini --mag 6.0 --dist 30
    python calculators.py energy --mag 7.5 --dist 100 -c 1.0
    python calculators.py connectivity --fault-type onland_strike_slip --geology karst --dist 50
    python calculators.py pore --mag 7.0 --dist 50 --skempton 0.7
    python calculators.py zscore --value -5.8 --mean -4.5 --std 0.8
    python calculators.py haversine --lat1 44.125 --lon1 8.208 --lat2 43.7 --lon2 7.26
    python calculators.py fractionation --temp 15 --mineral calcite
    python calculators.py recurrence --events "1285,1394,1580,1825"
"""

import argparse
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass


# =============================================================================
# PGA ATTENUATION MODELS
# =============================================================================

@dataclass
class PGAResult:
    """Peak Ground Acceleration result with uncertainty."""
    pga_g: float          # PGA in g
    pga_cm_s2: float      # PGA in cm/s²
    sigma: float          # Log-normal standard deviation
    model: str            # Which GMPE was used
    mmi: int              # Estimated Modified Mercalli Intensity

def pga_attenuation(
    magnitude: float,
    distance_km: float,
    depth_km: float = 10.0,
    model: str = "bindi2011",
    vs30: float = 760.0  # Rock site default
) -> PGAResult:
    """
    Calculate Peak Ground Acceleration using various GMPEs.

    Models:
        - bindi2011: Bindi et al. 2011 (Italy, recommended for Mediterranean)
        - boore2014: Boore et al. 2014 NGA-West2 (California)
        - akkar2014: Akkar et al. 2014 (Europe/Middle East)
        - simple: Simple distance decay (for quick estimates)

    Args:
        magnitude: Moment magnitude (Mw)
        distance_km: Epicentral distance in km
        depth_km: Hypocentral depth in km
        model: GMPE model name
        vs30: Shear wave velocity in top 30m (m/s)

    Returns:
        PGAResult with PGA values and uncertainty
    """
    # Hypocentral distance
    r_hyp = math.sqrt(distance_km**2 + depth_km**2)

    if model == "bindi2011":
        # Bindi et al. 2011 for Italy
        # ln(PGA) = a + b*M + c*ln(sqrt(R² + h²)) + site terms
        a, b, c = -2.0, 0.8, -1.5
        h = 6.0  # Reference depth
        r_eff = math.sqrt(r_hyp**2 + h**2)
        ln_pga = a + b * magnitude + c * math.log(r_eff)
        sigma = 0.3

    elif model == "boore2014":
        # Simplified Boore et al. 2014 NGA-West2
        # For Mw > 5, Rjb < 200 km
        c1, c2, c3 = -4.0, 1.1, -1.3
        r_ref = max(1.0, distance_km)  # Avoid log(0)
        ln_pga = c1 + c2 * (magnitude - 6.0) + c3 * math.log(r_ref)
        sigma = 0.28

    elif model == "akkar2014":
        # Akkar et al. 2014 for Europe/Middle East
        a1, a2, a3 = -3.5, 0.9, -1.4
        r_eff = math.sqrt(r_hyp**2 + 25)  # h=5 km reference
        ln_pga = a1 + a2 * magnitude + a3 * math.log(r_eff)
        sigma = 0.32

    else:  # simple
        # Basic empirical: PGA ~ 10^(0.5*M - 1.5*log10(R) - 2)
        r_eff = max(1.0, r_hyp)
        log10_pga = 0.5 * magnitude - 1.5 * math.log10(r_eff) - 2.0
        ln_pga = log10_pga * math.log(10)
        sigma = 0.4

    pga_g = math.exp(ln_pga)
    pga_cm_s2 = pga_g * 980.665

    # Estimate MMI from PGA (Wald et al. 1999)
    if pga_cm_s2 < 1.4:
        mmi = 1
    elif pga_cm_s2 < 3.9:
        mmi = 2
    elif pga_cm_s2 < 9.2:
        mmi = 3
    elif pga_cm_s2 < 18:
        mmi = 4
    elif pga_cm_s2 < 34:
        mmi = 5
    elif pga_cm_s2 < 65:
        mmi = 6
    elif pga_cm_s2 < 124:
        mmi = 7
    elif pga_cm_s2 < 235:
        mmi = 8
    elif pga_cm_s2 < 446:
        mmi = 9
    else:
        mmi = 10

    return PGAResult(
        pga_g=pga_g,
        pga_cm_s2=pga_cm_s2,
        sigma=sigma,
        model=model,
        mmi=mmi
    )


# =============================================================================
# CHIODINI CO2 FLUX MODEL
# =============================================================================

@dataclass
class ChiodiniResult:
    """CO2 flux perturbation result."""
    flux_ratio: float       # Ratio of post/pre-earthquake flux
    perturbation_pct: float # Percentage increase
    duration_years: float   # Expected duration of signal
    detectable: bool        # Whether signal should be detectable in speleothem

def chiodini_co2_flux(
    magnitude: float,
    distance_km: float,
    baseline_flux: float = 1.0  # Normalized
) -> ChiodiniResult:
    """
    Estimate CO2 flux perturbation from earthquake-induced fracturing.

    Based on Chiodini et al. observations of CO2 flux changes after
    Italian earthquakes, particularly Irpinia 1980 and L'Aquila 2009.

    The model assumes:
    - Earthquakes create/reopen fractures
    - Deep CO2 escapes through new pathways
    - Flux enhancement decays exponentially

    Args:
        magnitude: Earthquake magnitude (Mw)
        distance_km: Distance from rupture to cave
        baseline_flux: Pre-earthquake CO2 flux (normalized)

    Returns:
        ChiodiniResult with flux enhancement estimates
    """
    # Empirical scaling from Chiodini observations
    # Flux enhancement ~ 10^(0.4*M) / R^1.5
    # Detectable perturbations observed up to ~100 km for M7+

    if distance_km < 1:
        distance_km = 1  # Minimum distance

    # Magnitude scaling (exponential)
    mag_factor = 10 ** (0.4 * (magnitude - 5.0))

    # Distance decay
    dist_factor = (30.0 / distance_km) ** 1.5

    # Combined perturbation
    perturbation = mag_factor * dist_factor
    flux_ratio = 1.0 + perturbation

    # Duration scales with magnitude (larger EQ = longer perturbation)
    # M5 ~ 2 years, M7 ~ 20 years (logarithmic scaling)
    duration = 2.0 * 10 ** (0.5 * (magnitude - 5.0))

    # Detectability threshold (~10% change needed for speleothem signal)
    detectable = perturbation > 0.1

    return ChiodiniResult(
        flux_ratio=flux_ratio,
        perturbation_pct=perturbation * 100,
        duration_years=duration,
        detectable=detectable
    )


# =============================================================================
# SEISMIC ENERGY DENSITY (Wang & Manga 2010)
# =============================================================================

@dataclass
class SeismicEnergyResult:
    """Seismic energy density result for groundwater response prediction."""
    raw_energy_jm3: float      # Raw seismic energy density (J/m³)
    effective_energy_jm3: float # Effective energy with connectivity
    connectivity: float         # Aquifer connectivity coefficient (0-1)
    threshold_jm3: float       # Detection threshold
    threshold_exceeded: bool   # Whether threshold is exceeded
    ratio_to_threshold: float  # How many times above/below threshold

def seismic_energy_density(
    magnitude: float,
    distance_km: float,
    connectivity: float = 1.0
) -> SeismicEnergyResult:
    """
    Calculate seismic energy density using Wang & Manga (2010) formula.

    This provides the physical basis for predicting groundwater responses
    to earthquakes. The model is based on empirical observations showing
    sustained groundwater changes require e > 10⁻³ J/m³.

    Formula: log₁₀(e) = -2.0 + M - 2.0 × log₁₀(R)

    The connectivity coefficient accounts for the 1976/2012 null results
    at Yok Balum: both on-land (100 km) and offshore (200 km) M7.4-7.5
    earthquakes produced NO signal. This proves that energy density alone
    doesn't determine detectability - aquifer connectivity matters.

    Args:
        magnitude: Moment magnitude (Mw)
        distance_km: Distance from epicenter in km
        connectivity: Aquifer connectivity coefficient (0-1)
            - 0: No aquifer connection (offshore, isolated aquifer)
            - 0.1-0.3: Weak connection (distant fault, sedimentary barrier)
            - 0.7-1.0: Strong connection (fault intersects aquifer, karst)

    Returns:
        SeismicEnergyResult with energy calculations and threshold comparison

    Reference:
        Wang, C.-Y. and Manga, M. (2010). Hydrologic responses to earthquakes
        and a general metric. Geofluids, 10(1-2), 206-216.
    """
    if distance_km < 1:
        distance_km = 1  # Minimum distance to avoid log(0)

    # Wang & Manga (2010) seismic energy density formula
    log_e = -2.0 + magnitude - 2.0 * math.log10(distance_km)
    raw_energy = 10 ** log_e

    # Apply connectivity coefficient
    effective_energy = raw_energy * connectivity

    # Threshold for sustained groundwater changes (Wang & Manga 2010)
    threshold = 1e-3  # 10⁻³ J/m³

    return SeismicEnergyResult(
        raw_energy_jm3=raw_energy,
        effective_energy_jm3=effective_energy,
        connectivity=connectivity,
        threshold_jm3=threshold,
        threshold_exceeded=effective_energy > threshold,
        ratio_to_threshold=effective_energy / threshold
    )


def detection_distance_limit(
    magnitude: float,
    connectivity: float = 1.0,
    threshold: float = 1e-3
) -> float:
    """
    Calculate maximum distance at which an earthquake can be detected.

    Solves: threshold = 10^(-2 + M - 2*log10(R)) * C
    For R: R = 10^((M - 2 - log10(threshold/C)) / 2)

    Args:
        magnitude: Earthquake magnitude
        connectivity: Aquifer connectivity (0-1)
        threshold: Detection threshold in J/m³

    Returns:
        Maximum detection distance in km
    """
    if connectivity <= 0:
        return 0.0

    # Solve for R from energy density equation
    log_r = (magnitude - 2.0 - math.log10(threshold / connectivity)) / 2.0
    return 10 ** log_r


# =============================================================================
# AQUIFER CONNECTIVITY MODEL
# =============================================================================

@dataclass
class AquiferConnectivityResult:
    """Aquifer connectivity assessment result."""
    connectivity: float          # Combined connectivity coefficient (0-1)
    fault_factor: float          # Fault type contribution
    geology_factor: float        # Rock type contribution
    distance_factor: float       # Distance contribution
    confidence: str              # Assessment confidence level
    explanation: str             # Human-readable explanation

def aquifer_connectivity(
    fault_type: str,
    geology: str,
    distance_km: float,
    fault_intersects_aquifer: bool = False
) -> AquiferConnectivityResult:
    """
    Estimate aquifer connectivity coefficient based on physical factors.

    This model was developed to explain the "Ridley Paradox" at Yok Balum:
    - 1976 M7.5 (on-land, 100 km): NO signal
    - 2012 M7.4 (offshore, 200 km): NO signal
    - 620 CE (hypothesized local fault): 46-year signal

    The key insight is that energy density alone doesn't determine detectability.
    A fault must have a hydraulic pathway to the cave's aquifer system.

    Args:
        fault_type: Type of fault mechanism
            - "offshore_subduction": Subduction zone (C ~ 0.05-0.1)
            - "onland_strike_slip": Strike-slip on land (C ~ 0.3-0.5)
            - "onland_normal": Normal fault on land (C ~ 0.4-0.6)
            - "local_karst": Fault within karst aquifer system (C ~ 0.8-1.0)
        geology: Rock type between fault and cave
            - "sedimentary_basin": Low permeability sediments (factor 0.3)
            - "crystalline": Fractured crystalline rock (factor 0.5)
            - "karst": Karstified limestone (factor 0.9)
            - "same_aquifer": Fault in same aquifer as cave (factor 1.0)
        distance_km: Distance from fault to cave in km
        fault_intersects_aquifer: Does fault directly cut through the aquifer?

    Returns:
        AquiferConnectivityResult with connectivity estimate and explanation

    Reference:
        Developed for this project based on:
        - Wang & Manga (2010) - energy density threshold
        - Yok Balum 1976/2012 null results
        - Bàsura 1887 offshore null result
    """
    # Fault type factors (empirical)
    fault_factors = {
        "offshore_subduction": 0.05,
        "offshore_transform": 0.1,
        "onland_strike_slip": 0.4,
        "onland_normal": 0.5,
        "onland_thrust": 0.45,
        "local_karst": 0.9,
    }
    fault_factor = fault_factors.get(fault_type.lower(), 0.3)

    # Geology factors
    geology_factors = {
        "sedimentary_basin": 0.3,
        "crystalline": 0.5,
        "fractured": 0.6,
        "karst": 0.9,
        "same_aquifer": 1.0,
    }
    geology_factor = geology_factors.get(geology.lower(), 0.5)

    # Distance factor (inverse relationship)
    # At 0 km (direct intersection): factor = 1.0
    # At 50 km: factor ~ 0.5
    # At 100 km: factor ~ 0.3
    # At 200 km: factor ~ 0.2
    if distance_km < 1:
        distance_factor = 1.0
    else:
        distance_factor = 1.0 / (1.0 + 0.02 * distance_km)

    # Direct aquifer intersection overrides distance
    if fault_intersects_aquifer:
        distance_factor = 1.0
        fault_factor = max(fault_factor, 0.9)

    # Combined connectivity (geometric mean of factors)
    connectivity = (fault_factor * geology_factor * distance_factor) ** (1/3)
    connectivity = min(1.0, max(0.0, connectivity))  # Clamp to 0-1

    # Direct intersection bonus
    if fault_intersects_aquifer:
        connectivity = min(1.0, connectivity * 1.5)

    # Confidence assessment
    if fault_intersects_aquifer or distance_km < 20:
        confidence = "HIGH"
    elif distance_km < 50:
        confidence = "MODERATE"
    else:
        confidence = "LOW"

    # Generate explanation
    explanations = []
    if connectivity > 0.7:
        explanations.append("Strong hydraulic connection expected")
    elif connectivity > 0.3:
        explanations.append("Moderate hydraulic connection possible")
    else:
        explanations.append("Weak/no hydraulic connection")

    if fault_intersects_aquifer:
        explanations.append("fault directly intersects aquifer")
    if geology.lower() == "karst":
        explanations.append("karst enhances connectivity")
    if fault_type.lower().startswith("offshore"):
        explanations.append("offshore faults typically disconnected")

    return AquiferConnectivityResult(
        connectivity=connectivity,
        fault_factor=fault_factor,
        geology_factor=geology_factor,
        distance_factor=distance_factor,
        confidence=confidence,
        explanation="; ".join(explanations)
    )


# =============================================================================
# PORE PRESSURE PERTURBATION (Skempton-based)
# =============================================================================

@dataclass
class PorePressureResult:
    """Pore pressure perturbation result."""
    delta_p_pa: float           # Pressure change in Pascals
    delta_p_kpa: float          # Pressure change in kPa
    delta_p_bar: float          # Pressure change in bar
    static_stress_pa: float     # Static stress change (Coulomb)
    skempton_b: float           # Skempton's B coefficient used
    detectable: bool            # Whether perturbation is significant

def pore_pressure_perturbation(
    magnitude: float,
    distance_km: float,
    skempton_b: float = 0.7,
    shear_modulus_gpa: float = 30.0
) -> PorePressureResult:
    """
    Estimate pore pressure perturbation from earthquake-induced stress changes.

    This model combines:
    1. Static stress change estimation (Coulomb stress)
    2. Skempton's equation for pore pressure response

    The Skempton equation: Δp = B × Δσ_mean
    where B is the Skempton coefficient (0.5-1.0 for most rocks)

    Args:
        magnitude: Earthquake magnitude (Mw)
        distance_km: Distance from fault in km
        skempton_b: Skempton's B coefficient (default 0.7)
            - 0.5-0.6: Stiff rocks
            - 0.7-0.8: Typical fractured rocks
            - 0.9-1.0: Soft sediments
        shear_modulus_gpa: Shear modulus in GPa (default 30 for crust)

    Returns:
        PorePressureResult with pressure perturbation estimates

    Reference:
        Skempton, A.W. (1954). The pore-pressure coefficients A and B.
        Géotechnique, 4(4), 143-147.

        Manga, M. and Wang, C.-Y. (2007). Earthquake hydrology.
        Treatise on Geophysics, 4, 293-320.
    """
    if distance_km < 1:
        distance_km = 1

    # Estimate seismic moment
    # M0 = 10^(1.5*Mw + 9.1) in N·m
    moment_nm = 10 ** (1.5 * magnitude + 9.1)

    # Estimate rupture area from moment
    # M0 = μ × A × D, where μ = shear modulus, A = area, D = slip
    # Empirically: A ~ M0 / (μ × D_avg)
    # For simplicity, use Wells & Coppersmith: log10(A) = M - 4.0
    rupture_area_km2 = 10 ** (magnitude - 4.0)
    rupture_area_m2 = rupture_area_km2 * 1e6

    # Estimate average slip
    slip_m = 10 ** (-4.80 + 0.69 * magnitude)

    # Static stress change at distance R (simplified Okada model)
    # Δσ ~ μ × D / R for far field
    # More accurately: Δσ ~ M0 / (4π × R³) for point source approximation
    shear_modulus_pa = shear_modulus_gpa * 1e9
    distance_m = distance_km * 1000

    # Static stress change (simplified, order of magnitude)
    # Δσ_static ~ M0 / (4π × R³) for mean stress
    static_stress_pa = moment_nm / (4 * math.pi * distance_m ** 3)

    # Pore pressure change via Skempton equation
    # Δp = B × Δσ_mean
    delta_p_pa = skempton_b * static_stress_pa
    delta_p_kpa = delta_p_pa / 1000
    delta_p_bar = delta_p_pa / 1e5

    # Detectability threshold (~1 kPa for measurable groundwater response)
    detectable = delta_p_kpa > 1.0

    return PorePressureResult(
        delta_p_pa=delta_p_pa,
        delta_p_kpa=delta_p_kpa,
        delta_p_bar=delta_p_bar,
        static_stress_pa=static_stress_pa,
        skempton_b=skempton_b,
        detectable=detectable
    )


# =============================================================================
# ISOTOPE CALCULATIONS
# =============================================================================

def isotope_fractionation(
    temperature_c: float,
    mineral: str = "calcite"
) -> float:
    """
    Calculate oxygen isotope fractionation factor (1000*ln(alpha)).

    Based on Kim & O'Neil (1997) for calcite, Friedman & O'Neil (1977) for water.

    Args:
        temperature_c: Temperature in Celsius
        mineral: 'calcite' or 'aragonite'

    Returns:
        1000 * ln(alpha) fractionation factor
    """
    T_kelvin = temperature_c + 273.15

    if mineral.lower() == "calcite":
        # Kim & O'Neil 1997
        # 1000*ln(alpha) = 18.03 * (10^3 / T) - 32.42
        alpha_1000ln = 18.03 * (1000.0 / T_kelvin) - 32.42
    elif mineral.lower() == "aragonite":
        # Grossman & Ku 1986
        alpha_1000ln = 18.56 * (1000.0 / T_kelvin) - 33.49
    else:
        raise ValueError(f"Unknown mineral: {mineral}")

    return alpha_1000ln


def delta_to_temperature(
    delta18o_calcite: float,
    delta18o_water: float = -7.0,  # Typical meteoric water
    mineral: str = "calcite"
) -> float:
    """
    Estimate formation temperature from delta-18O values.

    Args:
        delta18o_calcite: δ18O of calcite (‰ VPDB)
        delta18o_water: δ18O of drip water (‰ VSMOW)
        mineral: 'calcite' or 'aragonite'

    Returns:
        Estimated temperature in Celsius
    """
    # Convert VPDB to VSMOW: δ18O_VSMOW = 1.03091 * δ18O_VPDB + 30.91
    delta18o_calcite_vsmow = 1.03091 * delta18o_calcite + 30.91

    # Solve fractionation equation for T
    # For calcite: 1000*ln(alpha) = 18.03 * (10^3 / T) - 32.42
    # alpha ≈ (1000 + δ_calcite) / (1000 + δ_water)

    alpha = (1000 + delta18o_calcite_vsmow) / (1000 + delta18o_water)
    ln_alpha_1000 = 1000 * math.log(alpha)

    # Solve: ln_alpha_1000 = 18.03 * (1000/T) - 32.42
    # T = 18030 / (ln_alpha_1000 + 32.42)
    T_kelvin = 18030.0 / (ln_alpha_1000 + 32.42)
    T_celsius = T_kelvin - 273.15

    return T_celsius


# =============================================================================
# STATISTICAL UTILITIES
# =============================================================================

def zscore(value: float, mean: float, std: float) -> float:
    """Calculate Z-score."""
    if std == 0:
        return 0.0
    return (value - mean) / std


def zscore_series(values: List[float]) -> Tuple[List[float], float, float]:
    """
    Calculate Z-scores for a series.

    Returns:
        Tuple of (z_scores, mean, std)
    """
    n = len(values)
    if n == 0:
        return [], 0.0, 0.0

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std = math.sqrt(variance)

    if std == 0:
        return [0.0] * n, mean, 0.0

    z_scores = [(x - mean) / std for x in values]
    return z_scores, mean, std


def recurrence_interval(event_dates: List[float]) -> Tuple[float, float, List[float]]:
    """
    Calculate recurrence interval statistics from event dates.

    Args:
        event_dates: List of event dates (years CE)

    Returns:
        Tuple of (mean_interval, std_interval, intervals)
    """
    if len(event_dates) < 2:
        return 0.0, 0.0, []

    sorted_dates = sorted(event_dates)
    intervals = [sorted_dates[i+1] - sorted_dates[i]
                 for i in range(len(sorted_dates) - 1)]

    mean_int = sum(intervals) / len(intervals)
    variance = sum((x - mean_int) ** 2 for x in intervals) / len(intervals)
    std_int = math.sqrt(variance)

    return mean_int, std_int, intervals


# =============================================================================
# GEOGRAPHIC UTILITIES
# =============================================================================

def haversine(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate great-circle distance between two points.

    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def bearing(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate initial bearing from point 1 to point 2.

    Returns:
        Bearing in degrees (0-360, clockwise from north)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)

    return (bearing_deg + 360) % 360


# =============================================================================
# SEISMIC UTILITIES
# =============================================================================

def magnitude_to_rupture_length(magnitude: float) -> float:
    """
    Estimate rupture length from magnitude (Wells & Coppersmith 1994).

    Args:
        magnitude: Moment magnitude

    Returns:
        Estimated rupture length in km
    """
    # log10(L) = -3.22 + 0.69*M (all fault types)
    log_L = -3.22 + 0.69 * magnitude
    return 10 ** log_L


def magnitude_to_slip(magnitude: float) -> float:
    """
    Estimate average slip from magnitude (Wells & Coppersmith 1994).

    Args:
        magnitude: Moment magnitude

    Returns:
        Estimated average slip in meters
    """
    # log10(D) = -4.80 + 0.69*M (all fault types)
    log_D = -4.80 + 0.69 * magnitude
    return 10 ** log_D


def moment_to_magnitude(moment_nm: float) -> float:
    """
    Convert seismic moment to moment magnitude.

    Args:
        moment_nm: Seismic moment in Newton-meters

    Returns:
        Moment magnitude (Mw)
    """
    # Mw = (2/3) * log10(M0) - 6.06
    return (2.0 / 3.0) * math.log10(moment_nm) - 6.06


def magnitude_to_moment(magnitude: float) -> float:
    """
    Convert moment magnitude to seismic moment.

    Args:
        magnitude: Moment magnitude (Mw)

    Returns:
        Seismic moment in Newton-meters
    """
    # M0 = 10^(1.5*Mw + 9.1)
    return 10 ** (1.5 * magnitude + 9.1)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Paleoseismic domain calculators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Calculator to run")

    # PGA calculator
    pga_parser = subparsers.add_parser("pga", help="PGA attenuation")
    pga_parser.add_argument("--mag", type=float, required=True, help="Magnitude")
    pga_parser.add_argument("--dist", type=float, required=True, help="Distance (km)")
    pga_parser.add_argument("--depth", type=float, default=10.0, help="Depth (km)")
    pga_parser.add_argument("--model", default="bindi2011",
                           choices=["bindi2011", "boore2014", "akkar2014", "simple"])

    # Chiodini CO2 flux
    co2_parser = subparsers.add_parser("chiodini", help="CO2 flux perturbation")
    co2_parser.add_argument("--mag", type=float, required=True, help="Magnitude")
    co2_parser.add_argument("--dist", type=float, required=True, help="Distance (km)")

    # Z-score
    z_parser = subparsers.add_parser("zscore", help="Calculate Z-score")
    z_parser.add_argument("--value", type=float, required=True)
    z_parser.add_argument("--mean", type=float, required=True)
    z_parser.add_argument("--std", type=float, required=True)

    # Haversine distance
    dist_parser = subparsers.add_parser("haversine", help="Great-circle distance")
    dist_parser.add_argument("--lat1", type=float, required=True)
    dist_parser.add_argument("--lon1", type=float, required=True)
    dist_parser.add_argument("--lat2", type=float, required=True)
    dist_parser.add_argument("--lon2", type=float, required=True)

    # Fractionation
    frac_parser = subparsers.add_parser("fractionation", help="Isotope fractionation")
    frac_parser.add_argument("--temp", type=float, required=True, help="Temperature (C)")
    frac_parser.add_argument("--mineral", default="calcite", choices=["calcite", "aragonite"])

    # Recurrence
    rec_parser = subparsers.add_parser("recurrence", help="Recurrence interval")
    rec_parser.add_argument("--events", type=str, required=True,
                           help="Comma-separated event dates")

    # Rupture parameters
    rup_parser = subparsers.add_parser("rupture", help="Rupture parameters from magnitude")
    rup_parser.add_argument("--mag", type=float, required=True, help="Magnitude")

    # Seismic energy density (Wang & Manga 2010)
    sed_parser = subparsers.add_parser("energy", help="Seismic energy density (Wang & Manga 2010)")
    sed_parser.add_argument("--mag", type=float, required=True, help="Magnitude")
    sed_parser.add_argument("--dist", type=float, required=True, help="Distance (km)")
    sed_parser.add_argument("--connectivity", "-c", type=float, default=1.0,
                           help="Aquifer connectivity (0-1, default 1.0)")

    # Aquifer connectivity
    conn_parser = subparsers.add_parser("connectivity", help="Estimate aquifer connectivity")
    conn_parser.add_argument("--fault-type", type=str, required=True,
                            choices=["offshore_subduction", "offshore_transform",
                                    "onland_strike_slip", "onland_normal",
                                    "onland_thrust", "local_karst"],
                            help="Fault mechanism type")
    conn_parser.add_argument("--geology", type=str, required=True,
                            choices=["sedimentary_basin", "crystalline", "fractured",
                                    "karst", "same_aquifer"],
                            help="Rock type between fault and cave")
    conn_parser.add_argument("--dist", type=float, required=True, help="Distance (km)")
    conn_parser.add_argument("--intersects", action="store_true",
                            help="Fault intersects aquifer directly")

    # Pore pressure perturbation
    pore_parser = subparsers.add_parser("pore", help="Pore pressure perturbation (Skempton)")
    pore_parser.add_argument("--mag", type=float, required=True, help="Magnitude")
    pore_parser.add_argument("--dist", type=float, required=True, help="Distance (km)")
    pore_parser.add_argument("--skempton", "-b", type=float, default=0.7,
                            help="Skempton B coefficient (0.5-1.0, default 0.7)")

    args = parser.parse_args()

    if args.command == "pga":
        result = pga_attenuation(args.mag, args.dist, args.depth, args.model)
        print(f"PGA Attenuation ({result.model})")
        print(f"  Magnitude:    {args.mag}")
        print(f"  Distance:     {args.dist} km")
        print(f"  Depth:        {args.depth} km")
        print(f"  ---")
        print(f"  PGA:          {result.pga_g:.4f} g ({result.pga_cm_s2:.1f} cm/s²)")
        print(f"  Sigma:        {result.sigma:.2f}")
        print(f"  Est. MMI:     {result.mmi}")

    elif args.command == "chiodini":
        result = chiodini_co2_flux(args.mag, args.dist)
        print(f"Chiodini CO2 Flux Model")
        print(f"  Magnitude:      {args.mag}")
        print(f"  Distance:       {args.dist} km")
        print(f"  ---")
        print(f"  Flux ratio:     {result.flux_ratio:.2f}x")
        print(f"  Perturbation:   +{result.perturbation_pct:.1f}%")
        print(f"  Duration:       ~{result.duration_years:.1f} years")
        print(f"  Detectable:     {'YES' if result.detectable else 'NO'}")

    elif args.command == "zscore":
        z = zscore(args.value, args.mean, args.std)
        print(f"Z-score: {z:+.3f}σ")

    elif args.command == "haversine":
        d = haversine(args.lat1, args.lon1, args.lat2, args.lon2)
        b = bearing(args.lat1, args.lon1, args.lat2, args.lon2)
        print(f"Distance: {d:.1f} km")
        print(f"Bearing:  {b:.1f}°")

    elif args.command == "fractionation":
        alpha = isotope_fractionation(args.temp, args.mineral)
        print(f"1000*ln(α) for {args.mineral} at {args.temp}°C: {alpha:.2f}‰")

    elif args.command == "recurrence":
        events = [float(x.strip()) for x in args.events.split(",")]
        mean_int, std_int, intervals = recurrence_interval(events)
        print(f"Events: {sorted(events)}")
        print(f"Intervals: {intervals}")
        print(f"Mean recurrence: {mean_int:.1f} ± {std_int:.1f} years")
        if len(events) >= 2:
            last_event = max(events)
            years_since = 2025 - last_event
            print(f"Years since last: {years_since:.0f}")
            print(f"Percent of cycle: {100*years_since/mean_int:.0f}%")

    elif args.command == "rupture":
        length = magnitude_to_rupture_length(args.mag)
        slip = magnitude_to_slip(args.mag)
        moment = magnitude_to_moment(args.mag)
        print(f"Rupture Parameters for Mw {args.mag}")
        print(f"  Length:  {length:.1f} km")
        print(f"  Slip:    {slip:.2f} m")
        print(f"  Moment:  {moment:.2e} N·m")

    elif args.command == "energy":
        result = seismic_energy_density(args.mag, args.dist, args.connectivity)
        max_dist = detection_distance_limit(args.mag, args.connectivity)
        print(f"Seismic Energy Density (Wang & Manga 2010)")
        print(f"  Magnitude:      {args.mag}")
        print(f"  Distance:       {args.dist} km")
        print(f"  Connectivity:   {args.connectivity}")
        print(f"  ---")
        print(f"  Raw energy:     {result.raw_energy_jm3:.3e} J/m³")
        print(f"  Effective:      {result.effective_energy_jm3:.3e} J/m³")
        print(f"  Threshold:      {result.threshold_jm3:.0e} J/m³")
        print(f"  Ratio:          {result.ratio_to_threshold:.1f}× threshold")
        print(f"  Detectable:     {'YES' if result.threshold_exceeded else 'NO'}")
        print(f"  Max det. dist:  {max_dist:.0f} km")

    elif args.command == "connectivity":
        result = aquifer_connectivity(
            args.fault_type, args.geology, args.dist, args.intersects
        )
        print(f"Aquifer Connectivity Model")
        print(f"  Fault type:     {args.fault_type}")
        print(f"  Geology:        {args.geology}")
        print(f"  Distance:       {args.dist} km")
        print(f"  Intersects:     {'YES' if args.intersects else 'NO'}")
        print(f"  ---")
        print(f"  Fault factor:   {result.fault_factor:.2f}")
        print(f"  Geology factor: {result.geology_factor:.2f}")
        print(f"  Distance factor:{result.distance_factor:.2f}")
        print(f"  ---")
        print(f"  Connectivity:   {result.connectivity:.2f}")
        print(f"  Confidence:     {result.confidence}")
        print(f"  Assessment:     {result.explanation}")

    elif args.command == "pore":
        result = pore_pressure_perturbation(args.mag, args.dist, args.skempton)
        print(f"Pore Pressure Perturbation (Skempton Model)")
        print(f"  Magnitude:      {args.mag}")
        print(f"  Distance:       {args.dist} km")
        print(f"  Skempton B:     {args.skempton}")
        print(f"  ---")
        print(f"  Static stress:  {result.static_stress_pa:.2e} Pa")
        print(f"  Δ Pressure:     {result.delta_p_kpa:.3f} kPa ({result.delta_p_bar:.4f} bar)")
        print(f"  Detectable:     {'YES' if result.detectable else 'NO'} (threshold: 1 kPa)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
