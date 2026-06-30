# cable_calc.py — Layer-based spool displacement 
import math

class CableCalculator:
    def __init__(self, spool_radius_mm, cable_diameter_mm, ppr=20):
        """
        Initialize for layer-based spool winding.
        
        Each complete rotation adds one full layer; radius increases by `(c/2 pi) * theta
        
        Args:
            spool_radius_mm (s): Spool radius at base (mm)
            cable_diameter_mm (c): Cable thickness/diameter (mm)
            ppr: Pulses per full rotation
        """
        self.spool_radius_mm = spool_radius_mm
        self.cable_diameter_mm = cable_diameter_mm
        self.ppr = ppr
    
    def calculate_displacement(self, pulse_count):
        """
        Calculate true cable displacement accounting for growing radius following
        angle increase, in a helical/spiral path (Archimedean spiral arc length).

        Formula:
            L = ∫[0, 2πN] sqrt(r(θ)² + (dr/dθ)²) dθ

        Where:
            r(θ) = R_core + (d / (2π))·θ      (spiral radius at angle θ)
            dr/dθ = d / (2π)                  (constant radial growth rate)
            R_core = core/spool radius (mm)
            d      = cable diameter, i.e. radial growth per full revolution (mm)
            N      = number of complete rotations (layers)

        Args:
            pulse_count: Total encoder pulses since reset

        Returns:
            Displacement in mm (float)
        """
        N = pulse_count / self.ppr  # Number of complete rotations
        R_core = self.spool_radius_mm
        d = self.cable_diameter_mm

        theta_max = 2 * math.pi * N
        k = d / (2 * math.pi)  # dr/dθ, constant

        def integrand(theta):
            r = R_core + k * theta
            dr_dtheta = k
            return math.sqrt(r * r + dr_dtheta * dr_dtheta)

        # Numerical integration via Simpson's rule (even number of intervals)
        num_intervals = 1000
        if num_intervals % 2 == 1:
            num_intervals += 1

        h = theta_max / num_intervals
        total = integrand(0.0) + integrand(theta_max)

        for i in range(1, num_intervals):
            theta_i = i * h
            weight = 4 if i % 2 == 1 else 2
            total += weight * integrand(theta_i)

        L = (h / 3.0) * total
        return L
    
    def get_current_layer_radius(pulse_count):
        """
        Get the effective spool radius of the current layer being wound.
        
        Args:
            pulse_count: Total pulses
        
        Returns:
            Radius mm (float)
        """
        N = pulse_count / self.ppr
        d = self.spool_radius_mm
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