"""
Module 11: Performance Monitoring
Author: Member A
Description: Real-time performance tracking and resource monitoring
Dependencies: psutil, time

Features:
- CPU and memory monitoring
- Operation timing and profiling
- Throughput measurement
- Resource usage tracking
- Performance metrics collection
- Alert system for performance degradation
"""

import time
import psutil
import os
import threading
from typing import Dict, List, Callable
from datetime import datetime
from collections import deque


class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, history_size: int = 100):
        """
        Initialize performance monitor
        
        Args:
            history_size: Number of historical records to keep
        """
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        self.operation_timings = {}
        self.alert_callbacks = []
        self.monitoring = False
        self.monitor_thread = None
        self.process = psutil.Process(os.getpid())
        
        # Thresholds
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 80.0  # %
        self.operation_time_threshold = 5.0  # seconds
        
    def start_monitoring(self, interval: float = 1.0):
        """
        Start background monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring:
            print("⚠️  Monitoring already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"✓ Performance monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("✓ Performance monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Background monitoring loop"""
        while self.monitoring:
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            self._check_alerts(metrics)
            time.sleep(interval)
    
    def collect_metrics(self) -> Dict:
        """
        Collect current system metrics
        
        Returns:
            Dictionary with current metrics
        """
        cpu_percent = self.process.cpu_percent(interval=0.1)
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        
        # System-wide metrics
        sys_cpu = psutil.cpu_percent(interval=0.1)
        sys_memory = psutil.virtual_memory()
        
        metrics = {
            'timestamp': datetime.now(),
            'process_cpu': cpu_percent,
            'process_memory_mb': memory_info.rss / (1024 * 1024),
            'process_memory_percent': memory_percent,
            'system_cpu': sys_cpu,
            'system_memory_percent': sys_memory.percent,
            'system_memory_available_mb': sys_memory.available / (1024 * 1024)
        }
        
        return metrics
    
    def _check_alerts(self, metrics: Dict):
        """Check if metrics exceed thresholds"""
        alerts = []
        
        if metrics['process_cpu'] > self.cpu_threshold:
            alerts.append(f"High CPU usage: {metrics['process_cpu']:.1f}%")
        
        if metrics['process_memory_percent'] > self.memory_threshold:
            alerts.append(f"High memory usage: {metrics['process_memory_percent']:.1f}%")
        
        if alerts:
            for callback in self.alert_callbacks:
                callback(alerts)
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
    
    def time_operation(self, operation_name: str):
        """
        Context manager for timing operations
        
        Usage:
            with monitor.time_operation("embed_image"):
                # Your code here
                pass
        """
        return OperationTimer(self, operation_name)
    
    def record_timing(self, operation_name: str, duration: float):
        """Record operation timing"""
        if operation_name not in self.operation_timings:
            self.operation_timings[operation_name] = deque(maxlen=self.history_size)
        
        self.operation_timings[operation_name].append({
            'timestamp': datetime.now(),
            'duration': duration
        })
        
        # Check for slow operations
        if duration > self.operation_time_threshold:
            for callback in self.alert_callbacks:
                callback([f"Slow operation: {operation_name} took {duration:.2f}s"])
    
    def get_operation_stats(self, operation_name: str) -> Dict:
        """
        Get statistics for specific operation
        
        Args:
            operation_name: Name of operation
            
        Returns:
            Dictionary with statistics
        """
        if operation_name not in self.operation_timings:
            return {}
        
        timings = [t['duration'] for t in self.operation_timings[operation_name]]
        
        return {
            'count': len(timings),
            'avg': sum(timings) / len(timings),
            'min': min(timings),
            'max': max(timings),
            'total': sum(timings)
        }
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all operations"""
        stats = {}
        for op_name in self.operation_timings.keys():
            stats[op_name] = self.get_operation_stats(op_name)
        return stats
    
    def get_current_metrics(self) -> Dict:
        """Get current real-time metrics"""
        return self.collect_metrics()
    
    def get_metrics_history(self) -> List[Dict]:
        """Get historical metrics"""
        return list(self.metrics_history)
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive performance summary
        
        Returns:
            Dictionary with performance summary
        """
        current = self.collect_metrics()
        
        # Calculate averages from history
        if self.metrics_history:
            avg_cpu = sum(m['process_cpu'] for m in self.metrics_history) / len(self.metrics_history)
            avg_memory = sum(m['process_memory_mb'] for m in self.metrics_history) / len(self.metrics_history)
        else:
            avg_cpu = current['process_cpu']
            avg_memory = current['process_memory_mb']
        
        # Operation statistics
        operation_stats = self.get_all_stats()
        
        return {
            'current': current,
            'averages': {
                'cpu_percent': avg_cpu,
                'memory_mb': avg_memory
            },
            'operations': operation_stats,
            'history_count': len(self.metrics_history)
        }
    
    def print_summary(self):
        """Print formatted performance summary"""
        summary = self.get_summary()
        
        print("="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)
        
        print("\n📊 Current Metrics:")
        print(f"   CPU Usage: {summary['current']['process_cpu']:.1f}%")
        print(f"   Memory Usage: {summary['current']['process_memory_mb']:.1f} MB")
        print(f"   System CPU: {summary['current']['system_cpu']:.1f}%")
        print(f"   System Memory: {summary['current']['system_memory_percent']:.1f}%")
        
        if self.metrics_history:
            print(f"\n📈 Averages (last {len(self.metrics_history)} samples):")
            print(f"   CPU: {summary['averages']['cpu_percent']:.1f}%")
            print(f"   Memory: {summary['averages']['memory_mb']:.1f} MB")
        
        if summary['operations']:
            print("\n⏱️  Operation Statistics:")
            for op_name, stats in summary['operations'].items():
                print(f"\n   {op_name}:")
                print(f"      Count: {stats['count']}")
                print(f"      Average: {stats['avg']:.3f}s")
                print(f"      Min: {stats['min']:.3f}s")
                print(f"      Max: {stats['max']:.3f}s")
                print(f"      Total: {stats['total']:.3f}s")
        
        print("\n" + "="*70)


