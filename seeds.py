from hashlib import sha256
import random

# You can fetch the wordlist used here by calling: `wget get https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt`
# `python -i seeds.py`
# >>> wordlist = [... list of words]
# >>> find_last(wordlist, word)
# 'profit'
# note that calling this multiple times will result in different last words
# as each 'last word' contains 3-bits of entropy (that we randomly generate here)

def arr_to_int(arr):
    total = 0
    for i, val in enumerate(arr[::-1]):
        total += 2 ** i * val
    return total

def get_exp_entropy(wordlen):
    if wordlen == 11:
        return 128, 4
    if wordlen == 14:
        return 160, 5
    if wordlen == 17:
        return 192, 6
    if wordlen == 20:
        return 224, 7

    assert wordlen == 23
    return 256, 8


def build_last_bits(count):
    last_bits = []
    for x in range(0, 2 ** count):
        bits = list(map(int, '{:0b}'.format(x)))
        while len(bits) < count:
            bits = [0] + bits
        assert len(bits) == count
        last_bits.append(bits)

    return last_bits


def get_word(words, bitslist, cslen):
    g = []
    for x in range(len(bitslist) // 8):
        bits = bitslist[x*8:(x+1)*8]
        g.append(int(''.join([str(x) for x in bits]), 2))

    byte = bytearray(g)
    chksum = int.from_bytes(sha256(byte).digest()[:1], 'little')
    cc = bin(chksum)[2:]
    while len(cc) < 8:
        cc = '0' + cc
    # truncate to required checksum bits
    cc = cc[:cslen]
    totes = bitslist + [int(c) for c in list(cc)]
    assert len(totes) % 11 == 0

    last_word_idx = arr_to_int(totes[-11:])
    return words[last_word_idx]


def find_last(wordlist):
    with open ('english.txt') as f:
        words = f.read().splitlines()

    nums = [words.index(w) for w in wordlist]

    bb = []
    for num in nums:
        b = list(map(int, '{:0b}'.format(num)))
        bb.append((11 - len(b)) * [0])
        bb.append(b)

    flat = [ item for sublist in bb for item in sublist ]
    exp_ent, cs_len = get_exp_entropy(len(nums))

    # collect missing bits
    missing_bits = exp_ent - len(flat)
    last_bits_set = build_last_bits(missing_bits)

    last_words = []
    for bitset in last_bits_set:
        assert len(flat + bitset) == exp_ent
        last_words.append(get_word(words, flat + bitset, cs_len))

    return last_words
