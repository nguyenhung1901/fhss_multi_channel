#!/usr/bin/env python3
import argparse
import wave
import os

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cover", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="findings/changed_samples.txt")
    args = parser.parse_args()

    cover_params, cover = read_samples(args.cover)
    input_params, stego = read_samples(args.input)

    if cover_params != input_params:
        print("ANALYZE_FAIL")
        print("WAV parameters do not match.")
        return

    outdir = os.path.dirname(args.out)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    changed = []
    for i, (c, s) in enumerate(zip(cover, stego)):
        if c != s:
            changed.append((i, s - c))

    with open(args.out, "w") as f:
        for idx, diff in changed:
            f.write(f"{idx} {diff}\n")

    print(f"cover={args.cover}")
    print(f"input={args.input}")
    print(f"changed_samples={len(changed)}")
    print(f"output={args.out}")

    if len(changed) > 0:
        print("ANALYZE_OK")
    else:
        print("ANALYZE_FAIL")

if __name__ == "__main__":
    main()
