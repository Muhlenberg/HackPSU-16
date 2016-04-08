import math, sys

__all__ = ['error', 'getsample',
           'max', 'minmax', 'avg', 'rms',
           'bias', 'add', 'mul', 'reverse',
           'cross', 'maxpp', 'avgpp',
           'lin2lin','tomono', 'tostereo', 'ratecv',
           'findfactor', 'findmax', 'findfit',
           'lin2ulaw', 'ulaw2lin',
           'lin2alaw', 'alaw2lin',
           'lin2adpcm', 'adpcm2lin',
          ]

_max = max

class error(Exception):
    """This exception is raised on all audioop errors, such as unknown
    number of bytes per sample, etc."""
    pass

_formats = {
    1: 'b',
    2: 'h',
    4: 'i',
}

def _assamples(fragment, width):
    if isinstance(fragment, str):
        fragment = fragment.encode()
    view = memoryview(fragment)
    try:
        format = _formats[width]
    except KeyError:
        raise error('Size should be 1, 2 or 4')
    try:
        return view.cast(format)
    except TypeError:
        if len(fragment) % width:
            raise error('not a whole number of frames')
        if not fragment: # cannot cast view with zeros in shape or strides
            return memoryview(b'')
        raise

def _newsamples(length, width):
    try:
        format = _formats[width]
    except KeyError:
        raise error('Size should be 1, 2 or 4')
    try:
        return memoryview(bytearray(length * width)).cast(format)
    except TypeError:
        if not length:
            return memoryview(b'')
        raise


def getsample(fragment, width, index):
    """Return the value of sample index from the fragment."""
    fragment = _assamples(fragment, width)
    if not (0 <= index < len(fragment)):
        raise error('Index out of range')
    return fragment[index]


def _bound(value, min, max):
    if value < min + 1: value = min
    elif value > max: value = max
    return value

_bounds = {
    1: lambda value: _bound(value, -0x80, 0x7f),
    2: lambda value: _bound(value, -0x8000, 0x7fff),
    4: lambda value: _bound(value, -0x80000000, 0x7fffffff),
}

def _from16(value, width):
    if width == 1: value >>= 8
    elif width == 4: value <<= 16
    return value

def _to16(value, width):
    if width == 1: value <<= 8
    elif width == 4: value >>= 16
    return value

def _from32(value, width):
    if width == 1: value >>= 24
    elif width == 2: value >>= 16
    return value

def _to32(value, width):
    if width == 1: value <<= 24
    elif width == 2: value <<= 16
    return value


def max(fragment, width):
    """Return the maximum of the absolute value of all samples in a fragment."""
    fragment = _assamples(fragment, width)
    if not fragment:
        return 0
    return _max(map(abs, fragment))

def minmax(fragment, width):
    """Return a tuple consisting of the minimum and maximum values of all
    samples in the sound fragment."""
    fragment = _assamples(fragment, width)
    if not fragment:
        return 0x7fffffff, -0x80000000
    return min(fragment), _max(fragment)

def avg(fragment, width):
    """Return the average over all samples in the fragment."""
    fragment = _assamples(fragment, width)
    if not fragment:
        return 0
    return sum(fragment) // len(fragment)

def rms(fragment, width):
    """Return the root-mean-square of the fragment, i.e. sqrt(sum(S_i^2)/n)."""
    fragment = _assamples(fragment, width)
    if not fragment:
        return 0
    return int(math.sqrt(_sqsum(fragment) / len(fragment)))


def bias(fragment, width, bias):
    """Return a fragment that is the original fragment with a bias added
    to each sample."""
    fragment = _assamples(fragment, width)
    bound = _bounds[width]
    output = _newsamples(len(fragment), width)
    for i, val in enumerate(fragment):
        output[i] = bound(val + bias)
    return output.tobytes()

def add(fragment1, fragment2, width):
    """Return a fragment which is the addition of the two samples passed
    as parameters."""
    fragment1 = _assamples(fragment1, width)
    fragment2 = _assamples(fragment2, width)
    if len(fragment1) != len(fragment2):
        raise error('Lengths should be the same')
    bound = _bounds[width]
    output = _newsamples(len(fragment1), width)
    for i in range(len(fragment1)):
        output[i] = bound(fragment1[i] + fragment2[i])
    return output.tobytes()

