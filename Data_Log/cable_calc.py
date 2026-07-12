# cable_calc.py
import math


class CableCalculator:
    def __init__(
        self,
        initial_radius_mm=None,
        line_thickness_mm=None,
        ppr=20,
        spool_diameter_mm=None,
        cable_diameter_mm=None,
    ):
        """
        Initialize a calculator for the exact length of a line wound onto a sheave.

        Args:
            initial_radius_mm: Initial radius of the sheave in millimeters.
            line_thickness_mm: Thickness of the line in millimeters.
            ppr: Pulses per full rotation of the encoder.
            spool_diameter_mm: Backward-compatible alias for the initial spool diameter.
            cable_diameter_mm: Backward-compatible alias for line thickness.
        """
        if initial_radius_mm is None:
            if spool_diameter_mm is not None:
                initial_radius_mm = spool_diameter_mm / 2.0
            else:
                initial_radius_mm = 0.0

        if line_thickness_mm is None:
            line_thickness_mm = cable_diameter_mm if cable_diameter_mm is not None else 0.0

        self.initial_radius_mm = float(initial_radius_mm)
        self.line_thickness_mm = float(line_thickness_mm)
        self.spool_diameter_mm = self.initial_radius_mm * 2.0
        self.cable_diameter_mm = self.line_thickness_mm
        self.ppr = ppr

    @staticmethod
    def _radial_growth_rate(line_thickness_mm):
        """Return the radial growth rate per radian for an Archimedean spiral."""
        return line_thickness_mm / (2.0 * math.pi)

    def _spiral_length(self, theta, initial_radius_mm=None, line_thickness_mm=None):
        """Calculate the exact spiral arc length for the given total angle change."""
        if theta == 0:
            return 0.0

        a = self.initial_radius_mm if initial_radius_mm is None else float(initial_radius_mm)
        b = self._radial_growth_rate(
            self.line_thickness_mm if line_thickness_mm is None else float(line_thickness_mm)
        ) 

        if b == 0.0:
            return abs(theta) * a

        r = a + b * theta
        sqrt_term = math.sqrt(b * b + r * r)
        a_sqrt_term = math.sqrt(b * b + a * a)
        ratio = (r + sqrt_term) / (a + a_sqrt_term)

        return (r * sqrt_term - a * a_sqrt_term + (b * b) * math.log(ratio)) / (2.0 * b)

    def calculate_line_length(self, theta=None, rotations=None, initial_radius_mm=None, line_thickness_mm=None):
        """
        Calculate the exact length of the line spooled onto the sheave.

        Args:
            theta: Total angle change in radians. If omitted, rotations is used.
            rotations: Number of full rotations. Used when theta is not provided.
            initial_radius_mm: Optional override for the initial sheave radius.
            line_thickness_mm: Optional override for the line thickness.

        Returns:
            Exact line length in millimeters.
        """
        if theta is None:
            if rotations is None:
                raise ValueError("Either theta or rotations must be provided.")
            theta = 2.0 * math.pi * abs(float(rotations))
        else:
            theta = abs(float(theta))

        return self._spiral_length(
            theta,
            initial_radius_mm=initial_radius_mm,
            line_thickness_mm=line_thickness_mm,
        )

    def calculate_displacement(self, pulse_count):
        """
        Convert encoder pulse count into the exact spooled line length.

        Args:
            pulse_count: Total encoder pulses since reset.

        Returns:
            Exact line length in millimeters.
        """
        rotations = pulse_count / self.ppr
        return self.calculate_line_length(rotations=rotations)