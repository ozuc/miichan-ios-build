#!/usr/bin/env python3
import os
import sys
import json
import shutil
import zipfile
from PIL import Image

BINARY_NAME = "MiiChan"
PKG_NAME = "MiiChan"
DISPLAY_NAME = "ふれあいミイちゃん"
BUNDLE_ID = "com.ryuugames.miichan"
SHORT_VERSION = "1.0.5"
VERSION = "1.0.5"
MIN_IOS_VERSION = "14.0"
TEAM_ID = "0000000000"

CPP_PLUGIN_CODE = """
// Godot Plugins
void godot_apple_embedded_plugins_initialize();
void godot_apple_embedded_plugins_deinitialize();
// Exported Plugins

// Use Plugins
void godot_apple_embedded_plugins_initialize() {
}

void godot_apple_embedded_plugins_deinitialize() {
}
"""

PRIV_TRACKING = """\t<key>NSPrivacyTracking</key>
\t<false/>"""

PRIV_API_TYPES = """\t<array>
\t\t<dict>
\t\t\t<key>NSPrivacyAccessedAPITypeReasons</key>
\t\t\t<array>
\t\t\t\t<string>C617.1</string>
\t\t\t</array>
\t\t\t<key>NSPrivacyAccessedAPIType</key>
\t\t\t<string>NSPrivacyAccessedAPICategoryFileTimestamp</string>
\t\t</dict>
\t\t<dict>
\t\t\t<key>NSPrivacyAccessedAPITypeReasons</key>
\t\t\t<array>
\t\t\t\t<string>E174.1</string>
\t\t\t</array>
\t\t\t<key>NSPrivacyAccessedAPIType</key>
\t\t\t<string>NSPrivacyAccessedAPICategoryDiskSpace</string>
\t\t</dict>
\t\t<dict>
\t\t\t<key>NSPrivacyAccessedAPITypeReasons</key>
\t\t\t<array>
\t\t\t\t<string>35F9.1</string>
\t\t\t</array>
\t\t\t<key>NSPrivacyAccessedAPIType</key>
\t\t\t<string>NSPrivacyAccessedAPICategorySystemBootTime</string>
\t\t</dict>
\t</array>"""

ORIENTATIONS = """<string>UIInterfaceOrientationLandscapeLeft</string>
<string>UIInterfaceOrientationLandscapeRight</string>"""

ICON_INFOS = [
    ("universal", "Icon-58", 58, "2x", "29x29", False),
    ("universal", "Icon-87", 87, "3x", "29x29", False),
    ("universal", "Icon-40", 40, "2x", "20x20", False),
    ("universal", "Icon-60", 60, "3x", "20x20", False),
    ("universal", "Icon-76", 76, "2x", "38x38", False),
    ("universal", "Icon-114", 114, "3x", "38x38", False),
    ("universal", "Icon-80", 80, "2x", "40x40", False),
    ("universal", "Icon-120", 120, "3x", "40x40", False),
    ("universal", "Icon-120-1", 120, "2x", "60x60", False),
    ("universal", "Icon-180", 180, "3x", "60x60", False),
    ("universal", "Icon-167", 167, "2x", "83.5x83.5", False),
    ("universal", "Icon-152", 152, "2x", "76x76", False),
    ("universal", "Icon-128", 128, "2x", "64x64", False),
    ("universal", "Icon-192", 192, "3x", "64x64", False),
    ("universal", "Icon-136", 136, "2x", "68x68", False),
    ("universal", "Icon-1024", 1024, "1x", "1024x1024", True),
]

FILES_TO_PARSE = {
    "godot_ios/godot_ios-Info.plist",
    "godot_ios.xcodeproj/project.pbxproj",
    "godot_ios/export_options.plist",
    "godot_ios/dummy.cpp",
    "godot_ios.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
    "godot_ios.xcodeproj/xcshareddata/xcschemes/godot_ios.xcscheme",
    "godot_ios/godot_ios.entitlements",
    "godot_ios/Launch Screen.storyboard",
    "PrivacyInfo.xcprivacy",
    "godot_ios/PrivacyInfo.xcprivacy",
}

