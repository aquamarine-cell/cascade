"""Example Python file for Cascade analysis."""


def fibonacci(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    
    return sequence


class DataProcessor:
    """Process and transform data."""
    
    def __init__(self, data):
        self.data = data
        self.processed = False
    
    def normalize(self):
        """Normalize data to 0-1 range."""
        min_val = min(self.data)
        max_val = max(self.data)
        range_val = max_val - min_val
        
        if range_val == 0:
            return [0.5] * len(self.data)
        
        return [(x - min_val) / range_val for x in self.data]
    
    def filter_outliers(self, threshold=2.0):
        """Remove outliers beyond threshold standard deviations."""
        import statistics
        
        mean = statistics.mean(self.data)
        stdev = statistics.stdev(self.data)
        
        filtered = [x for x in self.data if abs(x - mean) <= threshold * stdev]
        return filtered


def main():
    """Main entry point."""
    fib = fibonacci(10)
    print(f"Fibonacci sequence: {fib}")
    
    data = [1, 2, 3, 100, 5, 6]  # 100 is outlier
    processor = DataProcessor(data)
    normalized = processor.normalize()
    print(f"Normalized: {normalized}")
    
    filtered = processor.filter_outliers(threshold=1.5)
    print(f"Filtered: {filtered}")


if __name__ == "__main__":
    main()
