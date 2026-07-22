import { NextResponse } from "next/server";
import { createPrescriptionSchema } from "@/lib/schemas/prescription";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = createPrescriptionSchema.safeParse(body);
    if (!result.success) return NextResponse.json({ message: "Validation failed", errors: result.error.format() }, { status: 400 });

    const data = result.value;
    if (data.details.controlledSchedule === "CII") data.details.refillsAuthorized = 0; // Server-side enforcement

    const signedAt = new Date().toISOString();
    const prescriptionId = `rx_${Math.random().toString(36).substring(2, 9)}`;
    const newPrescription = { id: prescriptionId, ...data, signedAt, status: "created", createdAt: signedAt };

    return NextResponse.json(newPrescription, { status: 201 });
  } catch (error: any) {
    return NextResponse.json({ message: "Server Error", error: error.message }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ events: [] }, { status: 200 });
}
