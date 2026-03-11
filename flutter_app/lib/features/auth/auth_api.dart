import 'package:dio/dio.dart';

import '../../core/models.dart';

class AuthApi {
  AuthApi(this._dio);
  final Dio _dio;

  Future<LoginResponse> login({
    required String email,
    required String password,
  }) async {
    final res = await _dio.post(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    return LoginResponse.fromJson(res.data as Map<String, dynamic>);
  }
}

