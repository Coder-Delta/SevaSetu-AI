import logging
from typing import Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass 
class EKYCVerificationResult:
    is_verified: bool
    provider: str
    document_type: str
    verification_id: str
    message: str

class EKYCProviderStub:
    """
    Stub eKYC provider mimicking integration with Aadhaar eKYC or DigiLocker.
    All credentials are mock and operations return mock success.
    """
    def __init__(self):
        logger.warning("Using EKYCProviderStub — NOT for production use")
    
    async def verify_aadhaar(self, aadhaar_number: str) -> EKYCVerificationResult:
        # PII: Do not log or print full Aadhaar number in logs
        last_four = aadhaar_number[-4:] if len(aadhaar_number) >= 4 else "0000"
        logger.info(f"STUB: Simulating Aadhaar verification for number ending in {last_four}")
        return EKYCVerificationResult(
            is_verified=True,
            provider="UIDAI_STUB",
            document_type="Aadhaar",
            verification_id="STUB-AADHAAR-8938129",
            message="Verification successful (mock API)"
        )
    
    async def verify_pan(self, pan_number: str) -> EKYCVerificationResult:
        # PII: Do not log PAN
        last_four = pan_number[-4:] if len(pan_number) >= 4 else "0000"
        logger.info(f"STUB: Simulating PAN verification for PAN ending in {last_four}")
        return EKYCVerificationResult(
            is_verified=True,
            provider="NSDL_STUB",
            document_type="PAN",
            verification_id="STUB-PAN-349832",
            message="PAN Verification successful (mock API)"
        )
