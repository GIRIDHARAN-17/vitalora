# Vitalora Mobile App (Primary)

Professional Flutter application for ICU patient monitoring on iOS and Android. Real-time vital signs display, alert notifications, and doctor/admin dashboard on mobile devices.

## 📋 Overview

Vitalora Mobile provides:
- **Patient Dashboard** - Real-time vital signs for assigned patients
- **Alert Management** - Push notifications and alert acknowledgment  
- **User Authentication** - Secure JWT-based login
- **Admin Features** - Manage doctors, patients, and thresholds
- **Dark Theme** - Professional dark UI with glass morphism design
- **Offline Support** - Local caching of critical data

## 🛠️ Tech Stack

- **Framework**: Flutter 3.4+
- **Language**: Dart
- **State Management**: Riverpod 2.6.1
- **Networking**: Dio 5.7.0
- **Navigation**: GoRouter 14.6.2
- **Storage**: flutter_secure_storage 9.2.2
- **UI**: Material Design + Cupertino widgets
- **Charts**: fl_chart 0.69.0
- **Fonts**: Google Fonts

## 🚀 Prerequisites

- **Flutter 3.4+** installed and in PATH
- **Dart 3.2+**
- **Xcode 14+** (for iOS development)
- **Android Studio** or **Android SDK** (for Android)
- **Backend** running at http://localhost:8000 (or configured IP)

Check installation:
```powershell
flutter --version
dart --version
flutter doctor  # Should show no issues
```

## ⚡ Quick Start

### 1. Get Dependencies
```powershell
cd vitalora_app
flutter pub get
```

### 2. Configure Backend URL
Edit `lib/core/config.dart` and set the API base URL:

**Android Emulator:**
```dart
const String apiBaseUrl = 'http://10.0.2.2:8000';
```

**iOS Simulator:**
```dart
const String apiBaseUrl = 'http://127.0.0.1:8000';
```

**Physical Device (same Wi-Fi):**
```dart
const String apiBaseUrl = 'http://192.168.1.100:8000'; // Replace with your PC's LAN IP
```

Find LAN IP:
```powershell
# Windows
ipconfig  # Look for IPv4 Address (192.168.x.x)

# Mac/Linux
ifconfig  # Look for inet
```

### 3. Run on Device/Emulator

**List available devices:**
```powershell
flutter devices
```

**Run app:**
```powershell
# Default device
flutter run

# Specific device
flutter run -d emulator-5554

# Release mode (faster)
flutter run --release
```

**Enable hot reload** during development:
- Press `R` in terminal for hot reload
- Press `F` for full restart
- Press `Q` to quit

## 📁 Project Structure

```
lib/
├── main.dart              # Entry point
├── app.dart               # App configuration
├── core/
│   ├── config.dart       # API URL, constants
│   ├── constants.dart    # App-wide constants
│   ├── theme.dart        # Dark theme
│   └── exceptions.dart   # Custom exceptions
├── data/
│   ├── models/           # Data models (User, Patient, Vital, Alert)
│   ├── repositories/     # API communication layer
│   └── providers/        # Riverpod state providers
├── features/
│   ├── auth/
│   │   ├── screens/      # Login, register screens
│   │   ├── providers/    # Auth state (Riverpod)
│   │   └── widgets/
│   ├── dashboard/
│   │   ├── screens/      # Patient list, overview
│   │   ├── providers/    # Dashboard state
│   │   └── widgets/      # Reusable components
│   ├── patient/
│   │   ├── screens/      # Patient details, vitals
│   │   ├── providers/    # Patient data state
│   │   └── widgets/      # Vital charts, history
│   └── alerts/
│       ├── screens/      # Alert list, details
│       ├── providers/    # Alert state
│       └── widgets/
├── shared/
│   ├── widgets/          # App-wide widgets (AppBar, AppDrawer)
│   ├── dialogs/          # Reusable dialogs
│   └── extensions/       # Extension methods
└── test/                 # Widget and unit tests
```

## 🔐 Authentication

### Login Flow
1. User enters email/password on login screen
2. App sends `POST /auth/login` to backend
3. Backend returns JWT token + user role
4. Token stored securely in `flutter_secure_storage`
5. Token added to all API requests: `Authorization: Bearer {token}`

### Token Management
```dart
// Stored securely
await storage.write(key: 'access_token', value: token);

// Used in Dio interceptor
dio.options.headers['Authorization'] = 'Bearer $token';

// Auto-refresh on 401
// Manual re-login on 403 (access denied)
```

### User Roles
- **Admin**: Manage doctors, patients, system settings
- **Doctor**: Monitor assigned patients, view alerts

## 📱 UI/UX Features

### Theme
- **Dark mode** with glass morphism effects
- **Color palette**: Navy blues, accent greens, warning reds
- **Typography**: Google Fonts (Outfit, Inter)
- **Responsive**: Adapts to phone/tablet sizes

### Key Screens
1. **Login** - Secure authentication
2. **Dashboard** - Patient grid with vital summary
3. **Patient Details** - Full vital history with charts
4. **Alerts** - Real-time notifications
5. **Admin Panel** - User and patient management (if admin)

### Navigation
Uses **GoRouter** for type-safe, deep-link-enabled navigation:
```dart
// Navigate to patient details
context.push('/patient/${patient.id}');

// Go back
context.pop();
```

## 📊 Charts & Visualization

**fl_chart** provides:
- Line charts for vital trends
- Real-time value updates
- Responsive scaling
- Touch interactions

```dart
// Example: Heart rate over time
LineChart(
  LineChartData(
    lineBarsData: [
      LineChartBarData(
        spots: vitalHistory.map((v) => FlSpot(v.time, v.heartRate)).toList(),
      ),
    ],
  ),
);
```

