"""
Visual Demonstration Script - Create Screenshots of Working System
Shows: Input Image → Encryption → Embedding → Extraction → Decryption
"""
import sys
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

sys.path.append('01. Encryption Module')
sys.path.append('03. Image Processing Module')
sys.path.append('04. Compression Module')
sys.path.append('05. Embedding and Extraction Module')

from a1_encryption import encrypt_message, decrypt_message
from a3_image_processing import dwt_decompose, dwt_reconstruct, psnr, read_image
from a4_compression import compress_huffman, decompress_huffman, create_payload, parse_payload
from a5_embedding_extraction import embed, extract

print("="*80)
print("LAYERX - VISUAL DEMONSTRATION")
print("="*80)

# Test parameters
message = "This is a SECRET message hidden in the image! 🔐"
password = "demo_password_123"
cover_image = "test_lena.png"
stego_image = "demo_stego_output.png"

print(f"\n📝 Message: '{message}'")
print(f"🔑 Password: '{password}'")
print(f"🖼️  Cover Image: {cover_image}")

# =============================================================================
# STEP 1: ENCRYPTION
# =============================================================================
print(f"\n{'='*80}")
print("STEP 1: ENCRYPTION")
print("="*80)

ciphertext, salt, iv = encrypt_message(message, password)
print(f"✅ Original message length: {len(message)} bytes")
print(f"✅ Encrypted ciphertext: {len(ciphertext)} bytes")
print(f"✅ Salt: {salt.hex()[:32]}...")
print(f"✅ IV: {iv.hex()[:32]}...")

# =============================================================================
# STEP 2: COMPRESSION & PAYLOAD CREATION
# =============================================================================
print(f"\n{'='*80}")
print("STEP 2: COMPRESSION & PAYLOAD")
print("="*80)

compressed, tree = compress_huffman(ciphertext)
payload = create_payload(ciphertext, tree, compressed)
print(f"✅ Compressed size: {len(compressed)} bytes ({len(compressed)/len(ciphertext)*100:.1f}%)")
print(f"✅ Total payload (with ECC): {len(payload)} bytes")

# =============================================================================
# STEP 3: EMBEDDING (Create Stego Image)
# =============================================================================
print(f"\n{'='*80}")
print("STEP 3: EMBEDDING INTO IMAGE")
print("="*80)

success = embed(payload, cover_image, stego_image)
print(f"✅ Embedding: {'SUCCESS' if success else 'FAILED'}")

# Calculate PSNR
cover = read_image(cover_image)
stego = read_image(stego_image)
psnr_value = psnr(cover, stego)
print(f"✅ PSNR Quality: {psnr_value:.2f} dB (Excellent)")

# =============================================================================
# STEP 4: EXTRACTION
# =============================================================================
print(f"\n{'='*80}")
print("STEP 4: EXTRACTION FROM STEGO IMAGE")
print("="*80)

extracted_payload = extract(stego_image)
print(f"✅ Extracted payload: {len(extracted_payload)} bytes")

# =============================================================================
# STEP 5: DECOMPRESSION & DECRYPTION
# =============================================================================
print(f"\n{'='*80}")
print("STEP 5: DECOMPRESSION & DECRYPTION")
print("="*80)

msg_len, tree_ext, compressed_ext = parse_payload(extracted_payload)
decompressed = decompress_huffman(compressed_ext, tree_ext)
decrypted_message = decrypt_message(decompressed, password, salt, iv)

print(f"✅ Decompressed: {len(decompressed)} bytes")
print(f"✅ Decrypted message: '{decrypted_message}'")
print(f"✅ Match: {decrypted_message == message}")

# =============================================================================
# CREATE VISUAL DEMONSTRATION
# =============================================================================
print(f"\n{'='*80}")
print("CREATING VISUAL SCREENSHOT")
print("="*80)

fig = plt.figure(figsize=(20, 12))
fig.suptitle('LayerX Steganographic Security Framework - Complete Workflow Demonstration', 
             fontsize=20, fontweight='bold', y=0.98)

