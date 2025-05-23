# Magic bitboard helpers for chess engine
import numpy as np

# Magic numbers for rooks and bishops
# These are random 64-bit numbers that when multiplied by certain positions 
# create a unique pattern for lookup tables
ROOK_MAGICS = [
    0x8a80104000800020, 0x140002000100040, 0x2801880a0017001, 0x100081001000420,
    0x200020010080420, 0x3001c0002010008, 0x8480008002000100, 0x2080088004402900,
    0x800098204000, 0x2024401000200040, 0x100802000801000, 0x120800800801000,
    0x208808088000400, 0x2802200800400, 0x2200800100020080, 0x801000060821100,
    0x80044006422000, 0x100808020004000, 0x12108a0010204200, 0x140848010000802,
    0x481828014002800, 0x8094004002004100, 0x4010040010010802, 0x20008806104,
    0x100400080208000, 0x2040002120081000, 0x21200680100081, 0x20100080080080,
    0x2000a00200410, 0x20080800400, 0x80088400100102, 0x80004600042881,
    0x4040008040800020, 0x440003000200801, 0x4200011004500, 0x188020010100100,
    0x14800401802800, 0x2080040080800200, 0x124080204001001, 0x200046502000484,
    0x480400080088020, 0x1000422010034000, 0x30200100110040, 0x100021010009,
    0x2002080100110004, 0x202008004008002, 0x20020004010100, 0x2048440040820001,
    0x101002200408200, 0x40802000401080, 0x4008142004410100, 0x2060820c0120200,
    0x1001004080100, 0x20c020080040080, 0x2935610830022400, 0x44440041009200,
    0x280001040802101, 0x2100190040002085, 0x80c0084100102001, 0x4024081001000421,
    0x20030a0244872, 0x12001008414402, 0x2006104900a0804, 0x1004081002402
]

BISHOP_MAGICS = [
    0x40040844404084, 0x2004208a004208, 0x10190041080202, 0x108050020b0410,
    0x581104180800210, 0x2112080446200010, 0x1080820820060210, 0x3c0808410220200,
    0x4050404440404, 0x21001420088, 0x24d0080801082102, 0x1020a0a020400,
    0x40308200402, 0x4011002100800, 0x401484104104005, 0x801010402020200,
    0x400210c3880100, 0x404022024108200, 0x810018200204102, 0x4002801a02003,
    0x85040820080400, 0x810102c808880400, 0xe900410884800, 0x8002020480840102,
    0x220200865090201, 0x2010100a02021202, 0x152048408022401, 0x20080002081110,
    0x4001001021004000, 0x800040400a011002, 0xe4004081011002, 0x1c004001012080,
    0x8004200962a00220, 0x8422100208500202, 0x2000402200300c08, 0x8646020080080080,
    0x80020a0200100808, 0x2010004880111000, 0x623000a080011400, 0x42008c0340209202,
    0x209188240001000, 0x400408a884001800, 0x110400a6080400, 0x1840060a44020800,
    0x90080104000041, 0x201011000808101, 0x1a2208080504f080, 0x8012020600211212,
    0x500861011240000, 0x180806108200800, 0x4000020e01040044, 0x300000261044000a,
    0x802241102020002, 0x20906061210001, 0x5a84841004010310, 0x4010801011c04,
    0xa010109502200, 0x4a02012000, 0x500201010098b028, 0x8040002811040900,
    0x28000010020204, 0x6000020202d0240, 0x8918844842082200, 0x4010011029020020
]

# Shifts for indexing (bits to shift right after multiplication)
ROOK_SHIFTS = [
    12, 11, 11, 11, 11, 11, 11, 12,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12
]

BISHOP_SHIFTS = [
    6, 5, 5, 5, 5, 5, 5, 6,
    5, 5, 5, 5, 5, 5, 5, 5,
    5, 5, 7, 7, 7, 7, 5, 5,
    5, 5, 7, 9, 9, 7, 5, 5,
    5, 5, 7, 9, 9, 7, 5, 5,
    5, 5, 7, 7, 7, 7, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5,
    6, 5, 5, 5, 5, 5, 5, 6
]

# Attack lookup tables
ROOK_ATTACKS = []
BISHOP_ATTACKS = []
ROOK_MASKS = []
BISHOP_MASKS = []

