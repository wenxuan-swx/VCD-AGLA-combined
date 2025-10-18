"""
VCD + AGLA Combined Method - Utility Functions
"""

# Always import VCD noise (no external dependencies)
from .vcd_add_noise import add_diffusion_noise

# Try to import AGLA augmentation (requires LAVIS)
try:
    from .augmentation import augmentation
    __all__ = ['add_diffusion_noise', 'augmentation']
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import augmentation: {e}. AGLA functionality will not be available.")
    __all__ = ['add_diffusion_noise']

