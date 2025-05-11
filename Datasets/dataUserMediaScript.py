import os
import shutil
import random

# ─── Configuration ────────────────────────────────────────────────────────
IMAGES_DIR = r"C:\Users\zxq1lah\Downloads\user_media\data images"    # 🖼️ Images folder
RESUMES_DIR = r"C:\Users\zxq1lah\Downloads\user_media\data resumes"  # 📄 Resumes folder
OUTPUT_DIR = r"C:\Users\zxq1lah\Downloads\user_media\organize_media"
NUM_USERS = 130
# ───────────────────────────────────────────────────────────────────────────

def create_user_folders():
    try:
        # Validate source directories
        if not os.path.exists(IMAGES_DIR):
            raise FileNotFoundError(f"🚨 Critical Error: Image folder not found at {IMAGES_DIR}")
        if not os.path.exists(RESUMES_DIR):
            raise FileNotFoundError(f"🚨 Critical Error: Resume folder not found at {RESUMES_DIR}")

        # Collect files with progress
        print("🔍 Scanning source directories...")
        images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        resumes = [f for f in os.listdir(RESUMES_DIR) if f.lower().endswith('.pdf')]

        if not images:
            raise ValueError("❌ No images found in images directory (.jpg/.jpeg/.png required)")
        if not resumes:
            raise ValueError("❌ No PDF files found in resumes directory")

        # Shuffle files randomly
        random.shuffle(images)
        random.shuffle(resumes)

        # Calculate maximum possible folders
        max_folders = min(NUM_USERS, len(images), len(resumes))
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        print(f"\n🚀 Starting creation of {max_folders} user folders...")
        print(f"📦 Found {len(images)} images and {len(resumes)} resumes")

        # Create user folders
        for i in range(max_folders):
            user_id = f"U{i+1:06d}"
            user_folder = os.path.join(OUTPUT_DIR, user_id)
            
            # Create folder
            os.makedirs(user_folder, exist_ok=True)
            
            # Process image
            img_src = os.path.join(IMAGES_DIR, images[i])
            img_dst = os.path.join(user_folder, "profile.jpg")
            shutil.copy(img_src, img_dst)
            
            # Process resume
            resume_src = os.path.join(RESUMES_DIR, resumes[i])
            resume_dst = os.path.join(user_folder, "resume.pdf")
            shutil.copy(resume_src, resume_dst)
            
            # Print progress
            if (i+1) % 10 == 0:
                print(f"✅ Created {i+1} folders...")

        # Final report
        print(f"\n🎉 Successfully created {max_folders} user folders!")
        print(f"📂 Output location: {OUTPUT_DIR}")
        print(f"🖼️ Images used: {max_folders}/{len(images)}")
        print(f"📑 Resumes used: {max_folders}/{len(resumes)}")

    except Exception as e:
        print(f"\n🔥 Error: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Verify the source folders exist at these paths:")
        print(f"   - Images: {IMAGES_DIR}")
        print(f"   - Resumes: {RESUMES_DIR}")
        print("2. Check files have correct extensions (.jpg/.pdf)")
        print("3. Ensure you have read/write permissions")

if __name__ == '__main__':
    print("🏁 Starting folder organization...")
    create_user_folders()
    print("\n✨ Process completed!")