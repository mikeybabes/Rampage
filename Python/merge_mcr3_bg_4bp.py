import sys
from itertools import permutations

def get_best_plane_permutation(data0, data1, num_chars):
    perms = list(permutations([0,1,2,3]))
    best_score = -1
    best_perm = None
    for perm in perms:
        results = []
        for t in range(min(16,num_chars)):
            pixels = []
            chunk0 = data0[t*16:(t+1)*16]
            chunk1 = data1[t*16:(t+1)*16]
            for byte_idx in range(16):
                b0 = chunk0[byte_idx]
                b1 = chunk1[byte_idx]
                for i in range(4):
                    shift = 7 - (i*2)
                    p = [
                        (b0 >> shift) & 1,          # plane 0
                        (b0 >> (shift - 1)) & 1,    # plane 1
                        (b1 >> shift) & 1,          # plane 2
                        (b1 >> (shift - 1)) & 1,    # plane 3
                    ]
                    color = (p[perm[0]] |
                             (p[perm[1]] << 1) |
                             (p[perm[2]] << 2) |
                             (p[perm[3]] << 3))
                    pixels.append(color)
            unique = sorted(set(pixels))
            results.append(unique)
        score = sum((results[i] == [i]) for i in range(min(16,num_chars)))
        if score > best_score:
            best_score = score
            best_perm = perm
        if score == 16:
            break
    return best_perm

def process_inverted_to_linear(inverted0, inverted1, outbin, plane_perm=None, xor_val=None):
    with open(inverted0, "rb") as f:
        data0 = bytearray(f.read())
    with open(inverted1, "rb") as f:
        data1 = bytearray(f.read())
    assert len(data0) == len(data1)
    num_chars = len(data0) // 16

    if xor_val is not None:
        for i in range(len(data0)):
            data0[i] ^= xor_val
            data1[i] ^= xor_val

    # If no permutation given, auto-detect from first 16 chars
    if plane_perm is None:
        plane_perm = get_best_plane_permutation(data0, data1, num_chars)
        print(f"Auto-detected plane permutation: {plane_perm}")

    output = bytearray()
    for t in range(num_chars):
        pixels = []
        chunk0 = data0[t*16:(t+1)*16]
        chunk1 = data1[t*16:(t+1)*16]
        for byte_idx in range(16):
            b0 = chunk0[byte_idx]
            b1 = chunk1[byte_idx]
            for i in range(4):
                shift = 7 - (i*2)
                p = [
                    (b0 >> shift) & 1,          # plane 0
                    (b0 >> (shift - 1)) & 1,    # plane 1
                    (b1 >> shift) & 1,          # plane 2
                    (b1 >> (shift - 1)) & 1,    # plane 3
                ]
                color = (p[plane_perm[0]] |
                         (p[plane_perm[1]] << 1) |
                         (p[plane_perm[2]] << 2) |
                         (p[plane_perm[3]] << 3))
                pixels.append(color)
        # Pack as 2 pixels per byte, 32 bytes per tile
        for i in range(0, 64, 2):
            output.append((pixels[i] << 4) | (pixels[i+1] & 0xF))
    with open(outbin, "wb") as f:
        f.write(output)
    print(f"Wrote {num_chars} tiles ({len(output)} bytes) as linear 4bpp to {outbin}")

if __name__ == "__main__":
    xor_val = None
    perm = None
    # Basic usage: file0, file1, output
    if len(sys.argv) < 4:
        print(f"Usage: python {sys.argv[0]} inverted0.bin inverted1.bin output.bin [perm0 perm1 perm2 perm3] [--xor XX]")
        sys.exit(1)
    args = sys.argv[1:]
    if '--xor' in args:
        idx = args.index('--xor')
        xor_arg = args[idx+1]
        xor_val = int(xor_arg, 16) if xor_arg.startswith('0x') or xor_arg.startswith('0X') else int(xor_arg, 16)
        # Remove --xor and its value from the argument list for normal parsing
        args = args[:idx] + args[idx+2:]
    if len(args) == 7:  # includes permutation
        perm = tuple(int(x) for x in args[3:7])
    process_inverted_to_linear(args[0], args[1], args[2], plane_perm=perm, xor_val=xor_val)
