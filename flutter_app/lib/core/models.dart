class LoginResponse {
  LoginResponse({required this.accessToken, required this.role});
  final String accessToken;
  final String role;

  factory LoginResponse.fromJson(Map<String, dynamic> json) => LoginResponse(
        accessToken: json['access_token'] as String,
        role: json['role'] as String,
      );
}

class Doctor {
  Doctor({
    required this.name,
    required this.email,
    required this.specialization,
    this.phoneNumber,
  });
  final String name;
  final String email;
  final String specialization;
  final String? phoneNumber;

  factory Doctor.fromJson(Map<String, dynamic> json) => Doctor(
        name: json['name'] as String,
        email: json['email'] as String,
        specialization: json['specialization'] as String,
        phoneNumber: json['phone_number'] as String?,
      );
}

class Patient {
  Patient({
    required this.patientId,
    required this.name,
    required this.roomNo,
    required this.condition,
    required this.doctorEmail,
    this.age,
    this.gender,
  });

  final String patientId;
  final String name;
  final String roomNo;
  final String condition;
  final String doctorEmail;
  final int? age;
  final String? gender;

  factory Patient.fromJson(Map<String, dynamic> json) => Patient(
        patientId: json['patient_id'] as String,
        name: json['name'] as String,
        roomNo: json['room_no'] as String,
        condition: json['condition'] as String,
        doctorEmail: json['doctor_email'] as String,
        age: json['age'] as int?,
        gender: json['gender'] as String?,
      );
}

class Vital {
  Vital({
    required this.patientId,
    required this.timestamp,
    required this.respirationRate,
    required this.spo2,
    required this.oxygenSupport,
    required this.systolicBp,
    required this.heartRate,
    required this.temperature,
    required this.consciousness,
  });
  final String patientId;
  final DateTime timestamp;
  final int respirationRate;
  final int spo2;
  final int oxygenSupport;
  final int systolicBp;
  final int heartRate;
  final double temperature;
  final String consciousness;

  factory Vital.fromJson(Map<String, dynamic> json) => Vital(
        patientId: json['patient_id'] as String,
        timestamp: DateTime.parse(json['timestamp'] as String),
        respirationRate: (json['respiration_rate'] as num).toInt(),
        spo2: (json['spo2'] as num).toInt(),
        oxygenSupport: (json['oxygen_support'] as num).toInt(),
        systolicBp: (json['systolic_bp'] as num).toInt(),
        heartRate: (json['heart_rate'] as num).toInt(),
        temperature: (json['temperature'] as num).toDouble(),
        consciousness: json['consciousness'] as String,
      );
}

class AnalyzeResult {
  AnalyzeResult({
    required this.newsScore,
    required this.outbreakSeverity,
    required this.adjustedScore,
    required this.alertLevel,
  });
  final double newsScore;
  final double outbreakSeverity;
  final double adjustedScore;
  final String alertLevel;

  factory AnalyzeResult.fromJson(Map<String, dynamic> json) => AnalyzeResult(
        newsScore: (json['news_score'] as num).toDouble(),
        outbreakSeverity: (json['outbreak_severity'] as num).toDouble(),
        adjustedScore: (json['adjusted_score'] as num).toDouble(),
        alertLevel: json['alert_level'] as String,
      );
}

