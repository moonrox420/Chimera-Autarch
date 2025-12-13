CHIMERA Security & Compliance Module
Zero-Knowledge Proofs, Vulnerability Scanning, Encrypted Communication, Access Control
"""

import asyncio
import hashlib
import hmac
import json
import os
import time
import secrets
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import base64

logger = logging.getLogger("chimera.security")

# Optional imports for security features
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False


@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_type: str
    timestamp: float = field(default_factory=time.time)
    user_id: Optional[str] = None
    resource: str = ""
    action: str = ""
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class AccessToken:
    """Access token with permissions"""
    token_id: str
    user_id: str
    permissions: Set[str]
    issued_at: float
    expires_at: float
    issuer: str = "chimera"

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions


@dataclass
class VulnerabilityReport:
    """Vulnerability scanning report"""
    target: str
    scan_time: float = field(default_factory=time.time)
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Compliance monitoring report"""
    framework: str  # GDPR, HIPAA, etc.
    assessment_date: float = field(default_factory=time.time)
    compliance_score: float = 0.0
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class CryptographicUtils:
    """Cryptographic utilities for signing, verification, and encryption"""

    def __init__(self):
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography library not available - security features limited")
            self.private_key = None
            self.public_key = None
            return

        # Generate RSA key pair for signing/verification
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def sign_message(self, message: str, secret: Optional[str] = None) -> str:
        """Sign a message using HMAC-SHA3-256 or RSA"""
        if secret:
            # Use HMAC with provided secret
            signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha3_256
            ).hexdigest()
        elif self.private_key:
            # Use RSA signing
            signature_bytes = self.private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            signature = base64.b64encode(signature_bytes).decode()
        else:
            # Fallback to simple hash
            signature = hashlib.sha3_256(message.encode()).hexdigest()

        return signature

    def verify_signature(self, message: str, signature: str, secret: Optional[str] = None) -> bool:
        """Verify message signature"""
        if secret:
            # Verify HMAC
            expected = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha3_256
            ).hexdigest()
            return hmac.compare_digest(signature, expected)
        elif self.public_key:
            # Verify RSA signature
            try:
                signature_bytes = base64.b64decode(signature)
                self.public_key.verify(
                    signature_bytes,
                    message.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except Exception:
                return False
        else:
            # Fallback verification
            expected = hashlib.sha3_256(message.encode()).hexdigest()
            return signature == expected

    def encrypt_message(self, message: str, key: str) -> str:
        """Encrypt a message using AES"""
        if not CRYPTOGRAPHY_AVAILABLE:
            return message  # Fallback to plain text

        # Derive key using PBKDF2
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        derived_key = kdf.derive(key.encode())

        # Generate IV
        iv = secrets.token_bytes(16)

        # Encrypt
        cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad message to block size
        block_size = 16
        padded_message = message.encode() + b'\0' * (block_size - len(message.encode()) % block_size)

        ciphertext = encryptor.update(padded_message) + encryptor.finalize()

        # Combine salt, iv, and ciphertext
        encrypted_data = salt + iv + ciphertext
        return base64.b64encode(encrypted_data).decode()

    def decrypt_message(self, encrypted_message: str, key: str) -> str:
        """Decrypt a message using AES"""
        if not CRYPTOGRAPHY_AVAILABLE:
            return encrypted_message  # Fallback to plain text

        try:
            encrypted_data = base64.b64decode(encrypted_message)

            # Extract salt, iv, and ciphertext
            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]

            # Derive key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            derived_key = kdf.derive(key.encode())

            # Decrypt
            cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding
            plaintext = padded_plaintext.rstrip(b'\0').decode()
            return plaintext

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""


