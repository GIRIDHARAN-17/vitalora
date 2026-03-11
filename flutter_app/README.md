# Flutter App (Template Reference)

A Flutter template application for Vitalora ICU monitoring. This folder contains the base Dart code and pubspec configuration that serves as a reference for setting up Flutter projects with FastAPI backend integration.

## ⚠️ About This Folder

This is a **template/reference implementation**. The actual working Flutter project is in `vitalora_app/`. Use this folder to:

- Reference the project structure
- Copy code patterns
- Check pubspec dependencies
- Understand UI/UX implementation

**For development use:** See [vitalora_app/README.md](../vitalora_app/README.md)

## 📋 What's Included

```
flutter_app/
├── pubspec.yaml           # Dependencies & metadata
├── lib/
│   ├── main.dart         # App entry point
│   ├── app.dart          # App configuration
│   ├── core/             # Configuration, constants
│   │   ├── config.dart   # API URLs, settings
│   │   └── constants.dart
│   └── features/         # Feature modules
│       ├── auth/         # Login, registration
│       ├── dashboard/    # Patient overview
│       ├── patient/      # Patient details
│       └── alerts/       # Alert notifications
├── android/              # Android configuration
├── ios/                  # iOS configuration
└── test/                 # Unit tests
```

## 🛠️ Dependencies

```yaml
flutter:
  sdk: flutter
dio: ^5.7.0 # HTTP client
flutter_riverpod: ^2.6.1 # State management
go_router: ^14.6.2 # Navigation
flutter_secure_storage: ^9.2.2 # Secure token storage
google_fonts: ^6.2.1 # Typography
cupertino_icons: ^1.0.8 # iOS icons
```

## 🚀 Setup Instructions

### 1. Create New Project

```powershell
# From repo root - create fresh Flutter project
flutter create vitalora_app
```

### 2. Copy Template Files

```powershell
# Copy pubspec.yaml
Copy-Item flutter_app/pubspec.yaml -Destination vitalora_app/pubspec.yaml

# Copy lib folder
Remove-Item vitalora_app/lib -Recurse -Force
Copy-Item flutter_app/lib -Destination vitalora_app/lib -Recurse
```

### 3. Install Dependencies

```powershell
cd vitalora_app
flutter pub get
```

### 4. Configure Backend URL

Edit `lib/core/config.dart`:

```dart
class AppConfig {
  static const String apiBaseUrl = 'http://10.0.2.2:8000'; // Android
  // static const String apiBaseUrl = 'http://127.0.0.1:8000'; // iOS
  // static const String apiBaseUrl = 'http://<LAN_IP>:8000'; // Physical device
}
```

### 5. Run App

```powershell
flutter run
```

## 🖥️ Backend Integration

### API Endpoints Used

**Authentication**

- `POST /auth/login` - User login
- `POST /auth/register` - User registration

**Admin Features**

- `POST /admin/add_doctor` - Add doctor
- `POST /admin/add_patient` - Add patient
- `GET /admin/doctors` - List doctors
- `GET /admin/patients` - List patients

**Doctor Features**

- `GET /doctor/patients` - Get assigned patients
- `GET /doctor/patients/{id}` - Get patient details
- `GET /doctor/patients/{id}/vitals` - Get patient vitals
- `GET /doctor/alerts` - Get active alerts
- `POST /doctor/alerts/{id}/acknowledge` - Acknowledge alert

### Token Storage

Tokens are stored securely using `flutter_secure_storage`:

```dart
final storage = const FlutterSecureStorage();
await storage.write(key: 'access_token', value: token);
```

## 🎨 UI/UX Features

- **Dark Theme**: Glass morphism design
- **Responsive Layout**: Works on phones, tablets
- **Icons**: Cupertino icons for iOS, Material for Android
- **Fonts**: Google Fonts (Outfit, Inter)
- **Navigation**: GoRouter for type-safe routing

## 🔐 Security

- JWT tokens stored in secure storage (not SharedPreferences)
- HTTPS enforced in production
- No sensitive data in logs
- Token auto-refresh on 401 response

## 📱 Platform-Specific Setup

### Android

```powershell
cd vitalora_app/android
# Edit build.gradle for minSdk, targetSdk if needed
```

Edit `android/app/build.gradle`:

```gradle
android {
    compileSdkVersion 35
    minSdkVersion 21
    targetSdkVersion 35
}
```

### iOS

```powershell
cd vitalora_app/ios
pod install
```

Edit `ios/Podfile` if needed (min deployment target, etc.)

## 🧪 Testing

### Unit Tests

```powershell
flutter test
```

### Widget Tests

```powershell
cd vitalora_app
flutter test test/widget_test.dart
```

### Integration Tests

```powershell
flutter drive --target=test_driver/app.dart
```

### Manual Testing

1. Run app: `flutter run`
2. Use DevTools: `flutter pub global activate devtools && devtools`
3. Debug with Android Studio or VS Code debugger

## 🐛 Troubleshooting

### Build Issues

```powershell
# Clean build
flutter clean
flutter pub get
flutter run
```

### API Connection Failed

- Verify backend is running: `http://10.0.2.2:8000/docs` (Android emulator)
- Check firewall
- For physical device, use LAN IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
- Test with Postman first

### Token Expiration

- Manual re-login prompts
- Auto-refresh on 401 (if implemented)
- Clear secure storage: `flutter clean` + reinstall app

### iOS Pod Issues

```powershell
cd ios
rm -rf Pods
pod install
```

## 📚 Resources

- [Flutter Official Docs](https://flutter.dev/docs)
- [Dart Language Guide](https://dart.dev/guides)
- [Riverpod Documentation](https://riverpod.dev)
- [GoRouter Guide](https://pub.dev/packages/go_router)
- [Flutter Secure Storage](https://pub.dev/packages/flutter_secure_storage)

## 🚀 Deployment

### Release Build - Android

```powershell
flutter build apk --release
# Or for Play Store:
flutter build appbundle --release
```

Built APK: `build/app/outputs/flutter-app-release.apk`

### Release Build - iOS

```powershell
flutter build ios --release
# Create in Xcode
open ios/Runner.xcworkspace
```

## 📋 Features Status

- ✅ Flutter template structure
- ✅ FastAPI integration
- ✅ JWT authentication
- ✅ Patient dashboard
- ✅ Alert notification
- 🔄 Push notifications (WIP)
- 🔄 Offline data sync (Planned)

## 🤝 Contributing

- Follow Dart/Flutter style guide
- Use meaningful variable/function names
- Add tests for critical features
- Keep dependencies updated

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: March 2026 | **Version**: 1.0.0 | **Status**: Template Reference

- `GET /doctor/patients`
- `GET /doctor/patient/{patient_id}/vitals`
- Analysis:
  - `POST /patient/analyze`
