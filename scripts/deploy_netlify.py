"""
Netlify Deployment Automation Script for Samaroh (समारोह).
Allows programmatic deployment to Netlify via Netlify REST API,
or generates a deploy-ready bundle for Netlify Drop / GitHub Continuous Deployment.
"""
import os
import sys
import zipfile
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import httpx

PUBLIC_DIR = ROOT_DIR / "public"
DIST_DIR = ROOT_DIR / "dist"
ZIP_PATH = DIST_DIR / "samaroh-netlify-deploy.zip"

def create_deploy_bundle() -> Path:
    """Packages public static assets into a zip bundle for Netlify deployment."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Packaging static assets from {PUBLIC_DIR}...")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in PUBLIC_DIR.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(PUBLIC_DIR)
                zf.write(file_path, arcname)
                
    print(f"✅ Created Netlify deploy bundle: {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1024:.1f} KB)")
    return ZIP_PATH

def deploy_via_api(token: str, site_id: str | None = None):
    """Deploys the packaged zip directly to Netlify using the Netlify REST API."""
    print("🚀 Connecting to Netlify API...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip"
    }

    with open(ZIP_PATH, "rb") as f:
        zip_bytes = f.read()

    with httpx.Client(timeout=60.0) as client:
        if site_id:
            url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
            print(f"Deploying update to existing site ID: {site_id}...")
            res = client.post(url, headers=headers, content=zip_bytes)
        else:
            url = "https://api.netlify.com/api/v1/sites"
            print("Creating new site on Netlify...")
            res = client.post(url, headers=headers, content=zip_bytes)

        if res.status_code in (200, 201):
            data = res.json()
            ssl_url = data.get("ssl_url") or data.get("url")
            site_name = data.get("name")
            print("\n" + "=" * 60)
            print("॥ मङ्गलम् ॥ Samaroh successfully deployed to Netlify!")
            print(f"🌐 Live Site URL: {ssl_url}")
            print(f"🆔 Netlify Site ID: {data.get('id')}")
            print(f"📛 Site Name: {site_name}")
            print("=" * 60 + "\n")
            return ssl_url
        else:
            print(f"❌ Netlify deployment failed ({res.status_code}): {res.text}")
            return None

def main():
    bundle_path = create_deploy_bundle()
    token = os.getenv("NETLIFY_AUTH_TOKEN")
    site_id = os.getenv("NETLIFY_SITE_ID")

    if len(sys.argv) > 1 and sys.argv[1].startswith("--token="):
        token = sys.argv[1].split("=", 1)[1]

    if token:
        deploy_via_api(token, site_id)
    else:
        print("\n" + "-" * 65)
        print("ℹ️  HOW TO DEPLOY SAMAROH TO NETLIFY:")
        print("-" * 65)
        print("METHOD 1: Instant GitHub Continuous Deployment (Recommended)")
        print("1. Go to https://app.netlify.com")
        print("2. Click 'Add new site' -> 'Import an existing project'")
        print("3. Select GitHub and choose: ashish-29-2003/Event-Planner")
        print("4. Netlify will detect 'netlify.toml' automatically!")
        print("5. Click 'Deploy Samaroh'. Every future push will auto-deploy!\n")
        print("METHOD 2: Instant 10-Second Drag-and-Drop (Netlify Drop)")
        print("1. Go to https://app.netlify.com/drop")
        print(f"2. Drag and drop the '{PUBLIC_DIR}' folder (or '{bundle_path}')")
        print("3. Your live URL is generated immediately!\n")
        print("METHOD 3: Automated CLI Deployment")
        print("Set NETLIFY_AUTH_TOKEN in your .env or run:")
        print("python scripts/deploy_netlify.py --token=YOUR_NETLIFY_PERSONAL_ACCESS_TOKEN")
        print("-" * 65 + "\n")

if __name__ == "__main__":
    main()
