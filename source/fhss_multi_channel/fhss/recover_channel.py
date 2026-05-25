#!/usr/bin/env python3
import argparse
import wave
import random

def read_samples(path):
    with wave.open(path, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())

    if params.nchannels != 1 or params.sampwidth != 2:
        raise ValueError("Only mono 16-bit PCM WAV is supported")

    data = bytearray(frames)
    samples = []
    for i in range(0, len(data), 2):
        samples.append(int.from_bytes(bytes([data[i], data[i+1]]), byteorder="little", signed=True))
    return params, samples

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8:
            break
        chars.append(chr(int(chunk, 2)))
    return ''.join(chars)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cover", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="recovered.txt")
    parser.add_argument("--log", default="recover.log")
    parser.add_argument("--key", type=int, required=True)
    parser.add_argument("--frame-size", type=int, required=True)
    parser.add_argument("--msg-len", type=int, required=True)
    args = parser.parse_args()

    _, cover = read_samples(args.cover)
    _, stego = read_samples(args.input)

    total_bits = args.msg_len * 8
    random.seed(args.key)

    bits = []
    lines = []

    for frame_idx in range(total_bits):
        frame_start = frame_idx * args.frame_size
        hop_offset = random.randint(0, args.frame_size - 1)
        sample_index = frame_start + hop_offset

        cover_value = cover[sample_index]
        stego_value = stego[sample_index]
        diff = stego_value - cover_value

        bit = "1" if diff > 0 else "0"
        bits.append(bit)

        lines.append(
            f"frame={frame_idx} hop_offset={hop_offset} sample={sample_index} "
            f"cover={cover_value} stego={stego_value} diff={diff} recovered_bit={bit}"
        )

    text = bits_to_text(''.join(bits))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)

    with open(args.log, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    print("RECOVER_RUN_OK")
    print(f"cover={args.cover}")
    print(f"input={args.input}")
    print(f"output={args.output}")
    print(f"RECOVERED_TEXT={text}")

    if text == "CHANNEL42":
        print("RECOVER_OK")
    else:
        print("RECOVER_FAIL")

if __name__ == "__main__":
    main()