class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.monitor.record_timing(self.operation_name, duration)
        return False


class ThroughputMonitor:
    """Monitor data throughput"""
    
    def __init__(self, window_size: int = 10):
        """
        Initialize throughput monitor
        
        Args:
            window_size: Number of samples for moving average
        """
        self.window_size = window_size
        self.throughput_history = deque(maxlen=window_size)
    
    def record_throughput(self, bytes_processed: int, duration: float):
        """
        Record throughput measurement
        
        Args:
            bytes_processed: Number of bytes processed
            duration: Time taken in seconds
        """
        if duration > 0:
            throughput = bytes_processed / duration  # bytes/second
            self.throughput_history.append({
                'timestamp': datetime.now(),
                'throughput': throughput,
                'bytes': bytes_processed,
                'duration': duration
            })
    
    def get_average_throughput(self) -> float:
        """Get average throughput in MB/s"""
        if not self.throughput_history:
            return 0.0
        
        avg = sum(t['throughput'] for t in self.throughput_history) / len(self.throughput_history)
        return avg / (1024 * 1024)  # Convert to MB/s
    
    def get_stats(self) -> Dict:
        """Get throughput statistics"""
        if not self.throughput_history:
            return {}
        
        throughputs = [t['throughput'] / (1024 * 1024) for t in self.throughput_history]
        
        return {
            'count': len(throughputs),
            'average_mbps': sum(throughputs) / len(throughputs),
            'min_mbps': min(throughputs),
            'max_mbps': max(throughputs),
            'total_bytes': sum(t['bytes'] for t in self.throughput_history),
            'total_duration': sum(t['duration'] for t in self.throughput_history)
        }


def test_performance_monitoring():
    """Test performance monitoring module"""
    print("="*70)
    print("MODULE 11: PERFORMANCE MONITORING TEST")
    print("="*70)
    
    # Initialize monitor
    monitor = PerformanceMonitor()
    
    # Add alert callback
    def alert_handler(alerts):
        for alert in alerts:
            print(f"   ⚠️  ALERT: {alert}")
    
    monitor.add_alert_callback(alert_handler)
    
    print("\n1. Testing operation timing...")
    
    # Simulate some operations
    with monitor.time_operation("test_operation_1"):
        time.sleep(0.1)
    
    with monitor.time_operation("test_operation_2"):
        time.sleep(0.2)
    
    with monitor.time_operation("test_operation_1"):
        time.sleep(0.15)
    
    print("   ✓ Operations timed")
    
    # Test metrics collection
    print("\n2. Testing metrics collection...")
    metrics = monitor.collect_metrics()
    print(f"   Current CPU: {metrics['process_cpu']:.1f}%")
    print(f"   Current Memory: {metrics['process_memory_mb']:.1f} MB")
    print("   ✓ Metrics collected")
    
    # Test throughput monitoring
    print("\n3. Testing throughput monitoring...")
    tp_monitor = ThroughputMonitor()
    
    tp_monitor.record_throughput(1024*1024, 0.5)  # 1MB in 0.5s
    tp_monitor.record_throughput(2048*1024, 1.0)  # 2MB in 1s
    
    tp_stats = tp_monitor.get_stats()
    print(f"   Average throughput: {tp_stats['average_mbps']:.2f} MB/s")
    print("   ✓ Throughput monitored")
    
    # Print summary
    print("\n4. Performance summary:")
    monitor.print_summary()
    
    print("\n" + "="*70)
    print("✅ Performance monitoring module test completed!")
    print("="*70)


if __name__ == "__main__":
    test_performance_monitoring()
