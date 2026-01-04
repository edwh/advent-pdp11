#!/usr/bin/env python3
"""
Create a SIMH tape image with DOS-11 format files.

This creates a tape that RSTS/E can read using PIP with MT: device.

SIMH Tape Format:
- Each record: 4-byte length (LE) + data (even padded) + 4-byte length
- Tape mark: 4 zero bytes (0x00000000)
- End of medium: 4 bytes (0xFFFFFFFF)

DOS-11 Tape File Structure:
- 14-byte header record (filename, ext, PPN, protection, date)
- Multiple 512-byte data records
- Tape mark at end of file

Reference: https://vmsnet.pdp-11.narkive.com/26ioynLm/dos-11-magtape-format
"""

import struct
import sys
import os

# RAD50 character set for PDP-11
# Space=0, A-Z=1-26, $=27, .=28, unused=29, 0-9=30-39
RAD50_CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ$. 0123456789"

def char_to_rad50(c):
    """Convert a single character to RAD50 value."""
    c = c.upper()
    if c == ' ':
        return 0
    elif 'A' <= c <= 'Z':
        return ord(c) - ord('A') + 1
    elif c == '$':
        return 27
    elif c == '.':
        return 28
    elif '0' <= c <= '9':
        return ord(c) - ord('0') + 30
    else:
        return 0  # Unknown chars become space

def encode_rad50(s, length=3):
    """Encode a string to RAD50 (3 chars per 16-bit word)."""
    # Pad or truncate to exact length
    s = (s + ' ' * length)[:length]

    result = []
    for i in range(0, length, 3):
        chunk = s[i:i+3]
        if len(chunk) < 3:
            chunk = chunk + ' ' * (3 - len(chunk))

        c1 = char_to_rad50(chunk[0])
        c2 = char_to_rad50(chunk[1])
        c3 = char_to_rad50(chunk[2])

        word = (c1 * 40 + c2) * 40 + c3
        result.append(word)

    return result

def decode_rad50(word):
    """Decode a RAD50 word back to 3 characters."""
    c3 = word % 40
    word //= 40
    c2 = word % 40
    c1 = word // 40

    return RAD50_CHARS[c1] + RAD50_CHARS[c2] + RAD50_CHARS[c3]

def create_dos11_header(filename, ext, group=1, user=2, protection=0o233, date=0):
    """
    Create a 14-byte DOS-11 tape file header.

    Based on xferx/pdp11/dos11magtapefs.py from andreax79/xferx

    Format (7 words = 14 bytes):
    - Word 0-1: RAD50 filename chars 1-6 (2 words)
    - Word 2: RAD50 extension (1 word)
    - Word 3: UIC as 16-bit word (group << 8 | user)
    - Word 4: Protection code
    - Word 5: Creation date
    - Word 6: RAD50 filename chars 7-9 (optional, usually 0)

    UIC is [group,user] packed as (group << 8) + user
    """
    # Encode filename (first 6 chars -> 2 RAD50 words)
    fname = filename[:6].ljust(6)
    fname_words = encode_rad50(fname, 6)

    # Encode extension (3 chars -> 1 RAD50 word)
    ext = ext[:3].ljust(3)
    ext_word = encode_rad50(ext, 3)[0]

    # Encode filename chars 7-9 (optional)
    fname3 = 0
    if len(filename) > 6:
        fname3_str = filename[6:9].ljust(3)
        fname3 = encode_rad50(fname3_str, 3)[0]

    # UIC as 16-bit word: (group << 8) | user
    uic_word = (group << 8) | user

    # Pack header: fnam1, fnam2, ftyp, fuic, protection, date, fnam3
    header = struct.pack('<HHHHHHH',
                         fname_words[0],  # filename word 1
                         fname_words[1],  # filename word 2
                         ext_word,        # extension
                         uic_word,        # UIC
                         protection,      # protection code
                         date,            # creation date
                         fname3)          # filename word 3 (chars 7-9)

    assert len(header) == 14, f"Header should be 14 bytes, got {len(header)}"
    return header

def write_tape_record(f, data):
    """Write a single tape record in SIMH format."""
    length = len(data)
    # Pad to even length if needed
    if length % 2:
        data = data + b'\x00'

    # Write: length + data + length
    f.write(struct.pack('<I', length))  # Initial record length
    f.write(data)
    f.write(struct.pack('<I', length))  # Trailing record length

def write_tape_mark(f):
    """Write a tape mark (end of file marker)."""
    f.write(struct.pack('<I', 0))  # Tape mark = 0

def write_end_of_medium(f):
    """Write end of medium marker."""
    f.write(struct.pack('<I', 0xFFFFFFFF))

