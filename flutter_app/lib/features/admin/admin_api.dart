import 'package:dio/dio.dart';

import '../../core/models.dart';

class AdminApi {
  AdminApi(this._dio);
  final Dio _dio;

  Future<List<Doctor>> listDoctors() async {
    final res = await _dio.get('/admin/doctors');
    final data = res.data as List<dynamic>;
    return data.map((e) => Doctor.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<Patient>> listPatients() async {
    final res = await _dio.get('/admin/patients');
    final data = res.data as List<dynamic>;
    return data.map((e) => Patient.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> addDoctor({
    required String name,
    required String email,
    required String password,
    required String specialization,
    String? phoneNumber,
  }) async {
    await _dio.post('/admin/add_doctor', data: {
      'name': name,
      'email': email,
      'password': password,
      'specialization': specialization,
      if (phoneNumber != null) 'phone_number': phoneNumber,
    });
  }

  Future<void> addPatient({
    required String name,
    required String patientId,
    required String roomNo,
    required String condition,
    required String doctorEmail,
    int? age,
    String? gender,
    String? contactNumber,
    String? address,
    String? city,
    String? state,
  }) async {
    await _dio.post('/admin/add_patient', data: {
      'name': name,
      'patient_id': patientId,
      'room_no': roomNo,
      'condition': condition,
      'doctor_email': doctorEmail,
      if (age != null) 'age': age,
      if (gender != null) 'gender': gender,
      if (contactNumber != null) 'contact_number': contactNumber,
      if (address != null) 'address': address,
      if (city != null) 'city': city,
      if (state != null) 'state': state,
    });
  }
}

