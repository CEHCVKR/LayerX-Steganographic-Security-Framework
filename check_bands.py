import sys
sys.path.append('03. Image Processing Module')
from a3_image_processing import *
import cv2

img = cv2.imread('test_lena.png', 0)
bands = dwt_decompose(img, 2)

print('Band sizes:')
embed_bands = ['LH1', 'HL1', 'LH2', 'HL2', 'HH1', 'HH2', 'LL2']
total = 0
for b in embed_bands:
    if b in bands:
        s = bands[b].shape
        count = (s[0]-8) * (s[1]-8)
        print(f'  {b}: {s} -> {count}')
        total += count
print(f'Total: {total}')
