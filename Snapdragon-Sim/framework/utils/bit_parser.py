class BitParser:
    """
    Simulates reading a 16-bit status register from a Snapdragon chip.
    
    Bit Map:
    - Bit 0: Overheat Interruption (1 = Hot, 0 = Normal)
    - Bit 1: Low Voltage Warning (1 = Low, 0 = Normal)
    - Bit 8-15: CPU Core ID (Which core is reporting the error)
    """

    @staticmethod
    def parse_status(register_hex: str) -> dict:
        """
        Converts a Hex string like '0x0A01' into a readable dictionary.
        """
        # Convert Hex string to integer
        val = int(register_hex, 16)

        # Use Bitwise AND (&) to check specific bits
        is_overheat = bool(val & 0x01)       # Check Bit 0
        is_low_voltage = bool((val >> 1) & 0x01) # Shift and check Bit 1
        core_id = (val >> 8) & 0xFF          # Extract Bits 8-15

        return {
            "overheat_fault": is_overheat,
            "voltage_fault": is_low_voltage,
            "reporting_core": core_id
        }