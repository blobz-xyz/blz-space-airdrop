import math
from web3.utils.address import to_checksum_address
from pprint import pprint as pp

CSV_LIST = [
    #[ '../csv/Space BLOBz Tier S.csv', 's', 10_000 ],
    #[ '../csv/Space BLOBz Tier A.csv', 'a', 1_000 ],
    #[ '../csv/Space BLOBz Tier B.csv', 'b', 100 ],
    #[ '../csv/Space BLOBz Tier C.csv', 'c', 10 ],

    # 20241012
    #[ '../csv/20241012/Space BLOBz Tier S.csv', 's', 10_000 ],
    #[ '../csv/20241012/Space BLOBz Tier A.csv', 'a', 1_000 ],
    #[ '../csv/20241012/Space BLOBz Tier B.csv', 'b', 100 ],
    #[ '../csv/20241012/Space BLOBz Tier C.csv', 'c', 10 ],

    # 20241028
    [ '../csv/20241028/Space BLOBz Tier S.csv', 's', 10_000 ],
    [ '../csv/20241028/Space BLOBz Tier A.csv', 'a', 1_000 ],
    [ '../csv/20241028/Space BLOBz Tier B.csv', 'b', 100 ],
    [ '../csv/20241028/Space BLOBz Tier C.csv', 'c', 10 ],
]
SKIP_ADDRS = [
    '0x0000000000000000000000000000000000000000',
]
#SUPPLY = 17_692_841 #17,692,841.533338594688095218
#SUPPLY = 11_004_424 # 20241012
SUPPLY = 6_900_753 # 20241028

chunk = {}

# load snapshot data
for (csv_path, tier, rate) in CSV_LIST:
    tier_qty = 0
    with open(csv_path, 'r') as file:
        for line in file:
            # extract data
            [addr, qty] = line.strip().split(',')
            addr = addr.lower() # [!] use address in lowercase format
                                # [!] prevent sensitive address issue
            qty = int(qty)

            # skip some addresses
            if addr in SKIP_ADDRS:
                continue

            # update chunk
            wallet = chunk.get(addr) or {}
            points = wallet.get('points') or 0
            wallet[tier] = qty
            wallet['points'] = points + (qty * rate)
            chunk[addr] = wallet

            # update tier qty
            tier_qty += qty

    # recheck tier supply
    print(tier, csv_path, tier_qty)

# sum points
sum_points = 0
for (addr, info) in chunk.items():
    sum_points += info['points']

# calc reward + add checksum addr
for (addr, info) in chunk.items():
    info['reward'] = SUPPLY * (info['points'] / sum_points)
    info['addr'] = to_checksum_address(addr)

# reshape chunk
chunk = chunk.values()

# sort by points, address
chunk = sorted(chunk, key=lambda x: (-x['points'], x['addr']))

# add no
cur_no = None
cur_points = None
for (idx, info) in enumerate(chunk):
    if info['points'] != cur_points:
        cur_no = idx + 1
        cur_points = info['points']
    info['no'] = cur_no

# print output (header)
print("#,Address,BLZ,Points,S,A,B,C")

# print output (body)
for c in chunk:
    reward = math.floor(c['reward'] * 1_000) / 1_000 # floor 3 digits
    print('{},{},{},{},{},{},{},{}'.format(
        c['no'],        # no
        c['addr'],      # addr
        reward,         # reward
        c['points'],    # points
        c.get('s') or 0,# tier S
        c.get('a') or 0,# tier A
        c.get('b') or 0,# tier B
        c.get('c') or 0,# tier C
    ))