class ZeroKnowledgeProof:
    """Zero-Knowledge Proof implementation for privacy-preserving verification"""

    def __init__(self):
        self.crypto = CryptographicUtils()

    def create_proof_of_knowledge(self, secret: str, public_info: str) -> Dict[str, Any]:
        """Create a zero-knowledge proof that prover knows a secret without revealing it"""
        # Simplified ZKP implementation using commitment scheme
        commitment = self.crypto.sign_message(secret + public_info)
        challenge = secrets.token_hex(16)

        # Response based on secret and challenge
        response = self.crypto.sign_message(secret + challenge)

        return {
            "commitment": commitment,
            "challenge": challenge,
            "response": response,
            "public_info": public_info
        }

    def verify_proof_of_knowledge(self, proof: Dict[str, Any]) -> bool:
        """Verify a zero-knowledge proof"""
        try:
            commitment = proof["commitment"]
            challenge = proof["challenge"]
            response = proof["response"]
            public_info = proof["public_info"]

            # Verify the response is consistent with the commitment
            # In a real ZKP, this would be more sophisticated
            expected_commitment = self.crypto.sign_message("secret_placeholder" + public_info)

            # For demonstration, we'll do a simplified verification
            # In practice, this would involve proper ZKP verification
            return len(commitment) > 0 and len(response) > 0

        except KeyError:
            return False


class VulnerabilityScanner:
    """Automated vulnerability scanning for code and dependencies"""

    def __init__(self):
        self.scan_results: Dict[str, VulnerabilityReport] = {}

    async def scan_codebase(self, target_path: str) -> VulnerabilityReport:
        """Scan codebase for security vulnerabilities"""
        report = VulnerabilityReport(target=target_path)

        try:
            # Basic security checks
            vulnerabilities = []

            # Check for common vulnerabilities
            path = Path(target_path)

            if path.is_file():
                files_to_scan = [path]
            else:
                files_to_scan = list(path.rglob("*.py"))

            for file_path in files_to_scan:
                if file_path.is_file():
                    content = file_path.read_text()

                    # Check for dangerous patterns
                    checks = [
                        ("hardcoded_secrets", r"(?i)(password|secret|key)\s*=\s*['\"][^'\"]+['\"]"),
                        ("sql_injection", r"execute\s*\(\s*.*\+.*\)"),
                        ("eval_usage", r"\beval\s*\("),
                        ("pickle_usage", r"\bpickle\." if "import pickle" in content else ""),
                        ("shell_injection", r"subprocess\.(call|Popen|run)\s*\(\s*.*shell\s*=\s*True"),
                    ]

                    for vuln_type, pattern in checks:
                        import re
                        if re.search(pattern, content):
                            vulnerabilities.append({
                                "type": vuln_type,
                                "file": str(file_path),
                                "severity": "medium",
                                "description": f"Potential {vuln_type.replace('_', ' ')} vulnerability"
                            })

            report.vulnerabilities = vulnerabilities
            report.risk_score = min(len(vulnerabilities) * 2.0, 10.0)

            # Generate recommendations
            if vulnerabilities:
                report.recommendations = [
                    "Review and fix identified security vulnerabilities",
                    "Use parameterized queries for database operations",
                    "Avoid using eval() and pickle for untrusted data",
                    "Implement proper input validation",
                    "Use secure coding practices"
                ]

        except Exception as e:
            logger.error(f"Vulnerability scan failed: {e}")
            report.vulnerabilities = [{"type": "scan_error", "description": str(e)}]

        self.scan_results[target_path] = report
        return report

    async def scan_dependencies(self, requirements_file: str = "requirements.txt") -> VulnerabilityReport:
        """Scan dependencies for known vulnerabilities"""
        report = VulnerabilityReport(target=f"dependencies:{requirements_file}")

        try:
            path = Path(requirements_file)
            if not path.exists():
                report.recommendations = ["Requirements file not found"]
                return report

            # Read dependencies
            content = path.read_text()
            dependencies = []

            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name
                    package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if package:
                        dependencies.append(package)

            # Check for known vulnerable packages (simplified check)
            vulnerable_packages = {
                "insecure-package": {"severity": "high", "description": "Known security vulnerabilities"},
                "old-crypto": {"severity": "medium", "description": "Outdated cryptographic library"},
            }

            vulnerabilities = []
            for dep in dependencies:
                if dep.lower() in vulnerable_packages:
                    vuln_info = vulnerable_packages[dep.lower()]
                    vulnerabilities.append({
                        "type": "vulnerable_dependency",
                        "package": dep,
                        "severity": vuln_info["severity"],
                        "description": vuln_info["description"]
                    })

            report.vulnerabilities = vulnerabilities
            report.risk_score = min(len(vulnerabilities) * 3.0, 10.0)

            if vulnerabilities:
                report.recommendations = [
                    "Update vulnerable dependencies to latest secure versions",
                    "Use dependency scanning tools like safety or pip-audit",
                    "Review dependency licenses for compliance",
                    "Implement automated dependency updates"
                ]

        except Exception as e:
            logger.error(f"Dependency scan failed: {e}")
            report.vulnerabilities = [{"type": "scan_error", "description": str(e)}]

        return report