def mul(fragment, width, factor):
    """Return a fragment that has all samples in the original fragment
    multiplied by the floating-point value factor."""
    fragment = _assamples(fragment, width)
    bound = _bounds[width]
    output = _newsamples(len(fragment), width)
    for i, val in enumerate(fragment):
        output[i] = int(bound(val * factor))
    return output.tobytes()

def reverse(fragment, width):
    """Reverse the samples in a fragment and returns the modified fragment."""
    fragment = _assamples(fragment, width)
    output = _newsamples(len(fragment), width)
    for i in range(len(fragment)):
        output[len(fragment) - 1 - i] = fragment[i]
    return output.tobytes()


def cross(fragment, width):
    """Return the number of zero crossings in the fragment passed as an
    argument."""
    fragment = _assamples(fragment, width)
    ncross = -1
    prevsign = None
    for val in fragment:
        sign = val < 0
        if sign is not prevsign:
            ncross += 1
        prevsign = sign
    return ncross

def maxpp(fragment, width):
    """Return the maximum peak-peak value in the sound fragment."""
    fragment = _assamples(fragment, width)
    if not fragment:
        return 0
    prevextreme = None
    maxdiff = 0
    prevval = fragment[0]
    prevdiff = None
    for val in fragment[1:]:
        if val != prevval:
            diff = val < prevval
            if prevdiff is (not diff):
                # Derivative changed sign. Compute difference to last
                # extreme value and remember.
                if prevextreme is not None:
                    maxdiff = _max(maxdiff, abs(prevval - prevextreme))
                prevextreme = prevval
            prevval = val
            prevdiff = diff
    return maxdiff

def avgpp(fragment, width):
    """Return the average peak-peak value over all samples in the fragment."""
    fragment = _assamples(fragment, width)
    if not fragment:
        return 0
    prevextreme = None
    sumextreme = 0
    nextreme = 0
    prevval = fragment[0]
    prevdiff = None
    for val in fragment[1:]:
        if val != prevval:
            diff = val < prevval
            if prevdiff is (not diff):
                # Derivative changed sign. Compute difference to last
                # extreme value and remember.
                if prevextreme is not None:
                    sumextreme += abs(prevval - prevextreme)
                    nextreme += 1
                prevextreme = prevval
            prevval = val
            prevdiff = diff
    return sumextreme // nextreme if nextreme else 0


def _sqsum(fragment):
    return sum(val * val for val in fragment)

def _dotprod(fragment1, fragment2):
    return sum(val1 * val2 for val1, val2 in zip(fragment1, fragment2))

def findfactor(fragment, reference):
    """Return the factor with which you should multiply reference to
    make it match as well as possible to fragment."""
    if isinstance(fragment, str):
        fragment = fragment.encode()
    if isinstance(reference, str):
        reference = reference.encode()
    if len(fragment) & 1 or len(reference) & 1:
        raise error('Strings should be even-sized')
    if len(fragment) != len(reference):
        raise error('Samples should be same size')
    fragment = memoryview(fragment).cast('h')
    reference = memoryview(reference).cast('h')
    sum_ri_2 = _sqsum(reference)
    sum_aij_ri = _dotprod(fragment, reference)
    return sum_aij_ri / sum_ri_2

def findmax(fragment, length):
    """Search fragment for a slice of length `length' samples (not bytes!)
    with maximum energy."""
    if isinstance(fragment, str):
        fragment = fragment.encode()
    if len(fragment) & 1:
        raise error('Strings should be even-sized')
    if not (0 <= length <= len(fragment)):
        raise error('Input sample should be longer')
    fragment = memoryview(fragment).cast('h')

    result = _sqsum(fragment[:length])

    best_result = result
    best_j = 0
    for j in range(len(fragment) - length):
        aj_m1 = fragment[j]
        aj_lm1 = fragment[j + length]
        result += aj_lm1 * aj_lm1 - aj_m1 * aj_m1
        if result > best_result:
            best_result = result
            best_j = j + 1

    return best_j