def fix_config_file(text: str) -> str:
    out_lines = []
    for line in text.split("\n"):
        if "$binary" in line:
            out_lines.append(line.replace("$binary", BINARY_NAME))
        elif "$modules_buildfile" in line:
            out_lines.append(line.replace("$modules_buildfile", ""))
        elif "$modules_fileref" in line:
            out_lines.append(line.replace("$modules_fileref", ""))
        elif "$modules_buildphase" in line:
            out_lines.append(line.replace("$modules_buildphase", ""))
        elif "$modules_buildgrp" in line:
            out_lines.append(line.replace("$modules_buildgrp", ""))
        elif "$name" in line:
            out_lines.append(line.replace("$name", PKG_NAME))
        elif "$bundle_identifier" in line:
            out_lines.append(line.replace("$bundle_identifier", BUNDLE_ID))
        elif "$short_version" in line:
            out_lines.append(line.replace("$short_version", SHORT_VERSION))
        elif "$version" in line:
            out_lines.append(line.replace("$version", VERSION))
        elif "$min_version" in line:
            out_lines.append(line.replace("$min_version", MIN_IOS_VERSION))
        elif "$signature" in line:
            out_lines.append(line.replace("$signature", ""))
        elif "$team_id" in line:
            out_lines.append(line.replace("$team_id", TEAM_ID))
        elif "$default_build_config" in line:
            out_lines.append(line.replace("$default_build_config", "Release"))
        elif "$export_method" in line:
            out_lines.append(line.replace("$export_method", "ad-hoc"))
        elif "$provisioning_profile_specifier_debug" in line:
            out_lines.append(line.replace("$provisioning_profile_specifier_debug", ""))
        elif "$provisioning_profile_specifier_release" in line:
            out_lines.append(line.replace("$provisioning_profile_specifier_release", ""))
        elif "$provisioning_profile_specifier" in line:
            out_lines.append(line.replace("$provisioning_profile_specifier", ""))
        elif "$provisioning_profile_uuid_release" in line:
            out_lines.append(line.replace("$provisioning_profile_uuid_release", ""))
        elif "$provisioning_profile_uuid_debug" in line:
            out_lines.append(line.replace("$provisioning_profile_uuid_debug", ""))
        elif "$code_sign_style_debug" in line:
            out_lines.append(line.replace("$code_sign_style_debug", "Automatic"))
        elif "$code_sign_style_release" in line:
            out_lines.append(line.replace("$code_sign_style_release", "Automatic"))
        elif "$provisioning_profile_uuid" in line:
            out_lines.append(line.replace("$provisioning_profile_uuid", ""))
        elif "$code_sign_identity_debug" in line:
            out_lines.append(line.replace("$code_sign_identity_debug", "Apple Development"))
        elif "$code_sign_identity_release" in line:
            out_lines.append(line.replace("$code_sign_identity_release", "Apple Distribution"))
        elif "$additional_plist_content" in line:
            extra_plist = f"<key>CFBundleDisplayName</key>\n<string>{DISPLAY_NAME}</string>\n"
            out_lines.append(line.replace("$additional_plist_content", extra_plist))
        elif "$godot_archs" in line:
            out_lines.append(line.replace("$godot_archs", "arm64"))
        elif "$linker_flags" in line:
            out_lines.append(line.replace("$linker_flags", ""))
        elif "$targeted_device_family" in line:
            out_lines.append(line.replace("$targeted_device_family", "1,2"))
        elif "$cpp_code" in line:
            out_lines.append(line.replace("$cpp_code", CPP_PLUGIN_CODE))
        elif "$docs_in_place" in line:
            out_lines.append(line.replace("$docs_in_place", "<true/>"))
        elif "$docs_sharing" in line:
            out_lines.append(line.replace("$docs_sharing", "<true/>"))
        elif "$entitlements_full" in line:
            out_lines.append(line.replace("$entitlements_full", ""))
        elif "$required_device_capabilities" in line:
            out_lines.append(line.replace("$required_device_capabilities", "<string>arm64</string>"))
        elif "$interface_orientations" in line:
            out_lines.append(line.replace("$interface_orientations", ORIENTATIONS))
        elif "$ipad_interface_orientations" in line:
            out_lines.append(line.replace("$ipad_interface_orientations", ORIENTATIONS))
        elif "$camera_usage_description" in line:
            out_lines.append(line.replace("$camera_usage_description", "Camera not used"))
        elif "$microphone_usage_description" in line:
            out_lines.append(line.replace("$microphone_usage_description", "Microphone not used"))
        elif "$photolibrary_usage_description" in line:
            out_lines.append(line.replace("$photolibrary_usage_description", "Photo library not used"))
        elif "$plist_launch_screen_name" in line:
            out_lines.append(line.replace("$plist_launch_screen_name", "<key>UILaunchStoryboardName</key>\n<string>Launch Screen</string>"))
        elif "$pbx_launch_screen_file_reference" in line:
            out_lines.append(line.replace("$pbx_launch_screen_file_reference", '90DD2D9D24B36E8000717FE1 = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = file.storyboard; path = "Launch Screen.storyboard"; sourceTree = "<group>"; };'))
        elif "$pbx_launch_screen_copy_files" in line:
            out_lines.append(line.replace("$pbx_launch_screen_copy_files", "90DD2D9D24B36E8000717FE1 /* Launch Screen.storyboard */,"))
        elif "$pbx_launch_screen_build_phase" in line:
            out_lines.append(line.replace("$pbx_launch_screen_build_phase", "90DD2D9E24B36E8000717FE1 /* Launch Screen.storyboard in Resources */,"))
        elif "$pbx_launch_screen_build_reference" in line:
            out_lines.append(line.replace("$pbx_launch_screen_build_reference", "90DD2D9E24B36E8000717FE1 /* Launch Screen.storyboard in Resources */ = {isa = PBXBuildFile; fileRef = 90DD2D9D24B36E8000717FE1 /* Launch Screen.storyboard */; };"))
        elif "$pbx_launch_image_usage_setting" in line:
            out_lines.append(line.replace("$pbx_launch_image_usage_setting", ""))
        elif "$launch_screen_image_mode" in line:
            out_lines.append(line.replace("$launch_screen_image_mode", "center"))
        elif "$launch_screen_background_color" in line:
            out_lines.append(line.replace("$launch_screen_background_color", 'red="0.14" green="0.14" blue="0.14" alpha="1.0"'))
        elif "$pbx_locale_file_reference" in line:
            out_lines.append(line.replace("$pbx_locale_file_reference", ""))
        elif "$pbx_locale_build_reference" in line:
            out_lines.append(line.replace("$pbx_locale_build_reference", ""))
        elif "$swift_runtime_migration" in line:
            out_lines.append(line.replace("$swift_runtime_migration", ""))
        elif "$swift_runtime_build_settings" in line:
            out_lines.append(line.replace("$swift_runtime_build_settings", ""))
        elif "$swift_runtime_fileref" in line:
            out_lines.append(line.replace("$swift_runtime_fileref", ""))
        elif "$swift_runtime_binary_files" in line:
            out_lines.append(line.replace("$swift_runtime_binary_files", ""))
        elif "$swift_runtime_buildfile" in line:
            out_lines.append(line.replace("$swift_runtime_buildfile", ""))
        elif "$swift_runtime_build_phase" in line:
            out_lines.append(line.replace("$swift_runtime_build_phase", ""))
        elif "$priv_collection" in line:
            pass
        elif "$priv_tracking" in line:
            out_lines.append(PRIV_TRACKING)
        elif "$priv_api_types" in line:
            out_lines.append(PRIV_API_TYPES)
        else:
            out_lines.append(line)

    res = "\n".join(out_lines)
    # _add_assets_to_project replacements
    for ph in [
        "$additional_pbx_files",
        "$additional_pbx_frameworks_build",
        "$additional_pbx_frameworks_refs",
        "$additional_pbx_resources_build",
        "$additional_pbx_resources_refs",
        "$pbx_embeded_frameworks",
    ]:
        res = res.replace(ph, "")
    return res

