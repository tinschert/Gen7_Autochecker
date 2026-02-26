# blf_to_mf4_with_arxml.py
# Requirements: pip install python-can cantools asammdf numpy

import can
import cantools
from asammdf import MDF, Signal
import numpy as np
from pathlib import Path
from collections import defaultdict
import sys

# ────────────────────────────────────────────────
#  CONFIG - CHANGE THESE PATHS
# ────────────────────────────────────────────────
BLF_PATH   = Path(r"C:\TOOLS\Gen7_Checker\Gen5_37W_BL_2026-02-02_11-24_M705_RC2__BS-VJ932E_0013.blf")  # ← your .blf file
ARXML_PATH = Path(r"C:\TOOLS\Gen7_Checker\E3_1_1_UNECE_Gen2_MRR2023_15.05.01.00_F_E2E.arxml")
OUTPUT_MF4 = BLF_PATH.with_suffix(".mf4")

# Optional: set to True if you want string channels for enumerations
ADD_ENUM_STRINGS = True

# ────────────────────────────────────────────────

def main():
    print("Loading ARXML database...")
    try:
        db = cantools.database.load_file(str(ARXML_PATH))
        print(f"Loaded {len(db.messages)} messages from ARXML")
    except Exception as e:
        print(f"Error loading ARXML: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nReading BLF file...")
    try:
        with can.BLFReader(str(BLF_PATH)) as reader:
            messages = list(reader)
        print(f"Loaded {len(messages):,} CAN messages")
    except Exception as e:
        print(f"Error reading BLF: {e}", file=sys.stderr)
        sys.exit(1)

    if not messages:
        print("No messages found in BLF file.")
        return

    timestamps_all = np.array([msg.timestamp for msg in messages], dtype=np.float64)

    # Group messages by CAN ID
    by_id = defaultdict(list)
    for msg in messages:
        by_id[msg.arbitration_id].append(msg)

    mdf = MDF(version="4.20")  # Good compression & modern features
    added_signals = 0

    for can_id_hex, msgs_list in sorted(by_id.items(), key=lambda x: x[0]):
        can_id = can_id_hex  # already int
        ts = np.array([m.timestamp for m in msgs_list], dtype=np.float64)

        try:
            msg_def = db.get_message_by_frame_id(can_id)
            msg_name = msg_def.name
            print(f"Decoding {msg_name} (0x{can_id:08X}) – {len(msgs_list)} frames")
        except KeyError:
            print(f"Skipping unknown ID 0x{can_id:08X} ({len(msgs_list)} frames)")
            continue

        # Prepare per-signal lists
        signal_data = {sig.name: [] for sig in msg_def.signals}
        enum_str_data = {}  # only if needed
        if ADD_ENUM_STRINGS:
            enum_str_data = {sig.name + "_enum": [] for sig in msg_def.signals if sig.choices}

        valid_decodes = 0

        for m in msgs_list:
            try:
                decoded = msg_def.decode(m.data)

                for sig_name, raw_val in decoded.items():
                    if isinstance(raw_val, cantools.database.can.NamedSignalValue):
                        numeric_val = float(raw_val.value)
                        enum_name   = raw_val.name if raw_val.name is not None else str(raw_val.value)
                    else:
                        numeric_val = float(raw_val) if raw_val is not None else np.nan
                        enum_name   = None

                    signal_data[sig_name].append(numeric_val)

                    if ADD_ENUM_STRINGS and (sig_name + "_enum") in enum_str_data:
                        enum_str_data[sig_name + "_enum"].append(enum_name)

                valid_decodes += 1

            except Exception as decode_err:
                # Append NaN / None to keep lengths equal
                for sname in signal_data:
                    signal_data[sname].append(np.nan)
                if ADD_ENUM_STRINGS:
                    for k in enum_str_data:
                        enum_str_data[k].append(None)

        print(f"  → {valid_decodes}/{len(msgs_list)} frames decoded OK")

        # ── Add numeric signals ─────────────────────────────────────
        for sig_name, values_list in signal_data.items():
            if not values_list:
                continue

            samples = np.array(values_list, dtype=np.float64)

            # Get unit & comment if available
            sig_def = next((s for s in msg_def.signals if s.name == sig_name), None)
            unit    = sig_def.unit if sig_def and sig_def.unit else ""
            comment = sig_def.comment if sig_def and sig_def.comment else ""

            sig = Signal(
                samples    = samples,
                timestamps = ts[:len(samples)],
                name       = f"{msg_name}.{sig_name}",
                unit       = unit,
                comment    = f"{comment} (numeric value)".strip()
            )
            mdf.append(sig, comment=f"CAN ID 0x{can_id:08X}")
            added_signals += 1

        # ── Optional: Add string channels for enums ─────────────────
        if ADD_ENUM_STRINGS:
            for enum_key, str_list in enum_str_data.items():
                if not any(s for s in str_list if s is not None):
                    continue
                str_array = np.array([s if s is not None else "" for s in str_list], dtype="<U64")
                sig_str = Signal(
                    samples    = str_array,
                    timestamps = ts[:len(str_array)],
                    name       = f"{msg_name}.{enum_key}",
                    comment    = "Enum / named value string"
                )
                mdf.append(sig_str)

    # ── Fallback raw data if almost nothing was decoded ─────────────
    if added_signals < 5:
        print("\nWarning: Very few signals decoded → adding raw fallback channels")
        hex_list = [msg.data.hex().upper() for msg in messages]
        sig_hex = Signal(
            samples    = np.array(hex_list, dtype=f"S{256}"),  # up to 64 bytes = 128 hex chars
            timestamps = timestamps_all,
            name       = "CAN_RAW_HEX_ALL",
            comment    = "Raw hex data – fallback"
        )
        mdf.append(sig_hex)

        dlc_arr = np.array([len(msg.data) for msg in messages], dtype=np.uint8)
        sig_dlc = Signal(
            samples    = dlc_arr,
            timestamps = timestamps_all,
            name       = "CAN_DLC_ALL",
            unit       = "bytes"
        )
        mdf.append(sig_dlc)

    # ── Save ────────────────────────────────────────────────────────
    print(f"\nSaving MDF file with {added_signals} signal channels...")
    try:
        mdf.save(str(OUTPUT_MF4), overwrite=True, compression=2)
        print(f"Success! File saved: {OUTPUT_MF4}")
        print("Open it in asammdf to view/plot the signals.")
    except Exception as e:
        print(f"Error saving MF4: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()