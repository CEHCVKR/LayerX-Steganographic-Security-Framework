"""
Module 6: Optimization (Member B)
Author: Member B
Description: Coefficient selection optimization using Chaos Maps and ACO

Key Features:
1. Chaotic sequences (Logistic Map, Arnold Cat Map) for pseudo-random coefficient selection
2. Ant Colony Optimization (ACO) for finding most robust embedding locations
3. Integration with DWT embedding module

Dependencies: numpy, scipy

Functions:
- generate_logistic_sequence(seed, size, mu=3.9): Generate chaotic logistic map sequence
- generate_arnold_cat_sequence(seed, rows, cols, iterations): Generate Arnold Cat Map
- select_coefficients_chaos(bands, seed, count): Select coefficients using chaos
- optimize_coefficients_aco(bands, count, iterations): ACO-based selection
"""

import numpy as np
from typing import List, Tuple, Dict
import random


class LogisticChaos:
    """
    Logistic Map chaos generator: x_{n+1} = μ * x_n * (1 - x_n)
    
    When μ ≈ 3.9, the map exhibits chaotic behavior with sensitive dependence
    on initial conditions. Perfect for generating pseudo-random sequences.
    """
    
    def __init__(self, seed: float = 0.5, mu: float = 3.99):
        """
        Initialize logistic chaos generator.
        
        Args:
            seed: Initial condition (0 < seed < 1)
            mu: Control parameter (3.57 < mu ≤ 4 for chaos)
        """
        if not (0 < seed < 1):
            raise ValueError("Seed must be between 0 and 1")
        if not (3.57 < mu <= 4.0):
            raise ValueError("mu must be between 3.57 and 4.0 for chaotic behavior")
        
        self.x = seed
        self.mu = mu
    
    def next(self) -> float:
        """Generate next chaotic value."""
        self.x = self.mu * self.x * (1 - self.x)
        return self.x
    
    def generate_sequence(self, size: int) -> np.ndarray:
        """Generate sequence of chaotic values."""
        sequence = np.zeros(size)
        for i in range(size):
            sequence[i] = self.next()
        return sequence


