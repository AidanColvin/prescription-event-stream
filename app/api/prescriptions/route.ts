import { NextResponse } from "next/server";
import { createPrescriptionSchema } from "@/lib/schemas/prescription";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validationResult = createPrescriptionSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        { message: "Validation failed.", errors: validationResult.error.format() },
        { status: 400 }
      );
    }

    const data = validationResult.value;

    // Force CII refills to 0 on the server side unconditionally
    if (data.details.controlledSchedule === "CII") {
      data.details.refillsAuthorized = 0;
    }

    const signedAt = new Date().toISOString();
    const prescriptionId = `rx_${Math.random().toString(36).substring(2, 9)}`;

    const newPrescription = {
      id: prescriptionId,
      ...data,
      signedAt,
      status: "created",
      createdAt: signedAt,
    };

    const initialEvent = {
      id: `evt_${Math.random().toString(36).substring(2, 9)}`,
      prescriptionId,
      actorRole: "prescriber",
      actorId: data.prescriber.fullName,
      type: "created",
      payload: newPrescription,
      createdAt: signedAt,
    };

    // DB insertion logic goes here.

    return NextResponse.json(newPrescription, { status: 201 });
  } catch (error: any) {
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

export async function GET() {
  // Returns the event-sourced materialized view
  return NextResponse.json({ events: [] }, { status: 200 });
}
