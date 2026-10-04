"""Physics solvers for spring animations."""
import math

class SpringPhysics:
    """
    Continuous Hooke's Law Spring Solver:
    F = -stiffness * (position - target) - damping * velocity
    Calculates physically-accurate spring dynamics every 8ms (120 FPS).
    """
    def __init__(self, stiffness: float = 180.0, damping: float = 12.0, mass: float = 1.0, initial: float = 1.0):
        self.stiffness = stiffness
        self.damping = damping
        self.mass = mass
        self.current = initial
        self.target = initial
        self.velocity = 0.0
        self.settled_threshold = 0.0005
        self.is_active = False

    def trigger_impulse(self, impulse: float):
        """Attaches a velocity vector to trigger an instant kinetic compress/bounce."""
        self.velocity += impulse
        self.is_active = True

    def set_target(self, target: float):
        self.target = target
        self.is_active = True

    def step(self, dt: float = 0.00833) -> float:
        """Step the spring simulation by dt seconds (0.00833s = ~120 FPS)."""
        if not self.is_active:
            return self.current

        displacement = self.current - self.target
        force = -self.stiffness * displacement - self.damping * self.velocity
        acceleration = force / self.mass

        self.velocity += acceleration * dt
        self.current += self.velocity * dt

        if abs(self.velocity) < self.settled_threshold and abs(self.current - self.target) < self.settled_threshold:
            self.current = self.target
            self.velocity = 0.0
            self.is_active = False

        return self.current

SpringSolver = SpringPhysics