def init_magics():
    """Initialize all the magic bitboard tables"""
    global ROOK_ATTACKS, BISHOP_ATTACKS, ROOK_MASKS, BISHOP_MASKS
    
    # Initialize masks
    for square in range(64):
        ROOK_MASKS.append(create_rook_mask(square))
        BISHOP_MASKS.append(create_bishop_mask(square))
    
    # Initialize attack tables
    ROOK_ATTACKS = [None] * 64
    BISHOP_ATTACKS = [None] * 64
    
    for square in range(64):
        rook_bits = count_bits(ROOK_MASKS[square])
        bishop_bits = count_bits(BISHOP_MASKS[square])
        
        rook_size = 1 << rook_bits
        bishop_size = 1 << bishop_bits
        
        ROOK_ATTACKS[square] = [0] * rook_size
        BISHOP_ATTACKS[square] = [0] * bishop_size
        
        # Generate all possible blocker configurations
        rook_blockers = generate_blockers(ROOK_MASKS[square])
        bishop_blockers = generate_blockers(BISHOP_MASKS[square])
        
        # Fill in the attack tables
        for blockers in rook_blockers:
            magic_index = ((blockers * ROOK_MAGICS[square]) >> (64 - rook_bits)) & ((1 << rook_bits) - 1)
            ROOK_ATTACKS[square][magic_index] = compute_rook_attacks(square, blockers)
        
        for blockers in bishop_blockers:
            magic_index = ((blockers * BISHOP_MAGICS[square]) >> (64 - bishop_bits)) & ((1 << bishop_bits) - 1)
            BISHOP_ATTACKS[square][magic_index] = compute_bishop_attacks(square, blockers)

def count_bits(bitboard):
    """Count the number of set bits in a bitboard.
    
    This implementation uses bit manipulation for faster counting.
    It's more efficient than the traditional loop method.
    
    Args:
        bitboard: A 64-bit integer representing a bitboard
        
    Returns:
        int: The number of bits set to 1 in the bitboard
    """
    # This method uses the built-in function for counting bits
    # which is much faster than a manual loop
    if hasattr(int, "bit_count"):  # Python 3.10+ has bit_count directly
        return bitboard.bit_count()
    else:
        # Fallback to an optimized algorithm (Brian Kernighan's algorithm) 
        # for older Python versions
        count = 0
        while bitboard:
            count += 1
            bitboard &= (bitboard - 1)  # Clear the least significant bit set
        return count

def count_bits_lookup(bitboard):
    """Count the number of set bits using a lookup table approach.
    
    This can be faster for certain applications compared to count_bits.
    
    Args:
        bitboard: A 64-bit integer representing a bitboard
        
    Returns:
        int: The number of bits set to 1 in the bitboard
    """
    # Lookup table for 16-bit segments
    # Each entry contains the number of 1 bits for the value at that index
    lookup = [
        0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
        # ... (would be 65536 entries, truncated for brevity)
    ]
    
    # Compute for 16-bit chunks
    count = 0
    mask16 = 0xFFFF  # 16-bit mask
    
    # Process in 16-bit chunks
    count += lookup[bitboard & mask16]
    count += lookup[(bitboard >> 16) & mask16]
    count += lookup[(bitboard >> 32) & mask16]
    count += lookup[(bitboard >> 48) & mask16]
    
    return count

def create_rook_mask(square):
    """Create a mask for rook movement (excludes edges)"""
    mask = 0
    rank, file = square // 8, square % 8
    
    # Horizontal mask (exclude edges)
    for f in range(file + 1, 7):
        mask |= (1 << (rank * 8 + f))
    for f in range(file - 1, 0, -1):
        mask |= (1 << (rank * 8 + f))
    
    # Vertical mask (exclude edges)
    for r in range(rank + 1, 7):
        mask |= (1 << (r * 8 + file))
    for r in range(rank - 1, 0, -1):
        mask |= (1 << (r * 8 + file))
    
    return mask