def findfit(fragment, reference):
    """Return a tuple (offset, factor) where offset is the (integer) offset
    into fragment where the optimal match started and factor is the
    (floating-point) factor as per findfactor()."""
    if isinstance(fragment, str):
        fragment = fragment.encode()()
    if isinstance(reference, str):
        reference = reference.encode()()
    if len(fragment) & 1 or len(reference) & 1:
        raise error('Strings should be even-sized')
    if len(fragment) < len(reference):
        raise error('First sample should be longer')
    fragment = memoryview(fragment).cast('h')
    reference = memoryview(reference).cast('h')

    sum_ri_2 = _sqsum(reference)
    sum_aij_2 = _sqsum(fragment[:len(reference)])
    sum_aij_ri = _dotprod(fragment, reference)
    result = (sum_ri_2 * sum_aij_2 - sum_aij_ri * sum_aij_ri) / sum_aij_2

    best_result = result
    best_j = 0
    for j in range(len(fragment) - len(reference)):
        aj_m1 = fragment[j]
        aj_lm1 = fragment[j + len(reference)]
        sum_aij_2 += aj_lm1 * aj_lm1 - aj_m1 * aj_m1
        sum_aij_ri = _dotprod(fragment[j + 1:], reference)
        result = (sum_ri_2 * sum_aij_2 - sum_aij_ri * sum_aij_ri) / sum_aij_2
        if result < best_result:
            best_result = result
            best_j = j + 1

    return best_j, _dotprod(fragment[best_j:], reference) / sum_ri_2


def lin2lin(fragment, width, newwidth):
    """Convert samples between 1-, 2- and 4-byte formats."""
    fragment = _assamples(fragment, width)
    output = _newsamples(len(fragment), newwidth)
    for i, val in enumerate(fragment):
        output[i] = _from32(_to32(val, width), newwidth)
    return output.tobytes()


