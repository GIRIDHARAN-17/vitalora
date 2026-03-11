import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/role_select_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/admin/admin_home.dart';
import '../features/doctor/doctor_home.dart';

final router = GoRouter(
  initialLocation: '/role',
  routes: [
    GoRoute(
      path: '/role',
      builder: (_, __) => const RoleSelectScreen(),
    ),
    GoRoute(
      path: '/login/:role',
      builder: (context, state) {
        final role = state.pathParameters['role'] ?? 'doctor';
        return LoginScreen(role: role);
      },
    ),
    GoRoute(
      path: '/admin',
      builder: (_, __) => const AdminHome(),
    ),
    GoRoute(
      path: '/doctor',
      builder: (_, __) => const DoctorHome(),
    ),
  ],
  errorBuilder: (context, state) => Scaffold(
    body: Center(
      child: Text('Route error: ${state.error}'),
    ),
  ),
);