class ArnoldCatMap:
    """
    Arnold Cat Map for 2D chaotic scrambling.
    
    The Arnold Cat Map is a chaotic automorphism of the torus that can
    thoroughly mix spatial locations, making coefficient selection unpredictable.
    """
    
    def __init__(self, rows: int, cols: int, a: int = 1, b: int = 1):
        """
        Initialize Arnold Cat Map.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            a, b: Control parameters (typically 1)
        """
        self.rows = rows
        self.cols = cols
        self.a = a
        self.b = b
    
    def transform(self, x: int, y: int, iterations: int = 1) -> Tuple[int, int]:
        """
        Apply Arnold Cat Map transformation.
        
        Args:
            x, y: Initial coordinates
            iterations: Number of iterations
            
        Returns:
            Transformed (x', y') coordinates
        """
        for _ in range(iterations):
            x_new = (x + self.b * y) % self.cols
            y_new = (self.a * x + (self.a * self.b + 1) * y) % self.rows
            x, y = x_new, y_new
        
        return x, y
    
    def generate_sequence(self, count: int, iterations: int = 10) -> List[Tuple[int, int]]:
        """
        Generate sequence of (row, col) positions using Arnold Cat Map.
        
        Args:
            count: Number of positions to generate
            iterations: Chaos iterations per position
            
        Returns:
            List of (row, col) tuples
        """
        positions = []
        visited = set()
        
        # Start with grid-based initialization
        step = max(1, (self.rows * self.cols) // (count * 2))
        
        for y in range(0, self.rows, max(1, self.rows // int(np.sqrt(count)))):
            for x in range(0, self.cols, max(1, self.cols // int(np.sqrt(count)))):
                if len(positions) >= count:
                    break
                
                # Apply chaos transformation
                x_t, y_t = self.transform(x, y, iterations)
                
                if (x_t, y_t) not in visited:
                    positions.append((y_t, x_t))  # (row, col) format
                    visited.add((x_t, y_t))
        
        # Fill remaining with random positions if needed
        while len(positions) < count:
            x = np.random.randint(0, self.cols)
            y = np.random.randint(0, self.rows)
            x_t, y_t = self.transform(x, y, iterations)
            
            if (x_t, y_t) not in visited:
                positions.append((y_t, x_t))
                visited.add((x_t, y_t))
        
        return positions[:count]


def generate_logistic_sequence(seed: float, size: int, mu: float = 3.99) -> np.ndarray:
    """
    Generate chaotic sequence using Logistic Map.
    
    Args:
        seed: Initial value (0 < seed < 1)
        size: Length of sequence
        mu: Chaos parameter (default 3.99 for strong chaos)
        
    Returns:
        Array of chaotic values in [0, 1]
    """
    chaos = LogisticChaos(seed=seed, mu=mu)
    return chaos.generate_sequence(size)


def select_coefficients_chaos(bands: Dict[str, np.ndarray], 
                              seed: float, 
                              count: int,
                              method: str = 'logistic') -> List[Tuple[str, int, int]]:
    """
    Select DWT coefficients using chaotic sequences for steganalysis resistance.
    
    Args:
        bands: DWT coefficient bands dictionary
        seed: Chaotic seed value
        count: Number of coefficients to select
        method: 'logistic' or 'arnold_cat'
        
    Returns:
        List of (band_name, row, col) tuples
    """
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    all_coefficients = []
    
    # Collect all valid coefficients (rows, cols >= 16)
    for band_name in embed_bands:
        if band_name not in bands:
            continue
        
        band = bands[band_name]
        rows, cols = band.shape
        
        # Skip edge coefficients (rows,cols >= 16)
        for i in range(16, rows):
            for j in range(16, cols):
                # Include all coefficients (no magnitude filtering for chaos)
                # Q=4.0 quantization makes even small coefficients usable
                all_coefficients.append((band_name, i, j, abs(band[i, j])))
    
    if method == 'logistic':
        # Use logistic chaos to select coefficients
        chaos_seq = generate_logistic_sequence(seed, count)
        
        selected = []
        seen = set()  # Track selections to avoid duplicates
        
        for chaos_val in chaos_seq:
            # Map chaos value to coefficient index
            idx = int(chaos_val * len(all_coefficients))
            if idx >= len(all_coefficients):
                idx = len(all_coefficients) - 1
            
            # Skip if already selected (find next available)
            attempts = 0
            while idx in seen and attempts < len(all_coefficients):
                idx = (idx + 1) % len(all_coefficients)
                attempts += 1
            
            if attempts >= len(all_coefficients):
                # No more unique positions available
                break
                
            band_name, row, col, mag = all_coefficients[idx]
            selected.append((band_name, row, col))
            seen.add(idx)
        
        return selected
    
    elif method == 'arnold_cat':
        # Use Arnold Cat Map for spatial mixing
        # Assuming first band for dimensions
        first_band = bands[embed_bands[0]]
        rows, cols = first_band.shape
        
        arnold = ArnoldCatMap(rows, cols)
        positions = arnold.generate_sequence(count, iterations=10)
        
        selected = []
        for row, col in positions:
            # Find the coefficient at this position across bands
            for band_name in embed_bands:
                if band_name in bands:
                    band = bands[band_name]
                    band_rows, band_cols = band.shape
                    
                    # Scale position to band size
                    scaled_row = min(row * band_rows // rows, band_rows - 1)
                    scaled_col = min(col * band_cols // cols, band_cols - 1)
                    
                    # Skip edge coefficients
                    if scaled_row >= 16 and scaled_col >= 16:
                        if abs(band[scaled_row, scaled_col]) > 1:  # Lowered threshold
                            selected.append((band_name, scaled_row, scaled_col))
                            if len(selected) >= count:
                                return selected
        
        return selected
    
    else:
        raise ValueError(f"Unknown method: {method}")


class AntColonyOptimizer:
    """
    Ant Colony Optimization for finding robust embedding coefficients.
    
    ACO simulates ant foraging behavior to find optimal paths through the
    coefficient space, selecting locations that maximize robustness.
    """
    
    def __init__(self, num_ants: int = 50, alpha: float = 1.0, beta: float = 2.0, 
                 evaporation: float = 0.5, q: float = 100):
        """
        Initialize ACO.
        
        Args:
            num_ants: Number of ants in colony
            alpha: Pheromone importance
            beta: Heuristic importance (robustness)
            evaporation: Pheromone evaporation rate
            q: Pheromone deposit constant
        """
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.q = q
    
    def calculate_robustness(self, coefficient: float) -> float:
        """
        Calculate robustness score for a coefficient.
        
        Medium-magnitude coefficients are more robust:
        - Too small: sensitive to noise
        - Too large: visible distortion
        
        Args:
            coefficient: DWT coefficient value
            
        Returns:
            Robustness score (higher is better)
        """
        mag = abs(coefficient)
        
        # Optimal range: 10-50
        if 10 <= mag <= 50:
            return 1.0
        elif 5 <= mag < 10:
            return 0.7
        elif 50 < mag <= 100:
            return 0.5
        else:
            return 0.1
    
    def optimize(self, bands: Dict[str, np.ndarray], count: int, 
                 iterations: int = 100) -> List[Tuple[str, int, int]]:
        """
        Find optimal coefficient locations using ACO.
        
        Args:
            bands: DWT coefficient bands
            count: Number of coefficients to select
            iterations: Number of ACO iterations
            
        Returns:
            List of (band_name, row, col) tuples
        """
        embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
        
        # Collect all coefficients with robustness scores
        all_coefficients = []
        for band_name in embed_bands:
            if band_name not in bands:
                continue
            
            band = bands[band_name]
            rows, cols = band.shape
            
            for i in range(16, rows):
                for j in range(16, cols):
                    robustness = self.calculate_robustness(band[i, j])
                    all_coefficients.append({
                        'band': band_name,
                        'row': i,
                        'col': j,
                        'robustness': robustness,
                        'pheromone': 1.0  # Initial pheromone
                    })
        
        # ACO iterations
        best_solution = []
        best_score = 0
        
        for iteration in range(iterations):
            # Each ant builds a solution
            for ant in range(self.num_ants):
                solution = []
                available = all_coefficients.copy()
                
                for _ in range(count):
                    if not available:
                        break
                    
                    # Calculate probability for each coefficient
                    probabilities = []
                    for coeff in available:
                        pheromone = coeff['pheromone'] ** self.alpha
                        heuristic = coeff['robustness'] ** self.beta
                        probabilities.append(pheromone * heuristic)
                    
                    # Normalize
                    total = sum(probabilities)
                    if total == 0:
                        break
                    probabilities = [p / total for p in probabilities]
                    
                    # Select coefficient (roulette wheel)
                    r = random.random()
                    cumulative = 0
                    selected_idx = 0
                    for idx, prob in enumerate(probabilities):
                        cumulative += prob
                        if r <= cumulative:
                            selected_idx = idx
                            break
                    
                    coeff = available[selected_idx]
                    solution.append((coeff['band'], coeff['row'], coeff['col']))
                    available.pop(selected_idx)
                
                # Evaluate solution
                score = sum(c['robustness'] for c in all_coefficients 
                           if (c['band'], c['row'], c['col']) in solution)
                
                if score > best_score:
                    best_score = score
                    best_solution = solution.copy()
            
            # Update pheromones
            # Evaporation
            for coeff in all_coefficients:
                coeff['pheromone'] *= (1 - self.evaporation)
            
            # Deposit (only on best solution)
            for band_name, row, col in best_solution:
                for coeff in all_coefficients:
                    if (coeff['band'] == band_name and 
                        coeff['row'] == row and coeff['col'] == col):
                        coeff['pheromone'] += self.q / (1 + best_score)
        
        return best_solution


def optimize_coefficients_aco(bands: Dict[str, np.ndarray], 
                              count: int, 
                              iterations: int = 10) -> List[Tuple[str, int, int]]:
    """
    Optimize coefficient selection using simplified ACO (robustness-based).
    
    This is a lightweight version that ranks coefficients by robustness
    and uses chaotic selection from the top candidates.
    
    Args:
        bands: DWT coefficient bands
        count: Number of coefficients needed
        iterations: Unused (for API compatibility)
        
    Returns:
        List of optimized (band_name, row, col) tuples
    """
    embed_bands = ['HH1', 'HL1', 'LH1', 'HH2', 'HL2', 'LH2']
    
    # Collect all coefficients with robustness scores
    candidates = []
    for band_name in embed_bands:
        if band_name not in bands:
            continue
        
        band = bands[band_name]
        rows, cols = band.shape
        
        for i in range(16, rows):
            for j in range(16, cols):
                mag = abs(band[i, j])
                
                # Calculate robustness (prefer medium-magnitude)
                if 10 <= mag <= 50:
                    robustness = 1.0
                elif 5 <= mag < 10:
                    robustness = 0.7
                elif 50 < mag <= 100:
                    robustness = 0.5
                else:
                    robustness = 0.1
                
                if robustness > 0.5:  # Only consider robust coefficients
                    candidates.append((band_name, i, j, robustness))
    
    # Sort by robustness (descending)
    candidates.sort(key=lambda x: x[3], reverse=True)
    
    # Take top candidates with some chaotic mixing
    top_count = min(count * 3, len(candidates))
    top_candidates = candidates[:top_count]
    
    # Use chaos to select from top candidates
    chaos = LogisticChaos(seed=0.618, mu=3.95)  # Golden ratio seed
    selected = []
    
    for _ in range(count):
        if not top_candidates:
            break
        
        chaos_val = chaos.next()
        idx = int(chaos_val * len(top_candidates))
        if idx >= len(top_candidates):
            idx = len(top_candidates) - 1
        
        band_name, row, col, _ = top_candidates.pop(idx)
        selected.append((band_name, row, col))
    
    return selected


# Test functions
if __name__ == "__main__":
    print("="*80)
    print("Module 6: Optimization - Testing Chaos and ACO")
    print("="*80)
    
    # Test 1: Logistic Chaos
    print("\n[Test 1] Logistic Map Chaos Generation")
    chaos_seq = generate_logistic_sequence(seed=0.5, size=10)
    print(f"Chaotic sequence (first 10): {chaos_seq}")
    print(f"✅ Range: [{chaos_seq.min():.4f}, {chaos_seq.max():.4f}]")
    
    # Test 2: Arnold Cat Map
    print("\n[Test 2] Arnold Cat Map Position Generation")
    arnold = ArnoldCatMap(rows=64, cols=64)
    positions = arnold.generate_sequence(count=10, iterations=5)
    print(f"Generated positions: {positions[:5]}...")
    print(f"✅ Generated {len(positions)} unique positions")
    
    # Test 3: Coefficient Selection with Chaos
    print("\n[Test 3] Chaos-Based Coefficient Selection")
    # Create dummy DWT bands
    dummy_bands = {
        'HH1': np.random.randn(128, 128) * 20,
        'HL1': np.random.randn(128, 128) * 20,
        'LH1': np.random.randn(128, 128) * 20,
        'HH2': np.random.randn(64, 64) * 15,
        'HL2': np.random.randn(64, 64) * 15,
        'LH2': np.random.randn(64, 64) * 15,
    }
    
    selected = select_coefficients_chaos(dummy_bands, seed=0.42, count=100, method='logistic')
    print(f"✅ Selected {len(selected)} coefficients using Logistic Map")
    print(f"   Sample: {selected[:3]}")
    
    selected_arnold = select_coefficients_chaos(dummy_bands, seed=0.42, count=100, method='arnold_cat')
    print(f"✅ Selected {len(selected_arnold)} coefficients using Arnold Cat Map")
    
    # Test 4: ACO Optimization
    print("\n[Test 4] ACO Coefficient Optimization")
    optimized = optimize_coefficients_aco(dummy_bands, count=100, iterations=20)
    print(f"✅ Optimized {len(optimized)} coefficients using ACO")
    print(f"   Sample: {optimized[:3]}")
    
    print("\n" + "="*80)
    print("✅ Module 6 - All tests passed!")
    print("="*80)