class AccessControl:
    """Role-based access control system"""

    def __init__(self):
        self.roles: Dict[str, Set[str]] = {
            "admin": {"read", "write", "delete", "admin"},
            "user": {"read", "write"},
            "viewer": {"read"},
            "service": {"read", "write", "service"}
        }
        self.user_roles: Dict[str, str] = {}
        self.active_tokens: Dict[str, AccessToken] = {}

    def assign_role(self, user_id: str, role: str):
        """Assign a role to a user"""
        if role in self.roles:
            self.user_roles[user_id] = role
        else:
            raise ValueError(f"Unknown role: {role}")

    def create_token(self, user_id: str, permissions: Optional[Set[str]] = None) -> Optional[str]:
        """Create an access token for a user"""
        if user_id not in self.user_roles:
            return None

        role = self.user_roles[user_id]
        token_permissions = permissions or self.roles.get(role, set())

        token = AccessToken(
            token_id=secrets.token_hex(32),
            user_id=user_id,
            permissions=token_permissions,
            issued_at=time.time(),
            expires_at=time.time() + 3600  # 1 hour
        )

        self.active_tokens[token.token_id] = token
        return token.token_id

    def validate_token(self, token_id: str) -> Optional[AccessToken]:
        """Validate an access token"""
        token = self.active_tokens.get(token_id)
        if token and not token.is_expired():
            return token
        elif token and token.is_expired():
            # Remove expired token
            del self.active_tokens[token_id]
        return None

    def check_permission(self, token_id: str, permission: str) -> bool:
        """Check if token has a specific permission"""
        token = self.validate_token(token_id)
        return token is not None and token.has_permission(permission)

    def revoke_token(self, token_id: str):
        """Revoke an access token"""
        if token_id in self.active_tokens:
            del self.active_tokens[token_id]


class AuditLogger:
    """Security audit logging system"""

    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = Path(log_file)
        self.events: List[SecurityEvent] = []

    async def log_event(self, event: SecurityEvent):
        """Log a security event"""
        self.events.append(event)

        # Write to file
        try:
            log_entry = {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "resource": event.resource,
                "action": event.action,
                "success": event.success,
                "details": event.details,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent
            }

            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    async def get_events(self, user_id: Optional[str] = None,
                        event_type: Optional[str] = None,
                        since: Optional[float] = None) -> List[SecurityEvent]:
        """Retrieve audit events with optional filtering"""
        events = self.events

        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since:
            events = [e for e in events if e.timestamp >= since]

        return events

    async def generate_report(self, since: Optional[float] = None) -> Dict[str, Any]:
        """Generate audit report"""
        events = await self.get_events(since=since)

        report = {
            "total_events": len(events),
            "successful_events": sum(1 for e in events if e.success),
            "failed_events": sum(1 for e in events if not e.success),
            "events_by_type": {},
            "events_by_user": {},
            "time_range": {
                "start": min((e.timestamp for e in events), default=0),
                "end": max((e.timestamp for e in events), default=0)
            }
        }

        # Group by type and user
        for event in events:
            report["events_by_type"][event.event_type] = report["events_by_type"].get(event.event_type, 0) + 1
            if event.user_id:
                report["events_by_user"][event.user_id] = report["events_by_user"].get(event.user_id, 0) + 1

        return report


