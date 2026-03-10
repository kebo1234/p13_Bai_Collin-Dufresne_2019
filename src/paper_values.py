"""Published values from Bai, Collin-Dufresne (2019) Table 1 for comparison."""

PAPER_TABLE1 = {
    'ALL': {
        'Before Crisis': {'mean': -10, 'sd': 59, 'p10': -57, 'p90': 45},
        'Crisis I': {'mean': -118, 'sd': 192, 'p10': -273, 'p90': 14}, 
        'Crisis II': {'mean': -324, 'sd': 369, 'p10': -667, 'p90': -55},
        'Post-crisis': {'mean': -137, 'sd': 152, 'p10': -268, 'p90': -32}
    },
    'IG': {
        'Before Crisis': {'mean': -17, 'sd': 30, 'p10': -51, 'p90': 17},
        'Crisis I': {'mean': -83, 'sd': 108, 'p10': -150, 'p90': -10},
        'Crisis II': {'mean': -243, 'sd': 256, 'p10': -451, 'p90': -48},
        'Post-crisis': {'mean': -101, 'sd': 71, 'p10': -173, 'p90': -32}
    },
    'HY': {
        'Before Crisis': {'mean': 12, 'sd': 104, 'p10': -107, 'p90': 142},
        'Crisis I': {'mean': -180, 'sd': 265, 'p10': -486, 'p90': 57},
        'Crisis II': {'mean': -560, 'sd': 504, 'p10': -1248, 'p90': -114},
        'Post-crisis': {'mean': -237, 'sd': 242, 'p10': -477, 'p90': -35}
    }
}