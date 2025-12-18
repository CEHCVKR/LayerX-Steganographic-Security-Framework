"""
Module 12: Security Analysis
Author: Member A
Description: Comprehensive security analysis and vulnerability assessment
Dependencies: hashlib, cryptography

Features:
- Entropy analysis
- Key strength analysis
- Cryptographic validation
- Vulnerability scanning
- Security scoring
- Compliance checking
"""

import hashlib
import os
import sys
from typing import Dict, List, Tuple
from collections import Counter
import math

# Import previous modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def calculate_entropy(data: bytes) -> float:
    """
    Calculate Shannon entropy of data
    
    Args:
        data: Input bytes
        
    Returns:
        Entropy value (0-8 bits per byte)
    """
    if not data:
        return 0.0
    
    # Count byte frequencies
    counter = Counter(data)
    length = len(data)
    
    # Calculate entropy
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    
    return entropy


def analyze_key_strength(key: bytes) -> Dict[str, any]:
    """
    Analyze cryptographic key strength
    
    Args:
        key: Key bytes
        
    Returns:
        Dictionary with key analysis
    """
    key_length = len(key)
    entropy = calculate_entropy(key)
    
    # Count character types
    has_lower = any(chr(b).islower() for b in key if b < 128)
    has_upper = any(chr(b).isupper() for b in key if b < 128)
    has_digit = any(chr(b).isdigit() for b in key if b < 128)
    has_special = any(not chr(b).isalnum() for b in key if b < 128)
    
    # Calculate complexity score
    complexity = sum([has_lower, has_upper, has_digit, has_special])
    
    # Determine strength
    if key_length < 16:
        strength = "WEAK"
        score = 30
    elif key_length < 32:
        strength = "MODERATE"
        score = 60
    else:
        strength = "STRONG"
        score = 90
    
    # Adjust for entropy
    if entropy < 4.0:
        strength = "WEAK"
        score = min(score, 40)
    elif entropy < 6.0:
        score = min(score, 70)
    
    return {
        'length': key_length,
        'entropy': entropy,
        'strength': strength,
        'score': score,
        'complexity': complexity,
        'has_lower': has_lower,
        'has_upper': has_upper,
        'has_digit': has_digit,
        'has_special': has_special
    }