def create_bishop_mask(square):
    """Create a mask for bishop movement (excludes edges)"""
    mask = 0
    rank, file = square // 8, square % 8
    
    # Northwest diagonal
    r, f = rank - 1, file - 1
    while r > 0 and f > 0:
        mask |= (1 << (r * 8 + f))
        r -= 1
        f -= 1
    
    # Northeast diagonal
    r, f = rank - 1, file + 1
    while r > 0 and f < 7:
        mask |= (1 << (r * 8 + f))
        r -= 1
        f += 1
    
    # Southwest diagonal
    r, f = rank + 1, file - 1
    while r < 7 and f > 0:
        mask |= (1 << (r * 8 + f))
        r += 1
        f -= 1
    
    # Southeast diagonal
    r, f = rank + 1, file + 1
    while r < 7 and f < 7:
        mask |= (1 << (r * 8 + f))
        r += 1
        f += 1
    
    return mask

def generate_blockers(mask):
    """Generate all possible blocker configurations for a given mask"""
    blockers = []
    bit_count = count_bits(mask)
    combinations = 1 << bit_count
    
    for i in range(combinations):
        blocker = 0
        bit_index = 0
        temp_mask = mask
        
        while temp_mask:
            least_significant_bit = temp_mask & -temp_mask
            temp_mask &= (temp_mask - 1)  # Clear the least significant bit
            
            if (i & (1 << bit_index)):
                blocker |= least_significant_bit
            
            bit_index += 1
        
        blockers.append(blocker)
    
    return blockers

def compute_rook_attacks(square, blockers):
    """Compute rook attacks with blockers"""
    attacks = 0
    rank, file = square // 8, square % 8
    
    # North
    for r in range(rank + 1, 8):
        bit = 1 << (r * 8 + file)
        attacks |= bit
        if blockers & bit:
            break
    
    # South
    for r in range(rank - 1, -1, -1):
        bit = 1 << (r * 8 + file)
        attacks |= bit
        if blockers & bit:
            break
    
    # East
    for f in range(file + 1, 8):
        bit = 1 << (rank * 8 + f)
        attacks |= bit
        if blockers & bit:
            break
    
    # West
    for f in range(file - 1, -1, -1):
        bit = 1 << (rank * 8 + f)
        attacks |= bit
        if blockers & bit:
            break
    
    return attacks

def compute_bishop_attacks(square, blockers):
    """Compute bishop attacks with blockers"""
    attacks = 0
    rank, file = square // 8, square % 8
    
    # Northeast
    r, f = rank + 1, file + 1
    while r < 8 and f < 8:
        bit = 1 << (r * 8 + f)
        attacks |= bit
        if blockers & bit:
            break
        r += 1
        f += 1
    
    # Northwest
    r, f = rank + 1, file - 1
    while r < 8 and f >= 0:
        bit = 1 << (r * 8 + f)
        attacks |= bit
        if blockers & bit:
            break
        r += 1
        f -= 1
    
    # Southeast
    r, f = rank - 1, file + 1
    while r >= 0 and f < 8:
        bit = 1 << (r * 8 + f)
        attacks |= bit
        if blockers & bit:
            break
        r -= 1
        f += 1
    
    # Southwest
    r, f = rank - 1, file - 1
    while r >= 0 and f >= 0:
        bit = 1 << (r * 8 + f)
        attacks |= bit
        if blockers & bit:
            break
        r -= 1
        f -= 1
    
    return attacks

# Initialize magic bitboards when module is loaded
init_magics()

def get_rook_attacks(square, blockers):
    """Get rook attacks using magic bitboard lookup"""
    mask = ROOK_MASKS[square]
    blockers_mask = blockers & mask
    magic = ROOK_MAGICS[square]
    shift = ROOK_SHIFTS[square]
    index = ((blockers_mask * magic) >> (64 - shift)) & ((1 << shift) - 1)
    return ROOK_ATTACKS[square][index]

def get_bishop_attacks(square, blockers):
    """Get bishop attacks using magic bitboard lookup"""
    mask = BISHOP_MASKS[square]
    blockers_mask = blockers & mask
    magic = BISHOP_MAGICS[square]
    shift = BISHOP_SHIFTS[square]
    index = ((blockers_mask * magic) >> (64 - shift)) & ((1 << shift) - 1)
    return BISHOP_ATTACKS[square][index]

def get_slider_attacks(square, blockers, ortho):
    if ortho:
        return get_rook_attacks(square, blockers)
    else:
        return get_bishop_attacks(square, blockers)
