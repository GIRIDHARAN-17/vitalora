import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';

class RoleSelectScreen extends StatelessWidget {
  const RoleSelectScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          const _BackgroundGlow(),
          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: GlassCard(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Select Access Role',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.w800,
                              ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Please choose your role to continue.',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: VitaloraTheme.muted,
                              ),
                        ),
                        const SizedBox(height: 18),
                        Row(
                          children: [
                            Expanded(
                              child: _RoleTile(
                                title: 'Doctor',
                                icon: Icons.medical_services_outlined,
                                onTap: () => context.go('/login/doctor'),
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: _RoleTile(
                                title: 'Admin',
                                icon: Icons.admin_panel_settings_outlined,
                                onTap: () => context.go('/login/admin'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _RoleTile extends StatelessWidget {
  const _RoleTile({required this.title, required this.icon, required this.onTap});
  final String title;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: const Color(0x10FFFFFF),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: VitaloraTheme.border),
        ),
        child: Column(
          children: [
            Icon(icon, color: VitaloraTheme.cyan, size: 34),
            const SizedBox(height: 10),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BackgroundGlow extends StatelessWidget {
  const _BackgroundGlow();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: RadialGradient(
          center: Alignment(-0.2, -0.2),
          radius: 1.2,
          colors: [
            Color(0x330D0BFF),
            Color(0x00070A12),
          ],
        ),
      ),
      child: Align(
        alignment: const Alignment(0.7, -0.2),
        child: Container(
          width: 280,
          height: 280,
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [Color(0x2200E5FF), Color(0x0000E5FF)],
            ),
          ),
        ),
      ),
    );
  }
}

