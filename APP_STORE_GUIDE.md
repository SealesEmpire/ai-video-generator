# App Store Submission Guide

This guide covers how to build, configure, and submit the AI Video Generator app to the **Apple App Store** and **Google Play Store** using Capacitor.

## Prerequisites

### General
- Node.js 16+ and npm/yarn installed
- The web app builds successfully (`cd frontend && npm run build`)

### For iOS (Apple App Store)
- macOS computer with Xcode 15+ installed
- Apple Developer Program membership ($99/year) — [enroll here](https://developer.apple.com/programs/)
- A valid Apple Distribution certificate and provisioning profile
- CocoaPods installed (`sudo gem install cocoapods`)

### For Android (Google Play Store)
- Android Studio installed with SDK 34+
- Google Play Developer account ($25 one-time fee) — [register here](https://play.google.com/console/)
- A Java/Android keystore for signing the release build

---

## Project Setup

The app uses [Capacitor](https://capacitorjs.com/) to wrap the React web app into native iOS and Android shells.

### Key Files
| File | Purpose |
|------|---------|
| `frontend/capacitor.config.ts` | Capacitor configuration (app ID, name, plugins) |
| `frontend/ios/` | Native iOS Xcode project |
| `frontend/android/` | Native Android Studio project |

### App Identity
- **App ID (Bundle ID):** `com.aivideogenerator.app`
- **App Name:** AI Video Generator

> **Important:** Before submitting, update the `appId` in `capacitor.config.ts` to match your registered bundle identifier on Apple/Google (e.g., `com.yourcompany.aivideogenerator`).

---

## Building for iOS (Apple App Store)

### 1. Build the Web App & Sync
```bash
cd frontend
npm run build
npx cap sync ios
```

### 2. Open in Xcode
```bash
npx cap open ios
```
Or use: `npm run cap:open:ios`

### 3. Configure Signing in Xcode
1. Open the project in Xcode.
2. Select the **App** target.
3. Go to **Signing & Capabilities**.
4. Select your **Team** (Apple Developer account).
5. Set the **Bundle Identifier** to match your registered App ID.
6. Ensure **Automatically manage signing** is checked.

### 4. Set App Version
1. In Xcode, select the **App** target → **General** tab.
2. Set **Version** (e.g., `1.0.0`) and **Build** (e.g., `1`).

### 5. Replace App Icon
1. In Xcode, navigate to **App → Assets.xcassets → AppIcon**.
2. Replace the placeholder icon with your app icon (1024×1024 PNG, no alpha channel).
3. Use a tool like [App Icon Generator](https://appicon.co/) to create all required sizes.

### 6. Build for Distribution
1. Set the build target to **Any iOS Device (arm64)**.
2. Go to **Product → Archive**.
3. Once archived, the **Organizer** window opens.
4. Click **Distribute App** → **App Store Connect**.
5. Follow the prompts to upload.

### 7. Submit via App Store Connect
1. Go to [App Store Connect](https://appstoreconnect.apple.com/).
2. Create a new app with your bundle ID.
3. Fill in the required metadata:
   - App name, subtitle, description
   - Keywords and categories (e.g., Photo & Video)
   - Screenshots for required device sizes (6.7", 6.5", 5.5" iPhones, iPad)
   - Privacy policy URL
   - App rating questionnaire
4. Select your uploaded build.
5. Submit for **App Review**.

### iOS App Store Checklist
- [ ] Bundle ID registered in Apple Developer Portal
- [ ] App icon (1024×1024, no transparency)
- [ ] Screenshots for all required device sizes
- [ ] Privacy policy URL hosted publicly
- [ ] App description and keywords
- [ ] Age rating questionnaire completed
- [ ] In-app purchases configured (if applicable)
- [ ] App Review guidelines compliance verified

---

## Building for Android (Google Play Store)

### 1. Build the Web App & Sync
```bash
cd frontend
npm run build
npx cap sync android
```

### 2. Open in Android Studio
```bash
npx cap open android
```
Or use: `npm run cap:open:android`

### 3. Configure App Identity
1. In `frontend/android/app/build.gradle`, verify:
   - `applicationId` matches your registered package name
   - `versionCode` and `versionName` are set correctly

2. Update `frontend/android/app/src/main/res/values/strings.xml`:
   ```xml
   <string name="app_name">AI Video Generator</string>
   ```

### 4. Replace App Icon
1. In Android Studio, right-click `app/src/main/res` → **New → Image Asset**.
2. Select your app icon source image (512×512 PNG recommended).
3. Configure foreground and background layers for adaptive icons.
4. Click **Finish** to generate all density-specific icons.

### 5. Create a Signing Key
```bash
keytool -genkey -v -keystore ai-video-generator.keystore \
  -alias ai-video-generator -keyalg RSA -keysize 2048 -validity 10000
```

> **Important:** Store this keystore file securely. You need it for every future update.

### 6. Build a Signed Release APK/AAB
1. In Android Studio: **Build → Generate Signed Bundle / APK**.
2. Select **Android App Bundle (AAB)** (required by Google Play).
3. Choose your keystore and enter credentials.
4. Select **release** build variant.
5. Click **Finish** to generate the `.aab` file.

Alternatively, configure signing in `build.gradle` and build from the command line:
```bash
cd frontend/android
./gradlew bundleRelease
```

### 7. Submit via Google Play Console
1. Go to [Google Play Console](https://play.google.com/console/).
2. Create a new app.
3. Fill in the store listing:
   - App name, short and full descriptions
   - Category (e.g., Video Players & Editors)
   - App icon (512×512 PNG), feature graphic (1024×500)
   - Screenshots for phone and tablet (min 2 per device type)
   - Privacy policy URL
4. Complete the content rating questionnaire.
5. Set up pricing & distribution (countries).
6. Upload your signed AAB under **Production → Create new release**.
7. Submit for **Review**.

### Google Play Store Checklist
- [ ] Package name registered in Google Play Console
- [ ] App icon (512×512 PNG) and feature graphic (1024×500)
- [ ] Screenshots for phone and 7" and 10" tablets
- [ ] Privacy policy URL hosted publicly
- [ ] Store listing (name, descriptions, category)
- [ ] Content rating questionnaire completed
- [ ] Signing key created and stored securely
- [ ] Release AAB file built and uploaded
- [ ] Target API level meets Google Play requirements (API 34+)

---

## Updating the App

When you make changes to the web app:

```bash
cd frontend

# 1. Build the updated web app
npm run build

# 2. Sync changes to native platforms
npx cap sync

# 3. Open in IDE and build a new archive/bundle
npx cap open ios      # or npx cap open android
```

Remember to increment the version number in Xcode/Android Studio before each store submission.

---

## Backend Configuration for Native Apps

When running as a native mobile app, the frontend needs to communicate with your hosted backend API. Ensure:

1. **Set the backend URL** in `frontend/.env`:
   ```env
   REACT_APP_BACKEND_URL=https://your-api-domain.com
   ```

2. **CORS is configured** to allow requests from the Capacitor origin:
   ```python
   # In backend/server.py
   allow_origins=[
       "https://your-api-domain.com",
       "capacitor://localhost",  # iOS
       "http://localhost",       # Android
   ]
   ```

3. **HTTPS is required** — both app stores require secure connections.

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `npm run cap:build` | Build web app and sync to native platforms |
| `npm run cap:sync` | Sync web assets to native projects |
| `npm run cap:open:ios` | Open iOS project in Xcode |
| `npm run cap:open:android` | Open Android project in Android Studio |
| `npm run cap:run:ios` | Build and run on iOS simulator/device |
| `npm run cap:run:android` | Build and run on Android emulator/device |

---

## Troubleshooting

### iOS: "No signing identity found"
Ensure you have a valid Apple Developer certificate installed in Keychain Access and selected in Xcode.

### Android: "SDK not found"
Set `ANDROID_HOME` environment variable or create `frontend/android/local.properties`:
```
sdk.dir=/path/to/Android/sdk
```

### White screen on device
- Check browser console for errors: **Safari → Develop → Device** (iOS) or **chrome://inspect** (Android)
- Ensure `REACT_APP_BACKEND_URL` is set to an externally accessible URL (not `localhost`)
- Verify the `build` directory was synced: `npx cap sync`

### Network requests failing
- Ensure the backend CORS config includes `capacitor://localhost` and `http://localhost`
- Verify HTTPS is configured on the backend

---

## Additional Resources

- [Capacitor Documentation](https://capacitorjs.com/docs)
- [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Google Play Developer Policy](https://play.google.com/about/developer-content-policy/)
- [App Store Screenshot Specifications](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications/)
- [Google Play Asset Requirements](https://support.google.com/googleplay/android-developer/answer/9866151)
