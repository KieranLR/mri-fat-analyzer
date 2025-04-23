import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons


def load_images(mri_path, mask_path):
    mri_image = cv2.imread(mri_path, cv2.IMREAD_GRAYSCALE)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    if mri_image is None or mask is None:
        raise FileNotFoundError("MRI or mask image not found.")

    if mri_image.shape != mask.shape:
        raise ValueError("MRI and mask images must have the same dimensions.")

    return mri_image, mask


def apply_fat_highlight(mri_gray, mri_rgb, mask, threshold, mode):
    if mode == "below":
        fat_mask = (mri_gray < threshold) & (mask == 255)
    else:
        fat_mask = (mri_gray > threshold) & (mask == 255)

    highlighted = mri_rgb.copy()
    highlighted[fat_mask] = [255, 0, 0]  # red
    return highlighted, fat_mask


def calculate_fat_percentage(roi_pixels, threshold, mode):
    if mode == "below":
        fat_pixels = roi_pixels[roi_pixels < threshold]
    else:
        fat_pixels = roi_pixels[roi_pixels > threshold]

    if len(roi_pixels) == 0:
        return 0.0
    return (len(fat_pixels) / len(roi_pixels)) * 100


def build_gui(mri_image, mask):
    mri_rgb = cv2.cvtColor(mri_image, cv2.COLOR_GRAY2RGB)
    roi_pixels = mri_image[mask == 255]

    fig, ax = plt.subplots(figsize=(8, 6))
    plt.subplots_adjust(top=0.85, bottom=0.42)

    image_display = ax.imshow(mri_rgb)
    ax.set_title("MRI Fat Analysis – L3-L4 Region", fontsize=14, pad=20, loc='left')
    subtitle = fig.suptitle("Red pixels represent potential fat infiltration based on threshold.", fontsize=10, y=0.375)

    # Add legend as red box
    ax.annotate("Fat pixels", xy=(0.02, 0.96), xycoords='axes fraction',
                bbox=dict(boxstyle="round", fc="white", ec="gray"),
                color='red', fontsize=9)

    title = ax.text(0.5, -0.085, "", fontsize=10, ha='center', transform=ax.transAxes)

    # Slider
    ax_slider = plt.axes([0.2, 0.25, 0.6, 0.03])
    slider = Slider(ax_slider, 'Grayscale Threshold (Fat cutoff)', 0, 255, valinit=80, valstep=1)

    # Threshold color patch
    ax_color = plt.axes([0.82, 0.25, 0.05, 0.03])
    color_patch = np.ones((1, 1, 3), dtype=np.uint8) * 180
    color_display = ax_color.imshow(color_patch, extent=[0, 1, 0, 1])
    ax_color.axis('off')
    ax_color.set_title("Threshold Color", fontsize=8)

    # Radio toggle (mode)
    ax_radio = plt.axes([0.4, 0.12, 0.2, 0.08])
    radio = RadioButtons(ax_radio, ('Above', 'Below'), active=0)
    ax_radio.set_title("Fat if pixel is...", fontsize=9)

    def update(val=None):
        threshold = int(slider.val)
        mode = radio.value_selected.lower()

        # Update threshold color patch
        color_display.set_data(np.ones((1, 1, 3), dtype=np.uint8) * threshold)

        # Highlight fat and calculate %
        highlighted_img, fat_mask = apply_fat_highlight(mri_image, mri_rgb, mask, threshold, mode)
        fat_percent = calculate_fat_percentage(roi_pixels, threshold, mode)

        # Update image and annotation
        image_display.set_data(highlighted_img)
        title.set_text(f" Mode: {mode.capitalize()} | Threshold: {threshold} → Fat %: {fat_percent:.2f}%")
        fig.canvas.draw_idle()

    slider.on_changed(update)
    radio.on_clicked(update)
    update()

    ax.axis('off')
    plt.show()



def main():
    mri_path = "images/mri_image.png"
    mask_path = "images/mask.png"

    mri_image, mask = load_images(mri_path, mask_path)
    build_gui(mri_image, mask)


if __name__ == "__main__":
    main()
