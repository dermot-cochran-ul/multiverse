"""Instrumentation primitive types."""
from enum import Enum


class Instrumentation(str, Enum):
    TIMING_JITTER = "timing_jitter"
    EM_HARMONICS = "em_harmonics"
    RADIATION_DOSE = "radiation_dose"
    SPECTRAL_RESIDUE = "spectral_residue"
    GRAVITATIONAL_FLUX = "gravitational_flux"
