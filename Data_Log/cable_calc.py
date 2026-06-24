# cable_calc.py — Layer-based spool displacement (corrected)
import math

class CableCalculator:
    def __init__(self, spool_diameter_mm, cable_diameter_mm, ppr=20):
        """
        Initialize for layer-based spool winding.
        
        Each complete rotation adds one full layer; diameter increases by 2×cable_diameter.
        
        Args:
            spool_diameter_mm: Initial spool diameter (mm)
            cable_diameter_mm: Cable thickness/diameter (mm)
            ppr: Pulses per full rotation
        """
        self.spool_diameter_mm = spool_diameter_mm
        self.cable_diameter_mm = cable_diameter_mm
        self.ppr = ppr
    
    def calculate_displacement(self, pulse_count):
        """
        Calculate true cable displacement accounting for growing diameter per layer.
        
        Formula: s = π·N·(d + c·(N-1))
        
        Where:
          N = number of rotations (layers)
          d = initial spool diameter
          c = cable diameter
        
        Args:
            pulse_count: Total encoder pulses since reset
        
        Returns:
            Displacement in mm (float)
        """
        N = pulse_count / self.ppr  # Number of complete rotations
        d = self.spool_diameter_mm
        c = self.cable_diameter_mm
        
        # s = π·N·(d + c·(N-1))
        s = math.pi * N * (d + c * (N - 1))
        return s
    
    def get_current_layer_diameter(self, pulse_count):
        """
        Get the effective spool diameter for the current layer being wound.
        
        Args:
            pulse_count: Total pulses
        
        Returns:
            Diameter in mm (float)
        """
        N = pulse_count / self.ppr
        d = self.spool_diameter_mm
        c = self.cable_diameter_mm
        
        # Current diameter = d + 2c·(N-1)
        # The factor of 2 because cable adds radius on both sides
        current_diameter = d + 2 * c * (N - 1)
        return current_diameter
    
    def estimate_total_layers(self, spool_length_mm):
        """
        Estimate how many layers fit on the spool.
        
        Assumes tight side-by-side winding (no gaps).
        
        Args:
            spool_length_mm: Axial length of spool barrel (mm)
        
        Returns:
            Maximum layers (int)
        """
        max_layers = int(spool_length_mm / self.cable_diameter_mm)
        return max_layers
    
    def calculate_current_layer(self, pulse_count):
        """
        Return which layer is currently being wound.
        
        Args:
            pulse_count: Total pulses
        
        Returns:
            Current layer number (int, 1-indexed)
        """
        N = pulse_count / self.ppr
        return int(N) + 1