def tomono(fragment, width, lfactor, rfactor):
    """Convert a stereo fragment to a mono fragment.

    The left channel is multiplied by lfactor and the right channel by
    rfactor before adding the two channels to give a mono signal.
    """
    fragment = _assamples(fragment, width)
    if len(fragment) & 1:
        raise error('not a whole number of frames')
    bound = _bounds[width]
    output = _newsamples(len(fragment) // 2, width)
    for i in range(0, len(fragment), 2):
        val = fragment[i] * lfactor + fragment[i + 1] * rfactor
        output[i // 2] = int(bound(val))
    return output.tobytes()

def tostereo(fragment, width, lfactor, rfactor):
    """Generate a stereo fragment from a mono fragment.

    Each pair of samples in the stereo fragment are computed from the mono
    sample, whereby left channel samples are multiplied by lfactor and
    right channel samples by rfactor.
    """
    fragment = _assamples(fragment, width)
    bound = _bounds[width]
    output = _newsamples(len(fragment) * 2, width)
    for i, val in enumerate(fragment):
        output[i * 2 + 0] = int(bound(val * lfactor))
        output[i * 2 + 1] = int(bound(val * rfactor))
    return output.tobytes()


def _gcd(a, b):
    while b > 0:
        a, b = b, a % b
    return a;

def ratecv(fragment, width, nchannels, inrate, outrate, state,
           weightA=1, weightB=0):
    """Convert the frame rate of the input fragment."""
    if nchannels < 1:
        raise error('# of channels should be >= 1')
    if weightA < 1 or weightB < 0:
        raise error('weightA should be >= 1, weightB should be >= 0')
    if inrate <= 0 or outrate <= 0:
        raise error('sampling rate not > 0')
    fragment = _assamples(fragment, width)

    # divide inrate and outrate by their greatest common divisor
    d = _gcd(inrate, outrate)
    inrate //= d
    outrate //= d
    # divide weightA and weightB by their greatest common divisor
    d = _gcd(weightA, weightB)
    weightA //= d
    weightB //= d

    length = len(fragment) // nchannels  # number of frames

    if state is None:
        d = -outrate
        samps = [(0, 0)] * nchannels
    else:
        d, samps = state
        if len(samps) != nchannels:
            raise error('illegal state argument')
        samps = list(samps)

    # Space for the output buffer.
    # There are length input frames, so we need (mathematically)
    # ceiling(length*outrate/inrate) output frames.
    outlength = 1 + (length * outrate - 1) // inrate
    output = _newsamples(outlength * nchannels, width)

    i = 0
    j = 0
    while True:
        while d < 0:
            if length == 0:
                return bytes(output[:j]), (d, tuple(samps))
            for chan, (_, prev) in enumerate(samps):
                cur = _to32(fragment[i], width)
                i += 1
                # implements a simple digital filter
                cur = (weightA * cur + weightB * prev) // (weightA + weightB)
                samps[chan] = prev, cur
            length -= 1
            d += outrate
        while d >= 0:
            for prev, cur in samps:
                cur_o = (prev * d + cur * (outrate - d)) // outrate
                output[j] = _from32(cur_o, width)
                j += 1
            d -= inrate


def _st_14linear2ulaw(pcm_val):       # 2's complement (14-bit range)
    # The original sox code does this in the calling function, not here
    pcm_val >>= 2

    # u-law inverts all bits
    # Get the sign and the magnitude of the value.
    if pcm_val < 0:
        pcm_val = -pcm_val
        mask = 0xff ^ 0x80
    else:
        mask = 0xff
    pcm_val += 0b100001

    # Convert the scaled magnitude to segment number.
    seg = pcm_val.bit_length() - 6

    # Combine the sign, segment, quantization bits;
    # and complement the code word.
    if seg > 7:           # out of range, return maximum value.
        uval = 0x7f
    elif seg <= 0:
        uval = (pcm_val >> 1) & 0xf
    else:
        uval = (seg << 4) | ((pcm_val >> (seg + 1)) & 0xf)
    return uval ^ mask

_st_ulaw2linear16 = [
    -32124,  -31100,  -30076,  -29052,  -28028,  -27004,  -25980,  -24956,  
    -23932,  -22908,  -21884,  -20860,  -19836,  -18812,  -17788,  -16764,  
    -15996,  -15484,  -14972,  -14460,  -13948,  -13436,  -12924,  -12412,  
    -11900,  -11388,  -10876,  -10364,   -9852,   -9340,   -8828,   -8316,  
     -7932,   -7676,   -7420,   -7164,   -6908,   -6652,   -6396,   -6140,  
     -5884,   -5628,   -5372,   -5116,   -4860,   -4604,   -4348,   -4092,  
     -3900,   -3772,   -3644,   -3516,   -3388,   -3260,   -3132,   -3004,  
     -2876,   -2748,   -2620,   -2492,   -2364,   -2236,   -2108,   -1980,  
     -1884,   -1820,   -1756,   -1692,   -1628,   -1564,   -1500,   -1436,  
     -1372,   -1308,   -1244,   -1180,   -1116,   -1052,    -988,    -924,  
      -876,    -844,    -812,    -780,    -748,    -716,    -684,    -652,  
      -620,    -588,    -556,    -524,    -492,    -460,    -428,    -396,  
      -372,    -356,    -340,    -324,    -308,    -292,    -276,    -260,  
      -244,    -228,    -212,    -196,    -180,    -164,    -148,    -132,  
      -120,    -112,    -104,     -96,     -88,     -80,     -72,     -64,  
       -56,     -48,     -40,     -32,     -24,     -16,      -8,       0,  
     32124,   31100,   30076,   29052,   28028,   27004,   25980,   24956,  
     23932,   22908,   21884,   20860,   19836,   18812,   17788,   16764,  
     15996,   15484,   14972,   14460,   13948,   13436,   12924,   12412,  
     11900,   11388,   10876,   10364,    9852,    9340,    8828,    8316,  
      7932,    7676,    7420,    7164,    6908,    6652,    6396,    6140,  
      5884,    5628,    5372,    5116,    4860,    4604,    4348,    4092,  
      3900,    3772,    3644,    3516,    3388,    3260,    3132,    3004,  
      2876,    2748,    2620,    2492,    2364,    2236,    2108,    1980,  
      1884,    1820,    1756,    1692,    1628,    1564,    1500,    1436,  
      1372,    1308,    1244,    1180,    1116,    1052,     988,     924,  
       876,     844,     812,     780,     748,     716,     684,     652,  
       620,     588,     556,     524,     492,     460,     428,     396,  
       372,     356,     340,     324,     308,     292,     276,     260,  
       244,     228,     212,     196,     180,     164,     148,     132,  
       120,     112,     104,      96,      88,      80,      72,      64,  
        56,      48,      40,      32,      24,      16,       8,       0,
]

def lin2ulaw(fragment, width):
    """Convert samples in the audio fragment to u-LAW encoding."""
    fragment = _assamples(fragment, width)
    output = bytearray(len(fragment))
    for i, val in enumerate(fragment):
        output[i] = _st_14linear2ulaw(_to16(val, width))
    return bytes(output)

def ulaw2lin(fragment, width):
    """Convert sound fragments in u-LAW encoding to linearly encode()d sound
    fragments."""
    if isinstance(fragment, str):
        fragment = fragment.encode()()
    output = _newsamples(len(fragment), width)
    for i, val in enumerate(fragment):
        output[i] = _from16(_st_ulaw2linear16[val], width)
    return output.tobytes()



_SIGN_BIT = 0x80          # Sign bit for a A-law byte.
_QUANT_MASK = 0xf         # Quantization field mask.
_SEG_SHIFT = 4            # Left shift for segment number.
_SEG_MASK = 0x70          # Segment field mask.

def _st_linear2alaw(pcm_val): # 2's complement (13-bit range)
    # The original sox code does this in the calling function, not here
    pcm_val >>= 3

    # A-law using even bit inversion
    if pcm_val >= 0:
        mask = 0x55 | 0x80     # sign (7th) bit = 1
    else:
        mask = 0x55            # sign bit = 0
        pcm_val = ~pcm_val

    # Convert the scaled magnitude to segment number.
    seg = pcm_val.bit_length() - 5

    # Combine the sign, segment, and quantization bits.

    if seg > 7:  # out of range, return maximum value.
        aval = 0x7F
    elif seg <= 0:
        aval = pcm_val >> 1
    else:
        aval = (seg << 4) | (pcm_val >> seg) & 0xf
    return aval ^ mask

_st_alaw2linear16 = [
     -5504,   -5248,   -6016,   -5760,   -4480,   -4224,   -4992,   -4736,  
     -7552,   -7296,   -8064,   -7808,   -6528,   -6272,   -7040,   -6784,  
     -2752,   -2624,   -3008,   -2880,   -2240,   -2112,   -2496,   -2368,  
     -3776,   -3648,   -4032,   -3904,   -3264,   -3136,   -3520,   -3392,  
    -22016,  -20992,  -24064,  -23040,  -17920,  -16896,  -19968,  -18944,  
    -30208,  -29184,  -32256,  -31232,  -26112,  -25088,  -28160,  -27136,  
    -11008,  -10496,  -12032,  -11520,   -8960,   -8448,   -9984,   -9472,  
    -15104,  -14592,  -16128,  -15616,  -13056,  -12544,  -14080,  -13568,  
      -344,    -328,    -376,    -360,    -280,    -264,    -312,    -296,  
      -472,    -456,    -504,    -488,    -408,    -392,    -440,    -424,  
       -88,     -72,    -120,    -104,     -24,      -8,     -56,     -40,  
      -216,    -200,    -248,    -232,    -152,    -136,    -184,    -168,  
     -1376,   -1312,   -1504,   -1440,   -1120,   -1056,   -1248,   -1184,  
     -1888,   -1824,   -2016,   -1952,   -1632,   -1568,   -1760,   -1696,  
      -688,    -656,    -752,    -720,    -560,    -528,    -624,    -592,  
      -944,    -912,   -1008,    -976,    -816,    -784,    -880,    -848,  
      5504,    5248,    6016,    5760,    4480,    4224,    4992,    4736,  
      7552,    7296,    8064,    7808,    6528,    6272,    7040,    6784,  
      2752,    2624,    3008,    2880,    2240,    2112,    2496,    2368,  
      3776,    3648,    4032,    3904,    3264,    3136,    3520,    3392,  
     22016,   20992,   24064,   23040,   17920,   16896,   19968,   18944,  
     30208,   29184,   32256,   31232,   26112,   25088,   28160,   27136,  
     11008,   10496,   12032,   11520,    8960,    8448,    9984,    9472,  
     15104,   14592,   16128,   15616,   13056,   12544,   14080,   13568,  
       344,     328,     376,     360,     280,     264,     312,     296,  
       472,     456,     504,     488,     408,     392,     440,     424,  
        88,      72,     120,     104,      24,       8,      56,      40,  
       216,     200,     248,     232,     152,     136,     184,     168,  
      1376,    1312,    1504,    1440,    1120,    1056,    1248,    1184,  
      1888,    1824,    2016,    1952,    1632,    1568,    1760,    1696,  
       688,     656,     752,     720,     560,     528,     624,     592,  
       944,     912,    1008,     976,     816,     784,     880,     848,  
]

def lin2alaw(fragment, width):
    """Convert samples in the audio fragment to a-LAW encoding."""
    fragment = _assamples(fragment, width)
    output = bytearray(len(fragment))
    for i, val in enumerate(fragment):
        output[i] = _st_linear2alaw(_to16(val, width))
    return bytes(output)

def alaw2lin(fragment, width):
    """Convert sound fragments in a-LAW encoding to linearly encode()d sound
    fragments."""
    if isinstance(fragment, str):
        fragment = fragment.encode()()
    output = _newsamples(len(fragment), width)
    for i, cval in enumerate(fragment):
        output[i] = _from16(_st_alaw2linear16[cval], width)
    return output.tobytes()



# Intel ADPCM step variation table
_indexTable = [
    -1, -1, -1, -1, 2, 4, 6, 8,
    -1, -1, -1, -1, 2, 4, 6, 8,
]

_stepsizeTable = [
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
    19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
    130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
    337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
    876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066,
    2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358,
    5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899,
    15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767
]

def lin2adpcm(fragment, width, state):
    """Convert samples to 4 bit Intel/DVI ADPCM encoding."""
    fragment = _assamples(fragment, width)
    output = bytearray(len(fragment) // 2)
    if state is None:
        state = 0, 0
    valpred, index = state
    outputbuffer = None

    step = _stepsizeTable[index]
    for i, val in enumerate(fragment):
        val = _to16(val, width)
        # Step 1 - compute difference with previous value
        diff = val - valpred
        sign = 8 if diff < 0 else 0
        diff = abs(diff)

        # Step 2 - Divide and clamp
        # Note:
        # This code *approximately* computes:
        #    delta = diff*4/step;
        #    vpdiff = (delta+0.5)*step/4;
        # but in shift step bits are dropped. The net result of this
        # is that even if you have fast mul/div hardware you cannot
        # put it to good use since the fixup would be too expensive.
        delta = 0
        vpdiff = step >> 3
        if diff >= step:
            delta = 4
            diff -= step
            vpdiff += step
        step >>= 1
        if diff >= step:
            delta |= 2
            diff -= step
            vpdiff += step
        step >>= 1
        if diff >= step:
            delta |= 1
            vpdiff += step

        # Step 3 - Update previous value
        if sign:
            valpred -= vpdiff
        else:
            valpred += vpdiff

        # Step 4 - Clamp previous value to 16 bits
        valpred = _bounds[2](valpred)

        # Step 5 - Assemble value, update index and step values
        delta |= sign
        index += _indexTable[delta]
        index = _bound(index, 0, 88)
        step = _stepsizeTable[index]

        # Step 6 - Output value
        if outputbuffer is None:
            outputbuffer = (delta << 4) & 0xf0
        else:
            output[i >> 1] = (delta & 0x0f) | outputbuffer
            outputbuffer = None
    return bytes(output), (valpred, index)

def adpcm2lin(fragment, width, state):
    """Decode an Intel/DVI ADPCM coded fragment to a linear fragment."""
    if isinstance(fragment, str):
        fragment = fragment.encode()()
    if state is None:
        state = 0, 0
    valpred, index = state
    output = _newsamples(len(fragment) * 2, width)
    step = _stepsizeTable[index]
    for i in range(len(output)):
        # Step 1 - get the delta value and compute next index
        if i & 1:
            delta = inputbuffer & 0xf
        else:
            inputbuffer = fragment[i >> 1]
            delta = (inputbuffer >> 4) & 0xf

        # Step 2 - Find new index value (for later)
        index += _indexTable[delta]
        index = _bound(index, 0, 88)

        # Step 3 - Separate sign and magnitude
        sign = delta & 8
        delta &= 7

        # Step 4 - Compute difference and new predicted value
        # Computes 'vpdiff = (delta+0.5)*step/4', but see comment
        # in adpcm_coder.
        vpdiff = step >> 3
        if delta & 4: vpdiff += step
        if delta & 2: vpdiff += step >> 1
        if delta & 1: vpdiff += step >> 2
        if sign:
            valpred -= vpdiff
        else:
            valpred += vpdiff

        # Step 5 - clamp output value
        valpred = _bounds[2](valpred)

        # Step 6 - Update step value
        step = _stepsizeTable[index]

        # Step 6 - Output value
        output[i] = _from16(valpred, width)

    return output.tobytes(), (valpred, index)

