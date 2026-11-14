# Makes a copy of Seeed's sscma-node (reCamera OS 0.2.4 build) with the scaler queue depth set to 1 instead of 3.
# That removes the 9 fps cap. It changes one register in three store instructions, 6 bytes in all.
# It refuses any binary but the exact 0.2.4 one. It does not touch the input file.
# Usage: patch_sscma_node_depth.py <stock sscma-node> <output file>
import hashlib, struct, sys

STOCK_SHA256 = "fe50cc773d800840d7da5753312e9775ebda3bc77db29766e0700622bc2e6476"
PATCHED_SHA256 = "e1cf4617fc6a13627a43bf57c9f319a6b9d6d9d5307120b41bf9dcebf5731786"
# File offset -> offset of u32Depth from s0, for scaler channels 0, 1 and 2. Each is `sw s2, depth(s0)`.
# s2 holds 3 here and is reused later as the channel count, so it must stay. a5 holds 1 at all three places
# (loaded by `c.li a5, 1` at file offset 0x7af40 and not changed before them), so the stores are switched to a5.
SITES = {0x7afa0: 0x60, 0x7aff2: 0xbc, 0x7b032: 0x118}
S0, S2, A5 = 8, 18, 15

b = bytearray(open(sys.argv[1], "rb").read())
if hashlib.sha256(b).hexdigest() != STOCK_SHA256:
    sys.exit("not the reCamera OS 0.2.4 sscma-node; refusing to patch")
assert struct.unpack_from("<H", b, 0x7af40)[0] == 0x4785, "expected c.li a5, 1"
for off, depth_off in SITES.items():
    w, = struct.unpack_from("<I", b, off)
    assert w & 0x7f == 0x23 and (w >> 12) & 7 == 2, "expected a sw instruction"
    assert (w >> 20) & 31 == S2 and (w >> 15) & 31 == S0, "expected sw s2, x(s0)"
    assert (((w >> 25) << 5) | ((w >> 7) & 31)) == depth_off, "unexpected store offset"
    struct.pack_into("<I", b, off, (w & ~(31 << 20)) | (A5 << 20))
assert hashlib.sha256(b).hexdigest() == PATCHED_SHA256
open(sys.argv[2], "wb").write(b)
print("wrote", sys.argv[2], "sha256", PATCHED_SHA256[:16])
