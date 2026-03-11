import 'package:flutter/material.dart';

import 'core/router.dart';
import 'core/theme.dart';

class VitaloraApp extends StatelessWidget {
  const VitaloraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Vitalora',
      debugShowCheckedModeBanner: false,
      theme: VitaloraTheme.dark(),
      routerConfig: router,
    );
  }
}