def export_icons_and_splash(icon_src_path: str, binary_dir: str):
    iconset_dir = os.path.join(binary_dir, "Images.xcassets", "AppIcon.appiconset")
    os.makedirs(iconset_dir, exist_ok=True)

    base_img = Image.open(icon_src_path).convert("RGBA")
    images_json = []
    sizes_lines = []

    for idiom, exp_name, side_size, scale, unscaled_size, force_opaque in ICON_INFOS:
        resized = base_img.resize((side_size, side_size), Image.Resampling.LANCZOS)
        if force_opaque:
            bg = Image.new("RGBA", (side_size, side_size), (36, 36, 36, 255))
            bg.alpha_composite(resized)
            resized = bg.convert("RGB")
        filename = f"{exp_name}.png"
        resized.save(os.path.join(iconset_dir, filename), "PNG")
        sizes_lines.append(str(side_size))
        entry = {
            "idiom": idiom,
            "platform": "ios",
            "size": unscaled_size,
            "filename": filename,
        }
        if scale != "1x":
            entry["scale"] = scale
        images_json.append(entry)

    contents = {
        "images": images_json,
        "info": {"author": "xcode", "version": 1}
    }
    with open(os.path.join(iconset_dir, "Contents.json"), "w", encoding="utf-8") as f:
        json.dump(contents, f, separators=(",", ":"))
    with open(os.path.join(iconset_dir, "sizes"), "w", encoding="utf-8") as f:
        f.write("\n".join(sizes_lines) + "\n")

    # Splash screen images
    splash_dir = os.path.join(binary_dir, "Images.xcassets", "SplashImage.imageset")
    os.makedirs(splash_dir, exist_ok=True)
    splash_img = base_img.resize((256, 256), Image.Resampling.LANCZOS)
    splash_img.save(os.path.join(splash_dir, "splash@2x.png"), "PNG")
    splash_img.save(os.path.join(splash_dir, "splash@3x.png"), "PNG")

