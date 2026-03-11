import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/theme.dart';
import '../common/app_scaffold.dart';
import 'admin_api.dart';

class AdminHome extends ConsumerStatefulWidget {
  const AdminHome({super.key});

  @override
  ConsumerState<AdminHome> createState() => _AdminHomeState();
}

class _AdminHomeState extends ConsumerState<AdminHome> {
  int _tab = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [
      const _DoctorsTab(),
      const _PatientsTab(),
      const _AddDoctorTab(),
      const _AddPatientTab(),
    ];

    return AppScaffold(
      title: 'Admin Dashboard',
      child: Column(
        children: [
          _TabBar(
            index: _tab,
            onChanged: (i) => setState(() => _tab = i),
            items: const ['Doctors', 'Patients', 'Add Doctor', 'Add Patient'],
          ),
          const SizedBox(height: 14),
          Expanded(child: pages[_tab]),
        ],
      ),
    );
  }
}

class _TabBar extends StatelessWidget {
  const _TabBar({
    required this.index,
    required this.onChanged,
    required this.items,
  });
  final int index;
  final ValueChanged<int> onChanged;
  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: List.generate(items.length, (i) {
          final active = i == index;
          return Padding(
            padding: const EdgeInsets.only(right: 10),
            child: InkWell(
              borderRadius: BorderRadius.circular(999),
              onTap: () => onChanged(i),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: VitaloraTheme.border),
                  color: active ? const Color(0x22FFFFFF) : const Color(0x10FFFFFF),
                ),
                child: Text(
                  items[i],
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: active ? VitaloraTheme.text : VitaloraTheme.muted,
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}

final _adminApiProvider = Provider<AdminApi>((ref) => AdminApi(ref.watch(dioProvider)));

class _DoctorsTab extends ConsumerWidget {
  const _DoctorsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<List<Doctor>>(
      future: ref.read(_adminApiProvider).listDoctors(),
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final doctors = snap.data!;
        if (doctors.isEmpty) {
          return const Center(child: Text('No doctors found'));
        }
        return ListView.separated(
          itemCount: doctors.length,
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (context, i) {
            final d = doctors[i];
            return GlassCard(
              child: Row(
                children: [
                  const Icon(Icons.person_outline, color: VitaloraTheme.cyan),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(d.name, style: const TextStyle(fontWeight: FontWeight.w800)),
                        const SizedBox(height: 2),
                        Text(d.email, style: TextStyle(color: VitaloraTheme.muted)),
                        Text(d.specialization, style: TextStyle(color: VitaloraTheme.muted)),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

class _PatientsTab extends ConsumerWidget {
  const _PatientsTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<List<Patient>>(
      future: ref.read(_adminApiProvider).listPatients(),
      builder: (context, snap) {
        if (!snap.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final patients = snap.data!;
        if (patients.isEmpty) {
          return const Center(child: Text('No patients found'));
        }
        return ListView.separated(
          itemCount: patients.length,
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (context, i) {
            final p = patients[i];
            return GlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${p.name} (${p.patientId})',
                      style: const TextStyle(fontWeight: FontWeight.w800)),
                  const SizedBox(height: 4),
                  Text('Room: ${p.roomNo}', style: TextStyle(color: VitaloraTheme.muted)),
                  Text('Condition: ${p.condition}', style: TextStyle(color: VitaloraTheme.muted)),
                  Text('Doctor: ${p.doctorEmail}', style: TextStyle(color: VitaloraTheme.muted)),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

class _AddDoctorTab extends ConsumerStatefulWidget {
  const _AddDoctorTab();

  @override
  ConsumerState<_AddDoctorTab> createState() => _AddDoctorTabState();
}

class _AddDoctorTabState extends ConsumerState<_AddDoctorTab> {
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _spec = TextEditingController();
  final _phone = TextEditingController();
  bool _loading = false;
  String? _msg;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _password.dispose();
    _spec.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _msg = null;
    });
    try {
      await ref.read(_adminApiProvider).addDoctor(
            name: _name.text.trim(),
            email: _email.text.trim(),
            password: _password.text,
            specialization: _spec.text.trim(),
            phoneNumber: _phone.text.trim().isEmpty ? null : _phone.text.trim(),
          );
      setState(() => _msg = 'Doctor created successfully');
    } catch (_) {
      setState(() => _msg = 'Failed to create doctor');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: ListView(
        children: [
          TextField(controller: _name, decoration: const InputDecoration(labelText: 'Name')),
          const SizedBox(height: 10),
          TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
          const SizedBox(height: 10),
          TextField(
            controller: _password,
            obscureText: true,
            decoration: const InputDecoration(labelText: 'Password'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _spec,
            decoration: const InputDecoration(labelText: 'Specialization'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _phone,
            decoration: const InputDecoration(labelText: 'Phone (optional)'),
          ),
          const SizedBox(height: 14),
          GradientButton(label: 'Create Doctor', isLoading: _loading, onPressed: _submit),
          if (_msg != null) ...[
            const SizedBox(height: 10),
            Text(_msg!, textAlign: TextAlign.center, style: TextStyle(color: VitaloraTheme.muted)),
          ],
        ],
      ),
    );
  }
}

class _AddPatientTab extends ConsumerStatefulWidget {
  const _AddPatientTab();

  @override
  ConsumerState<_AddPatientTab> createState() => _AddPatientTabState();
}

class _AddPatientTabState extends ConsumerState<_AddPatientTab> {
  final _name = TextEditingController();
  final _pid = TextEditingController();
  final _room = TextEditingController();
  final _condition = TextEditingController();
  final _doctorEmail = TextEditingController();
  bool _loading = false;
  String? _msg;

  @override
  void dispose() {
    _name.dispose();
    _pid.dispose();
    _room.dispose();
    _condition.dispose();
    _doctorEmail.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _msg = null;
    });
    try {
      await ref.read(_adminApiProvider).addPatient(
            name: _name.text.trim(),
            patientId: _pid.text.trim(),
            roomNo: _room.text.trim(),
            condition: _condition.text.trim(),
            doctorEmail: _doctorEmail.text.trim(),
          );
      setState(() => _msg = 'Patient created successfully');
    } catch (_) {
      setState(() => _msg = 'Failed to create patient');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: ListView(
        children: [
          TextField(controller: _name, decoration: const InputDecoration(labelText: 'Name')),
          const SizedBox(height: 10),
          TextField(controller: _pid, decoration: const InputDecoration(labelText: 'Patient ID')),
          const SizedBox(height: 10),
          TextField(controller: _room, decoration: const InputDecoration(labelText: 'Room No')),
          const SizedBox(height: 10),
          TextField(
            controller: _condition,
            decoration: const InputDecoration(labelText: 'Condition (e.g., covid-19)'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _doctorEmail,
            decoration: const InputDecoration(labelText: 'Assigned Doctor Email'),
          ),
          const SizedBox(height: 14),
          GradientButton(label: 'Create Patient', isLoading: _loading, onPressed: _submit),
          if (_msg != null) ...[
            const SizedBox(height: 10),
            Text(_msg!, textAlign: TextAlign.center, style: TextStyle(color: VitaloraTheme.muted)),
          ],
        ],
      ),
    );
  }
}

