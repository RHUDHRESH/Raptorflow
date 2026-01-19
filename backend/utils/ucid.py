import random
import string
from datetime import datetime

class UCIDGenerator:
    """Utility to generate and validate Unique Customer IDs (UCID)."""
    
    @staticmethod
    def generate() -> str:
        """
        Generates a UCID in the format: RF-YYYY-XXXX
        YYYY: Current Year
        XXXX: 4 random alphanumeric characters
        """
        year = datetime.now().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"RF-{year}-{random_part}"

    @staticmethod
    def validate(ucid: str) -> bool:
        """Validates the format of a UCID."""
        if not ucid.startswith("RF-"):
            return False
        parts = ucid.split("-")
        if len(parts) != 3:
            return False
        if not (parts[1].isdigit() and len(parts[1]) == 4):
            return False
        if len(parts[2]) != 4:
            return False
        return True
