#!/usr/bin/env python3
import argparse
import wave
import random
import string
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
    return samples

def bits_to_text(bits):
    out = []
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8:
            break
        out.append(chr(int(chunk, 2)))
    return ''.join(out)

def recover_text(cover, stego, key, frame_size, msg_len):
    total_bits = msg_len * 8
    random.seed(key)
    bits = []

    for frame_idx in range(total_bits):
        frame_start = frame_idx * frame_size
        hop_offset = random.randint(0, frame_size - 1)
        sample_index = frame_start + hop_offset

        diff = stego[sample_index] - cover[sample_index]
        bit = "1" if diff > 0 else "0"
        bits.append(bit)

    return bits_to_text(''.join(bits))

def score_text(text):
    score = 0
    for c in text:
        if c in string.ascii_uppercase + string.digits:
            score += 2
        elif c in string.printable:
            score += 1
        else:
            score -= 4

    # Không in message đầy đủ ở bước search, chỉ dùng prefix để chấm điểm.
    if text.startswith("CHAN"):
        score += 30
    elif text.startswith("CH"):
        score += 15

    return score

def safe_preview(text):
    if text.startswith("CHAN"):
        return "CHAN?????"
    if text.startswith("CH"):
        return "CH???????"
    return "?????????"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cover", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--frame-size", type=int, required=True)
    parser.add_argument("--msg-len", type=int, required=True)
    parser.add_argument("--out", default="findings/key_candidates.txt")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    cover = read_samples(args.cover)
    stego = read_samples(args.input)

    results = []
    for key in range(args.start, args.end + 1):
        text = recover_text(cover, stego, key, args.frame_size, args.msg_len)
        results.append((score_text(text), key, safe_preview(text)))

    results.sort(reverse=True)

    with open(args.out, "w", encoding="utf-8") as f:
        for rank, (score, key, preview) in enumerate(results[:10], start=1):
            status = "LIKELY" if preview.startswith("CHAN") else "LOW"
            f.write(f"rank={rank} score={score} key={key} preview={preview} candidate={status}\n")

    print("TOP_KEY_CANDIDATES")
    for rank, (score, key, preview) in enumerate(results[:5], start=1):
        status = "LIKELY" if preview.startswith("CHAN") else "LOW"
        print(f"rank={rank} score={score} key={key} preview={preview} candidate={status}")

    best_score, best_key, best_preview = results[0]
    if best_preview.startswith("CHAN"):
        print("KEY_SEARCH_OK")
        print(f"BEST_KEY={best_key}")
    else:
        print("KEY_SEARCH_FAIL")

if __name__ == "__main__":
    main()