## 🔄 State Management with Riverpod

### Providers (Riverpod)
```dart
// Simple provider
final appConfigProvider = Provider((ref) => AppConfig());

// Async provider (fetches data)
final patientProvider = FutureProvider((ref) async {
  return await repository.getPatient(id);
});

// State notifier (mutable state)
final authProvider = StateNotifierProvider((ref) {
  return AuthNotifier();
});
```

### Usage in Widgets
```dart
@override
Widget build(BuildContext context, WidgetRef ref) {
  final patients = ref.watch(patientsProvider);
  
  return patients.when(
    data: (data) => PatientList(data),
    loading: () => LoadingWidget(),
    error: (err, stack) => ErrorWidget(err),
  );
}
```

## 🌐 API Integration

### Base Client (Dio)
```dart
// lib/data/repositories/
final dio = Dio(BaseOptions(
  baseUrl: AppConfig.apiBaseUrl,
  connectTimeout: Duration(seconds: 30),
));

// Add token to all requests
dio.interceptors.add(
  InterceptorsWrapper(
    onRequest: (options, handler) {
      final token = getToken();
      options.headers['Authorization'] = 'Bearer $token';
      return handler.next(options);
    },
  ),
);
```

### API Calls
```dart
// Login
Future<String> login(String email, String password) async {
  final response = await dio.post('/auth/login', data: {
    'email': email,
    'password': password,
  });
  return response.data['access_token'];
}

// Get patients
Future<List<Patient>> getPatients() async {
  final response = await dio.get('/doctor/patients');
  return List<Patient>.from(response.data.map((x) => Patient.fromJson(x)));
}
```

## 🔔 Push Notifications (Optional)

### Setup Firebase Cloud Messaging
1. Create Firebase project at https://console.firebase.google.com
2. Add Android and iOS apps
3. Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
4. Place in respective project folders

### Integration
```dart
// lib/services/notifications.dart
final messaging = FirebaseMessaging.instance;
await messaging.requestPermission();

// Listen to messages
FirebaseMessaging.onMessage.listen((message) {
  showAlert(message.notification?.title ?? 'Alert');
});
```

## 🧪 Testing

### Run Unit Tests
```powershell
flutter test
```

### Widget Tests
```powershell
flutter test test/widget_test.dart
```

### Integration Tests
```powershell
flutter drive --target=test_driver/app.dart
```

### Manual QA Checklist
- [ ] Login with valid credentials
- [ ] Dashboard loads patient list
- [ ] Click patient shows vitals chart
- [ ] Acknowledge alert updates status
- [ ] Logout clears token
- [ ] Re-login works after logout
- [ ] Error handling on network failure
- [ ] UI responsive on different screen sizes

## 🐛 Troubleshooting

### "Flutter: No devices found"
```powershell
# Start Android emulator
emulator -list-avds
emulator -avd emulator-name &

# Or connect physical device via USB with Developer Mode enabled
```

### "Connection refused" / API not responding
1. Verify backend is running: `http://10.0.2.2:8000/docs`
2. Check API_BASE_URL in `lib/core/config.dart`
3. Test with Postman/cURL first
4. Check firewall rules
5. For physical device: Use correct LAN IP, not localhost

### "Unable to boot simulator"
```powershell
# iOS
open -a Simulator
xcrun simctl erase all

# Android
emulator -avd emulator-name -wipe-data
```

### "Build failed: Gradle issue"
```powershell
flutter clean
cd android
./gradlew clean
cd ..
flutter pub get
flutter run
```

### "Keystore error" during release build
```powershell
# Android - create keystore for signing
keytool -genkey -v -keystore ~/key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias key
```

### Development Certificate Error (iOS)
```powershell
open ios/Runner.xcworkspace
# In Xcode: Signing & Capabilities → Update Team ID
```

## 📦 Building for Release

### Android Release Build
```powershell
flutter build apk --release
# Output: build/app/outputs/flutter-app-release.apk

# Or for Play Store (recommended)
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS Release Build
```powershell
flutter build ios --release
# Then in Xcode:
open ios/Runner.xcworkspace
# Archive and export for TestFlight or App Store
```

## 🚀 Deployment

### Google Play Store
1. Build appbundle: `flutter build appbundle --release`
2. Upload to Google Play Console
3. Set up store listing, screenshots, description

### Apple App Store
1. Build for iOS: `flutter build ios --release`
2. Archive in Xcode: Product → Archive
3. Upload via Transporter or App Store Connect

## 📚 Resources

- [Flutter Official Docs](https://flutter.dev/)
- [Riverpod Guide](https://riverpod.dev/)
- [GoRouter Documentation](https://pub.dev/packages/go_router)
- [Firebase Integration](https://firebase.google.com/docs/flutter/setup)
- [Dart Style Guide](https://dart.dev/guides/language/effective-dart)

## 📋 Features

- ✅ User authentication (JWT)
- ✅ Real-time patient dashboard
- ✅ Vital signs charts and history
- ✅ Alert notifications
- ✅ Responsive UI (phone/tablet)
- ✅ Dark theme support
- ✅ Token refresh
- ✅ Error handling
- 🔄 Push notifications (optional)
- 🔄 Offline data caching (planned)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Write clean, documented code
3. Follow Dart style guide: `dart format .`
4. Run tests: `flutter test`
5. Push and create Pull Request

### Code Style
```powershell
# Format code
dart format .

# Analyze for issues
dart analyze
flutter analyze
```

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: March 2026 | **Version**: 1.0.0 | **Status**: Production Ready
