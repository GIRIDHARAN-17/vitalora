import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/theme.dart';
import '../common/app_scaffold.dart';
import 'doctor_api.dart';

class DoctorHome extends ConsumerWidget {
  const DoctorHome({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final api = DoctorApi(ref.watch(dioProvider));
    return AppScaffold(
      title: 'Doctor Dashboard',
      child: FutureBuilder<List<Patient>>(
        future: api.assignedPatients(),
        builder: (context, snap) {
          if (!snap.hasData) return const Center(child: CircularProgressIndicator());
          final patients = snap.data!;
          if (patients.isEmpty) return const Center(child: Text('No assigned patients'));

          return ListView.separated(
            itemCount: patients.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, i) {
              final p = patients[i];
              return InkWell(
                borderRadius: BorderRadius.circular(20),
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => PatientDetailScreen(patient: p)),
                ),
                child: GlassCard(
                  child: Row(
                    children: [
                      const Icon(Icons.bed_outlined, color: VitaloraTheme.cyan),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('${p.name} (${p.patientId})',
                                style: const TextStyle(fontWeight: FontWeight.w900)),
                            const SizedBox(height: 4),
                            Text('Room: ${p.roomNo}', style: TextStyle(color: VitaloraTheme.muted)),
                            Text('Condition: ${p.condition}',
                                style: TextStyle(color: VitaloraTheme.muted)),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: VitaloraTheme.muted),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class PatientDetailScreen extends ConsumerStatefulWidget {
  const PatientDetailScreen({super.key, required this.patient});
  final Patient patient;

  @override
  ConsumerState<PatientDetailScreen> createState() => _PatientDetailScreenState();
}

class _PatientDetailScreenState extends ConsumerState<PatientDetailScreen> {
  String _location = 'Chennai';
  bool _analyzing = false;
  AnalyzeResult? _result;
  String? _error;

  Future<void> _analyze() async {
    setState(() {
      _analyzing = true;
      _error = null;
    });
    try {
      final api = DoctorApi(ref.read(dioProvider));
      final res = await api.analyze(patientId: widget.patient.patientId, location: _location);
      setState(() => _result = res);
    } catch (_) {
      setState(() => _error = 'Analyze failed. Ensure vitals >= 30 for this patient.');
    } finally {
      setState(() => _analyzing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final api = DoctorApi(ref.watch(dioProvider));
    final p = widget.patient;
    return Scaffold(
      appBar: AppBar(title: Text('${p.patientId}')),
      body: Container(
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(-0.8, -0.6),
            radius: 1.5,
            colors: [Color(0x220D0BFF), VitaloraTheme.bg],
          ),
        ),
        child: Column(
          children: [
            GlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(p.name, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18)),
                  const SizedBox(height: 6),
                  Text('Room: ${p.roomNo}', style: TextStyle(color: VitaloraTheme.muted)),
                  Text('Condition: ${p.condition}', style: TextStyle(color: VitaloraTheme.muted)),
                  const SizedBox(height: 10),
                  TextField(
                    decoration: const InputDecoration(labelText: 'Location'),
                    onChanged: (v) => _location = v,
                    controller: TextEditingController(text: _location),
                  ),
                  const SizedBox(height: 12),
                  GradientButton(
                    label: 'Analyze',
                    isLoading: _analyzing,
                    onPressed: _analyze,
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 10),
                    Text(_error!, style: const TextStyle(color: Colors.redAccent)),
                  ],
                  if (_result != null) ...[
                    const SizedBox(height: 12),
                    _ResultCard(result: _result!),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 14),
            Expanded(
              child: FutureBuilder<List<Vital>>(
                future: api.vitals(p.patientId),
                builder: (context, snap) {
                  if (!snap.hasData) return const Center(child: CircularProgressIndicator());
                  final vitals = snap.data!;
                  if (vitals.isEmpty) return const Center(child: Text('No vitals yet'));
                  return ListView.separated(
                    itemCount: vitals.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 10),
                    itemBuilder: (context, i) {
                      final v = vitals[i];
                      return GlassCard(
                        child: Row(
                          children: [
                            const Icon(Icons.monitor_heart_outlined, color: VitaloraTheme.cyan),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    '${v.timestamp.toLocal()}',
                                    style: const TextStyle(fontWeight: FontWeight.w800),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'RR ${v.respirationRate} | SpO2 ${v.spo2} | HR ${v.heartRate} | SBP ${v.systolicBp} | Temp ${v.temperature.toStringAsFixed(1)} | C ${v.consciousness}',
                                    style: TextStyle(color: VitaloraTheme.muted),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.result});
  final AnalyzeResult result;

  Color _levelColor(String level) {
    switch (level) {
      case 'critical':
        return Colors.redAccent;
      case 'high':
        return Colors.orangeAccent;
      case 'medium':
        return Colors.amberAccent;
      default:
        return VitaloraTheme.cyan;
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = _levelColor(result.alertLevel);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: VitaloraTheme.border),
        color: const Color(0x10FFFFFF),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('Alert: ${result.alertLevel.toUpperCase()}',
                  style: TextStyle(fontWeight: FontWeight.w900, color: c)),
            ],
          ),
          const SizedBox(height: 6),
          Text('NEWS score: ${result.newsScore.toStringAsFixed(2)}',
              style: TextStyle(color: VitaloraTheme.muted)),
          Text('Outbreak severity: ${result.outbreakSeverity.toStringAsFixed(2)}',
              style: TextStyle(color: VitaloraTheme.muted)),
          Text('Adjusted score: ${result.adjustedScore.toStringAsFixed(2)}',
              style: TextStyle(color: VitaloraTheme.muted)),
        ],
      ),
    );
  }
}