def main():
    if len(sys.argv) < 5:
        print("Usage: generate_xcode_project.py <ios.zip> <MiiChan.pck> <app_icon.webp> <dest_dir>")
        sys.exit(1)

    ios_zip_path = sys.argv[1]
    pck_path = sys.argv[2]
    icon_path = sys.argv[3]
    dest_dir = sys.argv[4]

    os.makedirs(dest_dir, exist_ok=True)
    binary_dir = os.path.join(dest_dir, BINARY_NAME)
    os.makedirs(binary_dir, exist_ok=True)

    library_to_use = "libgodot.ios.release.xcframework"
    found_library = False

    with zipfile.ZipFile(ios_zip_path, "r") as zf:
        for info in zf.infolist():
            file = info.filename
            if info.is_dir():
                continue

            data = zf.read(file)
            if file in FILES_TO_PARSE:
                text = data.decode("utf-8")
                text = fix_config_file(text)
                data = text.encode("utf-8")
            elif file.startswith("libgodot.ios"):
                if not file.startswith(library_to_use) or file.endswith("/empty"):
                    continue
                found_library = True
                file = file.replace(library_to_use, f"{BINARY_NAME}.xcframework")

            if len(data) > 0:
                out_rel = file.replace("godot_ios", BINARY_NAME)
                out_full = os.path.join(dest_dir, out_rel)
                os.makedirs(os.path.dirname(out_full), exist_ok=True)
                with open(out_full, "wb") as f:
                    f.write(data)
                if found_library and f"{BINARY_NAME}.xcframework" in out_rel:
                    os.chmod(out_full, 0o755)

    if not found_library:
        raise RuntimeError(f"Library {library_to_use} not found in {ios_zip_path}")

    # Copy .pck to dest_dir/MiiChan.pck
    target_pck = os.path.join(dest_dir, f"{BINARY_NAME}.pck")
    if os.path.abspath(pck_path) != os.path.abspath(target_pck):
        shutil.copyfile(pck_path, target_pck)

    # Export icons and splash
    export_icons_and_splash(icon_path, binary_dir)
    print(f"Successfully generated Xcode project at {dest_dir}")

if __name__ == "__main__":
    main()