def check_password_requirements(password: str) -> Dict[str, any]:
    """
    Check password against security requirements
    
    Args:
        password: Password string
        
    Returns:
        Dictionary with requirement checks
    """
    checks = {
        'min_length': len(password) >= 12,
        'has_upper': any(c.isupper() for c in password),
        'has_lower': any(c.islower() for c in password),
        'has_digit': any(c.isdigit() for c in password),
        'has_special': any(not c.isalnum() for c in password),
        'no_common': password.lower() not in ['password', '123456', 'admin', 'letmein']
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    if passed == total:
        verdict = "EXCELLENT"
        score = 100
    elif passed >= total - 1:
        verdict = "GOOD"
        score = 80
    elif passed >= total - 2:
        verdict = "FAIR"
        score = 60
    else:
        verdict = "POOR"
        score = 40
    
    return {
        'checks': checks,
        'passed': passed,
        'total': total,
        'verdict': verdict,
        'score': score
    }


def analyze_file_integrity(filepath: str) -> Dict[str, str]:
    """
    Calculate file hashes for integrity verification
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with hash values
    """
    hashes = {}
    
    with open(filepath, 'rb') as f:
        data = f.read()
        
        hashes['md5'] = hashlib.md5(data).hexdigest()
        hashes['sha1'] = hashlib.sha1(data).hexdigest()
        hashes['sha256'] = hashlib.sha256(data).hexdigest()
        hashes['sha512'] = hashlib.sha512(data).hexdigest()
    
    return hashes


def check_file_tampering(original_hash: str, current_filepath: str, 
                         algorithm: str = 'sha256') -> bool:
    """
    Check if file has been tampered with
    
    Args:
        original_hash: Original hash value
        current_filepath: Path to current file
        algorithm: Hash algorithm to use
        
    Returns:
        True if file is unmodified, False if tampered
    """
    with open(current_filepath, 'rb') as f:
        data = f.read()
        
        if algorithm == 'md5':
            current_hash = hashlib.md5(data).hexdigest()
        elif algorithm == 'sha1':
            current_hash = hashlib.sha1(data).hexdigest()
        elif algorithm == 'sha512':
            current_hash = hashlib.sha512(data).hexdigest()
        else:  # sha256
            current_hash = hashlib.sha256(data).hexdigest()
    
    return current_hash == original_hash


def scan_vulnerabilities(system_info: Dict) -> List[Dict]:
    """
    Scan for common vulnerabilities
    
    Args:
        system_info: Dictionary with system configuration
        
    Returns:
        List of found vulnerabilities
    """
    vulnerabilities = []
    
    # Check for weak encryption
    if 'encryption_algorithm' in system_info:
        if system_info['encryption_algorithm'] in ['DES', 'RC4', 'MD5']:
            vulnerabilities.append({
                'severity': 'HIGH',
                'category': 'Weak Encryption',
                'description': f"Using deprecated algorithm: {system_info['encryption_algorithm']}",
                'recommendation': 'Use AES-256 or ChaCha20'
            })
    
    # Check key length
    if 'key_length' in system_info:
        if system_info['key_length'] < 128:
            vulnerabilities.append({
                'severity': 'HIGH',
                'category': 'Weak Key',
                'description': f"Key length too short: {system_info['key_length']} bits",
                'recommendation': 'Use at least 256-bit keys'
            })
        elif system_info['key_length'] < 256:
            vulnerabilities.append({
                'severity': 'MEDIUM',
                'category': 'Suboptimal Key',
                'description': f"Key length should be increased: {system_info['key_length']} bits",
                'recommendation': 'Use 256-bit keys for better security'
            })
    
    # Check for secure random
    if 'random_source' in system_info:
        if system_info['random_source'] != 'cryptographic':
            vulnerabilities.append({
                'severity': 'HIGH',
                'category': 'Weak Random',
                'description': 'Not using cryptographically secure random',
                'recommendation': 'Use secrets module or os.urandom()'
            })
    
    # Check for SSL/TLS
    if 'network_encryption' in system_info:
        if not system_info['network_encryption']:
            vulnerabilities.append({
                'severity': 'CRITICAL',
                'category': 'No Transport Encryption',
                'description': 'Network communication not encrypted',
                'recommendation': 'Enable TLS/SSL for all network traffic'
            })
    
    # Check authentication
    if 'authentication_enabled' in system_info:
        if not system_info['authentication_enabled']:
            vulnerabilities.append({
                'severity': 'HIGH',
                'category': 'No Authentication',
                'description': 'System allows unauthenticated access',
                'recommendation': 'Implement strong authentication mechanism'
            })
    
    return vulnerabilities


def calculate_security_score(analysis_results: Dict) -> int:
    """
    Calculate overall security score
    
    Args:
        analysis_results: Dictionary with various analysis results
        
    Returns:
        Security score (0-100)
    """
    score = 100
    
    # Deduct for vulnerabilities
    if 'vulnerabilities' in analysis_results:
        for vuln in analysis_results['vulnerabilities']:
            if vuln['severity'] == 'CRITICAL':
                score -= 25
            elif vuln['severity'] == 'HIGH':
                score -= 15
            elif vuln['severity'] == 'MEDIUM':
                score -= 10
            else:  # LOW
                score -= 5
    
    # Deduct for weak keys
    if 'key_analysis' in analysis_results:
        key_score = analysis_results['key_analysis'].get('score', 100)
        if key_score < 60:
            score -= (100 - key_score) / 2
    
    # Deduct for low entropy
    if 'entropy' in analysis_results:
        if analysis_results['entropy'] < 4.0:
            score -= 20
        elif analysis_results['entropy'] < 6.0:
            score -= 10
    
    return max(0, min(100, int(score)))


class SecurityAnalyzer:
    """Comprehensive security analysis system"""
    
    def __init__(self):
        """Initialize security analyzer"""
        self.analysis_results = {}
        self.vulnerabilities = []
    
    def analyze_key(self, key: bytes, key_name: str = "default") -> Dict:
        """Analyze cryptographic key"""
        analysis = analyze_key_strength(key)
        self.analysis_results[f'key_{key_name}'] = analysis
        return analysis
    
    def analyze_password(self, password: str) -> Dict:
        """Analyze password strength"""
        analysis = check_password_requirements(password)
        self.analysis_results['password'] = analysis
        return analysis
    
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze file integrity"""
        hashes = analyze_file_integrity(filepath)
        self.analysis_results[f'file_{os.path.basename(filepath)}'] = hashes
        return hashes
    
    def scan_system(self, system_info: Dict) -> List[Dict]:
        """Scan system for vulnerabilities"""
        vulns = scan_vulnerabilities(system_info)
        self.vulnerabilities.extend(vulns)
        return vulns
    
    def calculate_score(self) -> int:
        """Calculate overall security score"""
        return calculate_security_score({
            'vulnerabilities': self.vulnerabilities,
            'key_analysis': self.analysis_results.get('key_default', {}),
            'entropy': self.analysis_results.get('key_default', {}).get('entropy', 8.0)
        })
    
    def generate_report(self) -> str:
        """Generate comprehensive security report"""
        report = []
        report.append("="*70)
        report.append("SECURITY ANALYSIS REPORT")
        report.append("="*70)
        
        # Key analysis
        if any(k.startswith('key_') for k in self.analysis_results):
            report.append("\n🔑 Key Analysis:")
            for key_name, analysis in self.analysis_results.items():
                if key_name.startswith('key_'):
                    report.append(f"\n   {key_name}:")
                    report.append(f"      Length: {analysis['length']} bytes")
                    report.append(f"      Entropy: {analysis['entropy']:.2f} bits/byte")
                    report.append(f"      Strength: {analysis['strength']}")
                    report.append(f"      Score: {analysis['score']}/100")
        
        # Password analysis
        if 'password' in self.analysis_results:
            pw = self.analysis_results['password']
            report.append("\n🔐 Password Analysis:")
            report.append(f"   Verdict: {pw['verdict']}")
            report.append(f"   Score: {pw['score']}/100")
            report.append(f"   Passed checks: {pw['passed']}/{pw['total']}")
        
        # Vulnerabilities
        if self.vulnerabilities:
            report.append("\n⚠️  Vulnerabilities Found:")
            for vuln in self.vulnerabilities:
                report.append(f"\n   [{vuln['severity']}] {vuln['category']}")
                report.append(f"      Description: {vuln['description']}")
                report.append(f"      Recommendation: {vuln['recommendation']}")
        else:
            report.append("\n✅ No vulnerabilities found")
        
        # Overall score
        score = self.calculate_score()
        report.append(f"\n📊 Overall Security Score: {score}/100")
        
        if score >= 90:
            rating = "EXCELLENT"
        elif score >= 70:
            rating = "GOOD"
        elif score >= 50:
            rating = "FAIR"
        else:
            rating = "POOR"
        
        report.append(f"   Rating: {rating}")
        
        report.append("\n" + "="*70)
        
        return "\n".join(report)


def test_security_analysis():
    """Test security analysis module"""
    print("="*70)
    print("MODULE 12: SECURITY ANALYSIS TEST")
    print("="*70)
    
    analyzer = SecurityAnalyzer()
    
    # Test key analysis
    print("\n1. Testing key strength analysis...")
    test_key = os.urandom(32)
    key_analysis = analyzer.analyze_key(test_key, "test_key")
    print(f"   Key length: {key_analysis['length']} bytes")
    print(f"   Entropy: {key_analysis['entropy']:.2f} bits/byte")
    print(f"   Strength: {key_analysis['strength']}")
    print("   ✓ Key analyzed")
    
    # Test password analysis
    print("\n2. Testing password strength...")
    test_password = "SecureP@ssw0rd123"
    pw_analysis = analyzer.analyze_password(test_password)
    print(f"   Verdict: {pw_analysis['verdict']}")
    print(f"   Score: {pw_analysis['score']}/100")
    print("   ✓ Password analyzed")
    
    # Test vulnerability scanning
    print("\n3. Testing vulnerability scan...")
    system_info = {
        'encryption_algorithm': 'AES-256',
        'key_length': 256,
        'random_source': 'cryptographic',
        'network_encryption': False,  # Intentional vuln for testing
        'authentication_enabled': True
    }
    vulns = analyzer.scan_system(system_info)
    print(f"   Found {len(vulns)} vulnerability(ies)")
    print("   ✓ Scan completed")
    
    # Test entropy calculation
    print("\n4. Testing entropy calculation...")
    random_data = os.urandom(1024)
    entropy = calculate_entropy(random_data)
    print(f"   Random data entropy: {entropy:.2f} bits/byte")
    print("   ✓ Entropy calculated")
    
    # Generate report
    print("\n5. Generating security report...")
    report = analyzer.generate_report()
    print(report)
    
    print("\n" + "="*70)
    print("✅ Security analysis module test completed!")
    print("="*70)


if __name__ == "__main__":
    test_security_analysis()