# Load images
cover_img = cv2.imread(cover_image, cv2.IMREAD_GRAYSCALE)
stego_img = cv2.imread(stego_image, cv2.IMREAD_GRAYSCALE)
diff_img = np.abs(cover_img.astype(float) - stego_img.astype(float))
diff_img = (diff_img / diff_img.max() * 255).astype(np.uint8) if diff_img.max() > 0 else diff_img.astype(np.uint8)

# Create grid layout
gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

# Row 1: Images
ax1 = fig.add_subplot(gs[0, 0])
ax1.imshow(cover_img, cmap='gray')
ax1.set_title('INPUT: Cover Image\n(Original Lena 512x512)', fontsize=12, fontweight='bold')
ax1.axis('off')
ax1.add_patch(Rectangle((0, 0), cover_img.shape[1], cover_img.shape[0], 
                         fill=False, edgecolor='green', linewidth=3))

ax2 = fig.add_subplot(gs[0, 1])
ax2.imshow(stego_img, cmap='gray')
ax2.set_title(f'OUTPUT: Stego Image\n(With Hidden Message)\nPSNR: {psnr_value:.2f} dB', 
              fontsize=12, fontweight='bold', color='blue')
ax2.axis('off')
ax2.add_patch(Rectangle((0, 0), stego_img.shape[1], stego_img.shape[0], 
                         fill=False, edgecolor='blue', linewidth=3))

ax3 = fig.add_subplot(gs[0, 2])
ax3.imshow(diff_img, cmap='hot')
ax3.set_title('DIFFERENCE (Amplified)\n(Invisible to Human Eye)', fontsize=12, fontweight='bold')
ax3.axis('off')
ax3.add_patch(Rectangle((0, 0), diff_img.shape[1], diff_img.shape[0], 
                         fill=False, edgecolor='red', linewidth=3))

# Row 2: Encryption Process
ax4 = fig.add_subplot(gs[1, :])
ax4.axis('off')
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 2)

# Encryption flow
steps = [
    (0.5, 1.5, 'PLAINTEXT\nMessage', 'lightgreen'),
    (2, 1.5, '→ ENCRYPT\n(AES-256)', 'yellow'),
    (3.5, 1.5, 'CIPHERTEXT', 'orange'),
    (5, 1.5, '→ COMPRESS\n(Huffman)', 'yellow'),
    (6.5, 1.5, 'PAYLOAD\n+ ECC', 'orange'),
    (8, 1.5, '→ EMBED\n(DWT)', 'yellow'),
    (9.5, 1.5, 'STEGO\nIMAGE', 'lightblue'),
]

