import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

const _kTokenKey = 'jwt_token';
const _kRoleKey = 'role';

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

class SessionState {
  const SessionState({this.token, this.role});
  final String? token;
  final String? role;

  bool get isAuthed => token != null && token!.isNotEmpty;
}

class SessionController extends StateNotifier<SessionState> {
  SessionController(this._storage) : super(const SessionState());

  final FlutterSecureStorage _storage;

  Future<void> load() async {
    final token = await _storage.read(key: _kTokenKey);
    final role = await _storage.read(key: _kRoleKey);
    state = SessionState(token: token, role: role);
  }

  Future<void> setSession({required String token, required String role}) async {
    await _storage.write(key: _kTokenKey, value: token);
    await _storage.write(key: _kRoleKey, value: role);
    state = SessionState(token: token, role: role);
  }

  Future<void> clear() async {
    await _storage.delete(key: _kTokenKey);
    await _storage.delete(key: _kRoleKey);
    state = const SessionState();
  }
}

final sessionProvider = StateNotifierProvider<SessionController, SessionState>((ref) {
  final storage = ref.watch(secureStorageProvider);
  final controller = SessionController(storage);
  controller.load();
  return controller;
});