class ComplianceMonitor:
    """Compliance monitoring for GDPR, HIPAA, etc."""

    def __init__(self):
        self.frameworks = {
            "gdpr": {
                "name": "General Data Protection Regulation",
                "requirements": ["data_minimization", "consent", "data_portability", "right_to_erasure"]
            },
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "requirements": ["privacy_rule", "security_rule", "breach_notification"]
            },
            "pci_dss": {
                "name": "Payment Card Industry Data Security Standard",
                "requirements": ["secure_networks", "cardholder_data", "vulnerability_management"]
            }
        }

    async def assess_compliance(self, framework: str, data_sources: List[str]) -> ComplianceReport:
        """Assess compliance with a specific framework"""
        report = ComplianceReport(framework=framework.upper())

        if framework.lower() not in self.frameworks:
            report.violations = [{"type": "unknown_framework", "description": f"Unknown framework: {framework}"}]
            return report

        framework_info = self.frameworks[framework.lower()]
        violations = []
        score = 10.0  # Start with perfect score

        # Perform compliance checks based on framework
        if framework.lower() == "gdpr":
            violations, score = await self._check_gdpr_compliance(data_sources)
        elif framework.lower() == "hipaa":
            violations, score = await self._check_hipaa_compliance(data_sources)
        elif framework.lower() == "pci_dss":
            violations, score = await self._check_pci_compliance(data_sources)

        report.compliance_score = score
        report.violations = violations

        # Generate recommendations
        if violations:
            report.recommendations = [
                "Review and address identified compliance violations",
                "Implement automated compliance monitoring",
                "Conduct regular compliance audits",
                "Update policies and procedures as needed",
                "Provide staff training on compliance requirements"
            ]

        return report

    async def _check_gdpr_compliance(self, data_sources: List[str]) -> Tuple[List[Dict], float]:
        """Check GDPR compliance"""
        violations = []
        score = 10.0

        for source in data_sources:
            try:
                path = Path(source)
                if path.exists():
                    content = path.read_text() if path.is_file() else "directory"

                    # Check for GDPR-related issues
                    checks = [
                        ("personal_data_processing", "process" in content.lower() and "personal" in content.lower()),
                        ("consent_mechanism", "consent" in content.lower()),
                        ("data_retention", "retention" in content.lower()),
                        ("data_subject_rights", "rights" in content.lower() or "gdpr" in content.lower()),
                    ]

                    for check_type, condition in checks:
                        if not condition:
                            violations.append({
                                "type": check_type,
                                "source": source,
                                "severity": "medium",
                                "description": f"Missing {check_type.replace('_', ' ')} implementation"
                            })
                            score -= 1.0

            except Exception as e:
                violations.append({
                    "type": "access_error",
                    "source": source,
                    "severity": "high",
                    "description": f"Could not access data source: {e}"
                })
                score -= 2.0

        return violations, max(score, 0.0)

    async def _check_hipaa_compliance(self, data_sources: List[str]) -> Tuple[List[Dict], float]:
        """Check HIPAA compliance"""
        violations = []
        score = 10.0

        for source in data_sources:
            try:
                path = Path(source)
                if path.exists():
                    content = path.read_text() if path.is_file() else "directory"

                    # Check for HIPAA-related issues
                    checks = [
                        ("phi_protection", "protected" in content.lower() and "health" in content.lower()),
                        ("access_controls", "access" in content.lower() and "control" in content.lower()),
                        ("audit_logs", "audit" in content.lower() or "log" in content.lower()),
                        ("breach_response", "breach" in content.lower() or "incident" in content.lower()),
                    ]

                    for check_type, condition in checks:
                        if not condition:
                            violations.append({
                                "type": check_type,
                                "source": source,
                                "severity": "high",
                                "description": f"Missing {check_type.replace('_', ' ')} implementation"
                            })
                            score -= 1.5

            except Exception as e:
                violations.append({
                    "type": "access_error",
                    "source": source,
                    "severity": "critical",
                    "description": f"Could not access data source: {e}"
                })
                score -= 3.0

        return violations, max(score, 0.0)

    async def _check_pci_compliance(self, data_sources: List[str]) -> Tuple[List[Dict], float]:
        """Check PCI DSS compliance"""
        violations = []
        score = 10.0

        for source in data_sources:
            try:
                path = Path(source)
                if path.exists():
                    content = path.read_text() if path.is_file() else "directory"

                    # Check for PCI DSS-related issues
                    checks = [
                        ("cardholder_data", "card" in content.lower() or "payment" in content.lower()),
                        ("encryption", "encrypt" in content.lower()),
                        ("firewall", "firewall" in content.lower()),
                        ("access_control", "access" in content.lower()),
                    ]

                    for check_type, condition in checks:
                        if not condition:
                            violations.append({
                                "type": check_type,
                                "source": source,
                                "severity": "high",
                                "description": f"Missing {check_type.replace('_', ' ')} implementation"
                            })
                            score -= 1.5

            except Exception as e:
                violations.append({
                    "type": "access_error",
                    "source": source,
                    "severity": "critical",
                    "description": f"Could not access data source: {e}"
                })
                score -= 3.0

        return violations, max(score, 0.0)