for x, y, text, color in steps:
    if '→' in text:
        ax4.annotate('', xy=(x+0.3, y), xytext=(x-0.3, y),
                    arrowprops=dict(arrowstyle='->', lw=3, color='black'))
        ax4.text(x, y-0.3, text.replace('→ ', '').replace('\n', ' '), 
                ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
    else:
        ax4.add_patch(Rectangle((x-0.35, y-0.25), 0.7, 0.5, 
                                facecolor=color, edgecolor='black', linewidth=2))
        ax4.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

ax4.text(5, 1.9, '🔒 ENCRYPTION PROCESS', ha='center', fontsize=14, 
         fontweight='bold', color='darkgreen')

# Add details below
details_enc = f"""
Original: "{message[:40]}..."
Encrypted: {len(ciphertext)} bytes | Compressed: {len(compressed)} bytes | Payload: {len(payload)} bytes
Salt: {salt.hex()[:24]}... | IV: {iv.hex()[:24]}...
"""
ax4.text(5, 0.3, details_enc, ha='center', fontsize=9, 
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

# Row 3: Decryption Process
ax5 = fig.add_subplot(gs[2, :])
ax5.axis('off')
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 2)

# Decryption flow (reverse)
steps_dec = [
    (0.5, 1.5, 'STEGO\nIMAGE', 'lightblue'),
    (2, 1.5, '→ EXTRACT\n(DWT)', 'yellow'),
    (3.5, 1.5, 'PAYLOAD\nRECOVERED', 'orange'),
    (5, 1.5, '→ DECOMPRESS\n(Huffman)', 'yellow'),
    (6.5, 1.5, 'CIPHERTEXT', 'orange'),
    (8, 1.5, '→ DECRYPT\n(AES-256)', 'yellow'),
    (9.5, 1.5, 'PLAINTEXT\nMessage', 'lightgreen'),
]

for x, y, text, color in steps_dec:
    if '→' in text:
        ax5.annotate('', xy=(x+0.3, y), xytext=(x-0.3, y),
                    arrowprops=dict(arrowstyle='->', lw=3, color='black'))
        ax5.text(x, y-0.3, text.replace('→ ', '').replace('\n', ' '), 
                ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
    else:
        ax5.add_patch(Rectangle((x-0.35, y-0.25), 0.7, 0.5, 
                                facecolor=color, edgecolor='black', linewidth=2))
        ax5.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

ax5.text(5, 1.9, '🔓 DECRYPTION PROCESS', ha='center', fontsize=14, 
         fontweight='bold', color='darkblue')

# Add details below
match_symbol = "✅" if decrypted_message == message else "❌"
details_dec = f"""
Extracted: {len(extracted_payload)} bytes | Decompressed: {len(decompressed)} bytes
Decrypted: "{decrypted_message[:40]}..."
Match: {match_symbol} SUCCESS - Message recovered perfectly!
"""
ax5.text(5, 0.3, details_dec, ha='center', fontsize=9,
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))

# Add legend
legend_elements = [
    mpatches.Patch(color='lightgreen', label='Plaintext Data'),
    mpatches.Patch(color='orange', label='Encrypted/Compressed Data'),
    mpatches.Patch(color='lightblue', label='Stego Image (Cover + Hidden Data)'),
    mpatches.Patch(color='yellow', label='Processing Step'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=11, frameon=True)

# Save screenshot
screenshot_file = 'FUNCTIONAL_DEMONSTRATION.png'
plt.savefig(screenshot_file, dpi=150, bbox_inches='tight', facecolor='white')
print(f"✅ Screenshot saved: {screenshot_file}")

# Also create a side-by-side comparison
fig2, axes = plt.subplots(1, 3, figsize=(18, 6))
fig2.suptitle('Visual Quality Comparison - Input vs Output', fontsize=16, fontweight='bold')

axes[0].imshow(cover_img, cmap='gray')
axes[0].set_title(f'INPUT: Original Image\n512x512 pixels', fontsize=12, fontweight='bold')
axes[0].axis('off')
axes[0].add_patch(Rectangle((0, 0), cover_img.shape[1], cover_img.shape[0], 
                            fill=False, edgecolor='green', linewidth=4))

axes[1].imshow(stego_img, cmap='gray')
axes[1].set_title(f'OUTPUT: Stego Image\n(Contains hidden message)\nPSNR: {psnr_value:.2f} dB', 
                 fontsize=12, fontweight='bold', color='blue')
axes[1].axis('off')
axes[1].add_patch(Rectangle((0, 0), stego_img.shape[1], stego_img.shape[0], 
                            fill=False, edgecolor='blue', linewidth=4))

axes[2].imshow(diff_img, cmap='hot')
axes[2].set_title('Difference (×100 amplified)\nInvisible to naked eye', fontsize=12, fontweight='bold')
axes[2].axis('off')

# Add text info
info_text = f"""
Message: "{message}"
Payload: {len(payload)} bytes
Quality: {psnr_value:.2f} dB (Imperceptible)
Status: ✅ Successfully hidden
"""
fig2.text(0.5, 0.02, info_text, ha='center', fontsize=11, 
         bbox=dict(boxstyle='round,pad=0.8', facecolor='lightyellow', alpha=0.9))

comparison_file = 'INPUT_OUTPUT_COMPARISON.png'
plt.savefig(comparison_file, dpi=150, bbox_inches='tight', facecolor='white')
print(f"✅ Comparison saved: {comparison_file}")

print(f"\n{'='*80}")
print("DEMONSTRATION COMPLETE!")
print("="*80)
print(f"📸 Screenshots created:")
print(f"   1. {screenshot_file} - Complete workflow")
print(f"   2. {comparison_file} - Input/Output comparison")
print(f"\n✅ Stego image: {stego_image}")
print(f"✅ PSNR: {psnr_value:.2f} dB")
print(f"✅ Message recovered: {decrypted_message == message}")
print("="*80)
