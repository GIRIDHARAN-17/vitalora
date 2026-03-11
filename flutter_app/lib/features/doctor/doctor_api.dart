import 'package:dio/dio.dart';

import '../../core/models.dart';

class DoctorApi {
  DoctorApi(this._dio);
  final Dio _dio;

  Future<List<Patient>> assignedPatients() async {
    final res = await _dio.get('/doctor/patients');
    final data = res.data as List<dynamic>;
    return data.map((e) => Patient.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Vital>> vitals(String patientId) async {
    final res = await _dio.get('/doctor/patient/$patientId/vitals');
    final data = res.data as List<dynamic>;
    return data.map((e) => Vital.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<AnalyzeResult> analyze({required String patientId, required String location}) async {
    final res = await _dio.post('/patient/analyze', data: {
      'patient_id': patientId,
      'location': location,
    });
    return AnalyzeResult.fromJson(res.data as Map<String, dynamic>);
  }
}