def write_file_to_tape(tape_file, filename, ext, data, group=1, user=2,
                        block_size=512, single_record=False, combined=False):
    """
    Write a file to the tape in DOS-11 format.

    Structure:
    1. 14-byte header record (or combined with data)
    2. Data records (512-byte blocks or single record)
    3. Tape mark

    Args:
        group: UIC group number (default 1)
        user: UIC user number (default 2)
        block_size: Size of data blocks (default 512)
        single_record: If True, write all data as one record
        combined: If True, write header + all data as one record
    """
    # Create header
    header = create_dos11_header(filename, ext, group, user)

    if combined:
        # Write header + all data as a single tape record
        write_tape_record(tape_file, header + data)
    else:
        # Write header as separate record
        write_tape_record(tape_file, header)

        if single_record:
            # Write all data as one record
            write_tape_record(tape_file, data)
        else:
            # Write data in blocks
            offset = 0
            while offset < len(data):
                block = data[offset:offset + block_size]
                # Pad last block to block_size
                if len(block) < block_size:
                    block = block + b'\x00' * (block_size - len(block))
                write_tape_record(tape_file, block)
                offset += block_size

    # Write tape mark to end the file
    write_tape_mark(tape_file)

def create_test_tape(output_path):
    """Create a test tape with a simple file."""
    print(f"Creating test tape: {output_path}")

    with open(output_path, 'wb') as f:
        # Write a simple test file
        test_data = b"Hello from the tape drive!\r\n"
        test_data += b"This is a test of DOS-11 tape format.\r\n"
        test_data += b"If you can read this, the tape transfer works!\r\n"

        # Pad to 512 bytes (one block)
        test_data = test_data.ljust(512, b'\x00')

        # Try with header + data combined as continuous tape file
        # Some systems expect header + data to flow continuously
        write_file_to_tape(f, "TEST", "TXT", test_data, single_record=False)

        # Write end of medium
        write_end_of_medium(f)

    print(f"Created tape with 1 file, {os.path.getsize(output_path)} bytes")

def create_data_tape(output_path, files):
    """
    Create a tape with multiple files.

    Args:
        output_path: Path to write the tape image
        files: List of (filename, ext, data_bytes) tuples
    """
    print(f"Creating data tape: {output_path}")

    with open(output_path, 'wb') as f:
        for filename, ext, data in files:
            print(f"  Adding file: {filename}.{ext} ({len(data)} bytes)")
            write_file_to_tape(f, filename, ext, data)

        # Write end of medium
        write_end_of_medium(f)

    print(f"Created tape with {len(files)} files, {os.path.getsize(output_path)} bytes total")

def dump_tape(tape_path):
    """Dump the contents of a SIMH tape image for debugging."""
    print(f"\nDumping tape: {tape_path}")
    print("=" * 60)

    with open(tape_path, 'rb') as f:
        record_num = 0
        file_num = 0

        while True:
            pos = f.tell()
            length_bytes = f.read(4)
            if len(length_bytes) < 4:
                print(f"[EOF at position {pos}]")
                break

            length = struct.unpack('<I', length_bytes)[0]

            if length == 0:
                print(f"Record {record_num}: TAPE MARK (end of file {file_num})")
                file_num += 1
                record_num += 1
                continue

            if length == 0xFFFFFFFF:
                print(f"Record {record_num}: END OF MEDIUM")
                break

            if length == 0xFFFFFFFE:
                print(f"Record {record_num}: ERASE GAP")
                record_num += 1
                continue

            # Read data
            padded_length = (length + 1) & ~1
            data = f.read(padded_length)

            # Read trailing length
            trailing = f.read(4)
            trailing_length = struct.unpack('<I', trailing)[0] if len(trailing) == 4 else 0

            if length == 14:
                # Try to decode as DOS-11 header
                try:
                    fname1 = struct.unpack('<H', data[0:2])[0]
                    fname2 = struct.unpack('<H', data[2:4])[0]
                    ext_word = struct.unpack('<H', data[4:6])[0]
                    proj = data[6]
                    prog = data[7]
                    prot = struct.unpack('<H', data[8:10])[0]
                    date = struct.unpack('<H', data[10:12])[0]

                    filename = decode_rad50(fname1) + decode_rad50(fname2)
                    extension = decode_rad50(ext_word)

                    print(f"Record {record_num}: HEADER - {filename.strip()}.{extension.strip()} "
                          f"[{proj},{prog}] prot={prot:o} date={date}")
                except Exception as e:
                    print(f"Record {record_num}: {length} bytes (header decode failed: {e})")
            elif length == 512:
                print(f"Record {record_num}: DATA BLOCK {length} bytes")
            else:
                print(f"Record {record_num}: {length} bytes")

            record_num += 1

    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  create_tape.py test           - Create a test tape")
        print("  create_tape.py dump <file>    - Dump tape contents")
        print("  create_tape.py create <file> <input1> [input2...]  - Create tape from files")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'test':
        create_test_tape('/tmp/test.tap')
        dump_tape('/tmp/test.tap')

    elif command == 'dump' and len(sys.argv) >= 3:
        dump_tape(sys.argv[2])

    elif command == 'create' and len(sys.argv) >= 4:
        output = sys.argv[2]
        files = []
        for input_file in sys.argv[3:]:
            basename = os.path.basename(input_file)
            if '.' in basename:
                name, ext = basename.rsplit('.', 1)
            else:
                name, ext = basename, 'DAT'

            with open(input_file, 'rb') as f:
                data = f.read()

            files.append((name[:6], ext[:3], data))

        create_data_tape(output, files)
        dump_tape(output)

    else:
        print("Invalid command or arguments")
        sys.exit(1)
