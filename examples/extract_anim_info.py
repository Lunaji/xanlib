#!/usr/bin/env python3
# Extracts animation information from an XBF file
# Usage: python extract_anim_info.py <path to xbf file>
# Example: python extract_anim_info.py Data/3DDATA0001/Buildings/AT_MGT_H0.xbf

from struct import unpack, calcsize
import argparse

animation_names = [
 'Stationary',
 'Idle 0',
 'Idle 1',
 'Move Start',
 'Move Stop',
 'Move',
 'Turn Left',
 'Turn Right',
 'Fire 0',
 'Fire 1',
 'Fire 2',
 'Fire 3',
 'Fire 4',
 'Explode',
 'Blow Up 1',
 'Blow Up 2',
 'Shot 1',
 'Shot 2',
 'Burnt 1',
 'Run Over 1',
 'Gassed 1',
 'Deployed Death 1',
 'Deployed Death 2',
 'Deploy Gun',
 'Deploy Gun Hold',
 'Undeploy Gun',
 'Deployed Idle 0',
 'Deployed Fire',
 'DeployedDeath0',
 'Harv Unload Start',
 'Harv Unload Hold',
 'Harv Unload End',
 'Harv Eat Start',
 'Harv Eat Hold',
 'Harv Eat End',
 'Repair Arms Out',
 'Repair Arms Hold',
 'Repair Arms In',
 'Sink',
 'SinkHold',
 'Surface',
 'SinkMove',
 'Move Special',
 'StandToLayDown',
 'LayDownToStand',
 'Lay Down',
 'Crawl',
 'Lay Down Fire',
 'Crouch',
 'CrouchFire',
 'Construct',
 'Deconstruct',
 'Takeoff',
 'Land',
 'Hover',
 'Fly',
 'FlyToHover',
 'HoverToFly',
 'StartPickup',
 'Pickup',
 'EndPickup',
 'Enter Portal',
 'Exit Portal',
 'Win',
 'Leeched',
 'Leech Death',
 'Born',
 'Refinery Pad 1',
 'Refinery Pad 2',
 'Sell',
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        xbf_bytes = f.read()

    for animation_name in animation_names:
        offset = xbf_bytes.find(animation_name.encode('ascii')+b'\x00')

        if offset == -1:
            continue

        header_format = '<32si'
        header_size = calcsize(header_format)
        name, unknown_1 = unpack(header_format, xbf_bytes[offset:offset + header_size])

        name = name.split(b'\x00')[0].decode('ascii')

        range_format = '<3i?3s2i'
        range_size = calcsize(range_format)
        is_last = False
        i = 0
        frame_ranges = []
        while not is_last:
            data_slice = xbf_bytes[offset + header_size + i * range_size:offset + header_size + (i + 1) * range_size]
            unknown_2, repeat, body_part, is_last, padding, start, end = unpack(range_format, data_slice)
            frame_ranges.append(f'{start}-{end}')
            i += 1

        print(f'{name}: ' + ', '.join(frame_ranges))