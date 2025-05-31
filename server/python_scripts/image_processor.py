# server/python_scripts/image_processor.py

import sys
from PIL import Image, ImageEnhance, ImageFilter # Tambahkan ImageFilter
import os

def process_image(input_path, output_path, mode='grayscale', output_format='jpeg'):
    """
    Memproses gambar menggunakan PIL (Pillow).
    input_path: Jalur file gambar input.
    output_path: Jalur untuk menyimpan gambar output.
    mode: 'original', 'enhance', 'grayscale', 'resize', 'cartoon' (atau mode AI lainnya).
    output_format: 'jpeg', 'png', 'webp', 'jpg' (format output yang diinginkan).
    """
    try:
        img = Image.open(input_path)
        print(f"[{os.path.basename(sys.argv[0])}] Membuka gambar: {input_path} (Mode: {img.mode}, Format Asli: {img.format})")

        processed_img = img

        # --- Bagian Simulasi AI / Mode Pemrosesan ---
        if mode == 'original':
            print(f"[{os.path.basename(sys.argv[0])}] Mode 'original': Gambar tidak diubah.")
            processed_img = img
        elif mode == 'enhance':
            enhancer = ImageEnhance.Contrast(img)
            processed_img = enhancer.enhance(1.2)

            enhancer = ImageEnhance.Color(processed_img)
            processed_img = enhancer.enhance(1.1)

            enhancer = ImageEnhance.Brightness(processed_img)
            processed_img = enhancer.enhance(1.1)
            print(f"[{os.path.basename(sys.argv[0])}] Mode 'enhance': Peningkatan Warna/Kontras (Simulasi HD Color).")

        elif mode == 'grayscale':
            processed_img = img.convert('L')
            print(f"[{os.path.basename(sys.argv[0])}] Mengkonversi ke grayscale.")

        elif mode == 'resize':
            target_size = (300, 300)
            processed_img = img.resize(target_size)
            print(f"[{os.path.basename(sys.argv[0])}] Me-resize gambar ke {target_size}.")

        elif mode == 'cartoon': # NEW CARTOON MODE
            print(f"[{os.path.basename(sys.argv[0])}] Mode 'cartoon': Menerapkan efek kartun (simulasi).")
            # Konversi ke RGB untuk memastikan konsistensi
            if img.mode != 'RGB':
                img = img.convert('RGB')
                print(f"[{os.path.basename(sys.argv[0])}] Mengkonversi gambar ke RGB untuk efek kartun.")

            # Langkah 1: Posterisasi (mengurangi jumlah warna)
            # Anda bisa eksperimen dengan nilai bands (misal 4, 6, 8)
            processed_img = img.quantize(colors=64, method=Image.WEBACCESSIBILITY) # Mengurangi warna ke 64

            # Langkah 2: Deteksi tepi dan gabungkan (opsional, bisa bikin gambar lebih gelap)
            # Ini akan membuat garis hitam tebal di tepi
            # edges = img.filter(ImageFilter.FIND_EDGES)
            # processed_img = Image.composite(processed_img, edges.convert('RGB'), edges.convert('1'))

            # Langkah 2 (alternatif): Edge enhancement sederhana
            # processed_img = processed_img.filter(ImageFilter.EDGE_ENHANCE_MORE)

            # Langkah 2 (lebih sederhana): Smoothing untuk tampilan kartun yang lebih rata
            processed_img = processed_img.filter(ImageFilter.SMOOTH)
            processed_img = processed_img.filter(ImageFilter.SMOOTH_MORE)


        else:
            print(f"[{os.path.basename(sys.argv[0])}] Mode pemrosesan tidak dikenal ('{mode}'). Menggunakan gambar asli.")
            processed_img = img

        # --- Simpan Gambar Hasil dalam Format yang Diminta ---
        save_format = output_format.upper()
        if save_format == 'JPG':
            save_format = 'JPEG'
            print(f"[{os.path.basename(sys.argv[0])}] Mengubah format output 'JPG' menjadi 'JPEG' untuk Pillow.")

        if save_format in ['JPEG', 'WEBP'] and processed_img.mode == 'RGBA':
            background = Image.new("RGB", processed_img.size, (255, 255, 255))
            background.paste(processed_img, (0, 0), processed_img)
            processed_img = background
            print(f"[{os.path.basename(sys.argv[0])}] Mengkonversi RGBA ke RGB dengan latar belakang putih untuk format {output_format}.")
        elif save_format in ['JPEG'] and processed_img.mode == 'L':
            processed_img = processed_img.convert('RGB')
            print(f"[{os.path.basename(sys.argv[0])}] Mengkonversi L (grayscale) ke RGB untuk format {output_format}.")
        elif save_format in ['JPEG', 'WEBP'] and processed_img.mode not in ['RGB', 'L']:
            processed_img = processed_img.convert('RGB')
            print(f"[{os.path.basename(sys.argv[0])}] Mengkonversi mode gambar ({processed_img.mode}) ke RGB untuk format {output_format}.")


        save_params = {}
        if save_format in ['JPEG']:
            save_params['quality'] = 90
            save_params['optimize'] = True
        elif save_format == 'WEBP':
            save_params['quality'] = 80
            save_params['method'] = 6
        elif save_format == 'PNG':
            save_params['optimize'] = True
            save_params['compress_level'] = 9

        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        try:
            processed_img.save(output_path, format=save_format, **save_params)
            print(f"[{os.path.basename(sys.argv[0])}] Gambar hasil disimpan: {output_path} (Format: {output_format})")
            print(f"SUCCESS:{output_path}")
        except Exception as save_e:
            print(f"ERROR: Gagal menyimpan gambar sebagai {output_format} (Pillow format: {save_format}). Error: {save_e}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Terjadi kesalahan umum saat memproses gambar. Detail: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("ERROR: Penggunaan: python image_processor.py <input_path> <output_path> <mode> <output_format>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    processing_mode = sys.argv[3]
    output_format = sys.argv[4]

    process_image(input_file, output_file, processing_mode, output_format)