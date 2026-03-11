"""
Simulate ICU vitals for a patient by inserting records into MongoDB periodically.

This is meant for demos:
- Generates random vitals (normal) or intentionally bad vitals (high/critical)
- The backend monitoring service will compute NEWS score trend and trigger alerts

Usage examples:
  python -m backend.scripts.simulate_vitals --patient-id P-101 --interval-seconds 120 --mode normal
  python -m backend.scripts.simulate_vitals --patient-id P-101 --interval-seconds 10 --mode high --steps 40
  python -m backend.scripts.simulate_vitals --patient-id P-101 --interval-seconds 5 --mode deteriorating --steps 80

Notes:
- patient_id is case-sensitive; use exactly what exists in MongoDB.
"""

from __future__ import annotations

import argparse
import asyncio
import random
from datetime import datetime

from backend.database.mongodb import Mongo


def _rand_normal() -> dict:
    rr = random.randint(12, 20)
    spo2 = random.randint(94, 99)
    hr = random.randint(65, 95)
    sbp = random.randint(105, 135)
    temp = round(random.uniform(36.5, 37.7), 1)
    oxygen_support = 1 if spo2 < 94 else 0
    consciousness = "A"
    return {
        "respiration_rate": rr,
        "spo2": spo2,
        "oxygen_support": oxygen_support,
        "systolic_bp": sbp,
        "heart_rate": hr,
        "temperature": temp,
        "consciousness": consciousness,
    }


def _rand_high() -> dict:
    rr = random.randint(26, 34)
    spo2 = random.randint(85, 91)
    hr = random.randint(125, 160)
    sbp = random.randint(75, 95)
    temp = round(random.uniform(39.1, 40.2), 1)
    oxygen_support = 1
    consciousness = random.choice(["V", "P", "U"])
    return {
        "respiration_rate": rr,
        "spo2": spo2,
        "oxygen_support": oxygen_support,
        "systolic_bp": sbp,
        "heart_rate": hr,
        "temperature": temp,
        "consciousness": consciousness,
    }


def _rand_deteriorating(step: int, total: int) -> dict:
    t = step / max(1, total - 1)
    rr = int(16 + t * 18 + random.randint(-2, 2))
    spo2 = int(98 - t * 14 + random.randint(-1, 1))
    hr = int(80 + t * 70 + random.randint(-5, 5))
    sbp = int(125 - t * 45 + random.randint(-5, 5))
    temp = round(36.8 + t * 3.2 + random.uniform(-0.2, 0.2), 1)
    oxygen_support = 1 if spo2 < 94 else 0
    consciousness = "A" if spo2 > 92 else random.choice(["V", "P", "U"])
    return {
        "respiration_rate": max(6, min(rr, 40)),
        "spo2": max(70, min(spo2, 100)),
        "oxygen_support": oxygen_support,
        "systolic_bp": max(60, min(sbp, 220)),
        "heart_rate": max(35, min(hr, 200)),
        "temperature": max(34.0, min(temp, 41.0)),
        "consciousness": consciousness,
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patient-id", dest="patient_id")
    parser.add_argument("--patient_id", dest="patient_id")
    parser.add_argument("--interval-seconds", type=int, default=120)
    parser.add_argument(
        "--mode", choices=["normal", "high", "deteriorating"], default="normal")
    parser.add_argument("--steps", type=int, default=0,
                        help="0 = run forever; otherwise stop after N inserts")
    args = parser.parse_args()

    if not args.patient_id:
        raise SystemExit("Missing required --patient-id / --patient_id")

    Mongo.connect()
    db = Mongo.db
    if db is None:
        raise RuntimeError("DB not connected")

    patient = await db["patient"].find_one({"patient_id": args.patient_id})
    if not patient:
        raise RuntimeError(
            f"Patient not found: {args.patient_id}. Create patient first.")

    print(
        f"Simulating vitals for {args.patient_id} mode={args.mode} every {args.interval_seconds}s")

    i = 0
    while True:
        if args.mode == "normal":
            vitals = _rand_normal()
        elif args.mode == "high":
            vitals = _rand_high()
        else:
            vitals = _rand_deteriorating(i, max(args.steps, 60))

        doc = {"patient_id": args.patient_id,
               "timestamp": datetime.utcnow(), **vitals}
        await db["patient_vitals"].insert_one(doc)

        i += 1
        print(
            f"[{i}] inserted vitals: RR={doc['respiration_rate']} SpO2={doc['spo2']} "
            f"HR={doc['heart_rate']} SBP={doc['systolic_bp']} Temp={doc['temperature']} "
            f"C={doc['consciousness']}"
        )

        if args.steps and i >= args.steps:
            break

        await asyncio.sleep(max(1, args.interval_seconds))

    Mongo.close()


if __name__ == "__main__":
    asyncio.run(main())