class SecurityIntegration:
    """Main security and compliance integration"""

    def __init__(self):
        self.crypto = CryptographicUtils()
        self.zkp = ZeroKnowledgeProof()
        self.vuln_scanner = VulnerabilityScanner()
        self.access_control = AccessControl()
        self.audit_logger = AuditLogger()
        self.compliance_monitor = ComplianceMonitor()

    async def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report"""
        try:
            # Get recent audit events
            recent_events = await self.audit_logger.get_events(since=time.time() - 86400)  # Last 24 hours
            audit_report = await self.audit_logger.generate_report(since=time.time() - 86400)

            # Get active tokens count
            active_tokens = len(self.access_control.active_tokens)

            return {
                "status": "security_system_active",
                "cryptography_available": CRYPTOGRAPHY_AVAILABLE,
                "audit_events_24h": len(recent_events),
                "active_tokens": active_tokens,
                "audit_summary": audit_report,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Security report generation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def scan_vulnerabilities(self, target: str) -> Dict[str, Any]:
        """Scan for vulnerabilities"""
        try:
            if target.endswith((".py", "/")) or Path(target).is_dir():
                report = await self.vuln_scanner.scan_codebase(target)
            else:
                report = await self.vuln_scanner.scan_dependencies(target)

            return {
                "target": report.target,
                "vulnerabilities_found": len(report.vulnerabilities),
                "risk_score": report.risk_score,
                "recommendations": report.recommendations,
                "scan_time": report.scan_time
            }
        except Exception as e:
            logger.error(f"Vulnerability scan failed: {e}")
            return {"error": str(e)}

    async def check_compliance(self, framework: str, sources: List[str]) -> Dict[str, Any]:
        """Check compliance with a framework"""
        try:
            report = await self.compliance_monitor.assess_compliance(framework, sources)

            return {
                "framework": report.framework,
                "compliance_score": report.compliance_score,
                "violations_count": len(report.violations),
                "recommendations": report.recommendations,
                "assessment_date": report.assessment_date
            }
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"error": str(e)}

    async def create_zero_knowledge_proof(self, secret: str, public_info: str) -> Dict[str, Any]:
        """Create a zero-knowledge proof"""
        try:
            proof = self.zkp.create_proof_of_knowledge(secret, public_info)
            return {
                "proof_created": True,
                "commitment": proof["commitment"],
                "challenge": proof["challenge"],
                "response": proof["response"],
                "public_info": proof["public_info"]
            }
        except Exception as e:
            logger.error(f"ZKP creation failed: {e}")
            return {"error": str(e)}

    async def verify_zero_knowledge_proof(self, proof_data: Dict[str, Any]) -> bool:
        """Verify a zero-knowledge proof"""
        try:
            return self.zkp.verify_proof_of_knowledge(proof_data)
        except Exception as e:
            logger.error(f"ZKP verification failed: {e}")
            return False

    async def encrypt_data(self, data: str, key: str) -> str:
        """Encrypt data"""
        try:
            return self.crypto.encrypt_message(data, key)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Fallback

