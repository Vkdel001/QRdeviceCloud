import os
import glob
from image_uploader import ESP32ImageUploader

def batch_upload_images(folder_path: str, file_extension: str = "*.jpg"):
    """Upload all images from a folder to ESP32"""
    
    uploader = ESP32ImageUploader()
    
    if not uploader.connect():
        print("Failed to connect to ESP32. Please check connection.")
        return
    
    try:
        # Get all image files
        pattern = os.path.join(folder_path, file_extension)
        image_files = glob.glob(pattern)
        
        # Also check for other common formats
        for ext in ["*.jpeg", "*.png", "*.bmp"]:
            if ext != file_extension:
                pattern = os.path.join(folder_path, ext)
                image_files.extend(glob.glob(pattern))
        
        if not image_files:
            print(f"No image files found in {folder_path}")
            return
        
        print(f"Found {len(image_files)} image files")
        
        # Check free memory
        free_memory = uploader.get_free_memory()
        if free_memory:
            print(f"ESP32 free memory: {free_memory} KB")
        
        successful_uploads = 0
        failed_uploads = 0
        
        for i, image_path in enumerate(image_files, 1):
            if i > 99:  # ESP32 supports files 1-99
                print(f"Skipping {image_path} - file number limit reached (99)")
                break
                
            filename = os.path.basename(image_path)
            print(f"\nUploading {i}/99: {filename}")
            
            if uploader.upload_image(image_path, i, chunk_size=1024):
                print(f"✓ Successfully uploaded as {i}.jpeg")
                successful_uploads += 1
            else:
                print(f"✗ Failed to upload {filename}")
                failed_uploads += 1
                
                # Ask user if they want to continue on failure
                if failed_uploads > 0 and i < len(image_files):
                    continue_upload = input("Continue with next image? (y/n): ").lower()
                    if continue_upload != 'y':
                        break
        
        print(f"\n" + "="*50)
        print("BATCH UPLOAD SUMMARY")
        print("="*50)
        print(f"Total files processed: {successful_uploads + failed_uploads}")
        print(f"Successful uploads: {successful_uploads}")
        print(f"Failed uploads: {failed_uploads}")
        
    except Exception as e:
        print(f"Error during batch upload: {e}")
    finally:
        uploader.disconnect()


def main():
    print("ESP32 Batch Image Uploader")
    print("="*50)
    
    folder_path = input("Enter folder path containing images: ").strip()
    
    if not os.path.exists(folder_path):
        print("Folder does not exist!")
        return
    
    print(f"Uploading images from: {folder_path}")
    print("Supported formats: JPG, JPEG, PNG, BMP")
    print("Image requirements:")
    print("- Max size: 320x480 pixels")
    print("- Max file size: 80KB")
    print("- Will be saved as 1.jpeg, 2.jpeg, etc.")
    
    confirm = input("\nProceed with batch upload? (y/n): ").lower()
    if confirm == 'y':
        batch_upload_images(folder_path)
    else:
        print("Upload cancelled")


if __name__ == "__main__":
    main()