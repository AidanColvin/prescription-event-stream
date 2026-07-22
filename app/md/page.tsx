"use client";

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createPrescriptionSchema } from "@/lib/schemas/prescription";
import { z } from "zod";
import { useRouter } from "next/navigation";

type PrescriptionFormData = z.infer<typeof createPrescriptionSchema>;

/** Renders the prescriber form interface for creating US compliant prescriptions. */
export default function PrescriberFormPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const { register, handleSubmit, watch, setValue, formState: { errors, isSubmitting, isValid } } = useForm<PrescriptionFormData>({
    resolver: zodResolver(createPrescriptionSchema),
    mode: "onChange",
    defaultValues: {
      details: {
        issueDate: new Date().toISOString().split("T")[0],
        refillsAuthorized: 0,
        strengthUnit: "mg",
        dosageForm: "tablet",
        quantityUnit: "tablets",
      },
      prescriber: { designation: "MD", signature: { signedElectronically: true } },
    },
  });

  const controlledSchedule = watch("details.controlledSchedule");

  useEffect(() => {
    if (controlledSchedule === "CII") setValue("details.refillsAuthorized", 0);
  }, [controlledSchedule, setValue]);

  const onSubmit = async (data: PrescriptionFormData) => {
    setServerError(null);
    try {
      const response = await fetch("/api/prescriptions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error("Failed to create prescription.");
      const result = await response.json();
      router.push(`/prescriptions/${result.id}`);
    } catch (err: any) {
      setServerError(err.message || "An unexpected error occurred.");
    }
  };

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8 font-sans">
      <div className="max-w-4xl mx-auto bg-white border border-[#d2d2d7] rounded-[16px] p-8 shadow-sm">
        <h1 className="text-3xl font-semibold mb-8 tracking-tight">Prescribe Medication</h1>

        {serverError && <div className="mb-6 p-4 bg-[#ffebee] text-[#c0392b] rounded-lg text-sm">{serverError}</div>}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-12">
          <section>
            <h2 className="text-xl font-medium border-b border-[#d2d2d7] pb-3 mb-6 sticky top-0 bg-white z-10">Patient Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Full Legal Name</label>
                <input {...register("patient.fullName")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
                {errors.patient?.fullName && <p className="text-[#c0392b] text-xs mt-2">{errors.patient.fullName.message}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Date of Birth</label>
                <input type="date" {...register("patient.dateOfBirth")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
                {errors.patient?.dateOfBirth && <p className="text-[#c0392b] text-xs mt-2">{errors.patient.dateOfBirth.message}</p>}
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Street Address</label>
                <input {...register("patient.address.street1")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
              </div>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">City</label>
                <input {...register("patient.address.city")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">State</label>
                  <input {...register("patient.address.state")} maxLength={2} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm uppercase focus:outline-none focus:border-[#0071e3]" />
                </div>
                <div>
                  <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Postal Code</label>
                  <input {...register("patient.address.postalCode")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Phone Number</label>
                <input {...register("patient.phone")} placeholder="(555) 000-0000" className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-medium border-b border-[#d2d2d7] pb-3 mb-6 sticky top-0 bg-white z-10">Prescriber Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Full Name & Designation</label>
                <div className="flex gap-3">
                  <input {...register("prescriber.fullName")} className="flex-1 border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
                  <select {...register("prescriber.designation")} className="border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]">
                    {["MD", "DO", "NP", "PA", "DDS", "DMD", "DPM", "OD"].map((d) => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">DEA Registration Number</label>
                <input {...register("prescriber.deaNumber")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm uppercase focus:outline-none focus:border-[#0071e3]" />
                {errors.prescriber?.deaNumber && <p className="text-[#c0392b] text-xs mt-2">{errors.prescriber.deaNumber.message}</p>}
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Electronic Signature (Typed Name)</label>
                <input {...register("prescriber.signature.typedName")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm italic focus:outline-none focus:border-[#0071e3]" />
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-medium border-b border-[#d2d2d7] pb-3 mb-6 sticky top-0 bg-white z-10">Medication Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Drug Name</label>
                <input {...register("details.drugName")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
              </div>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Controlled Schedule</label>
                <select {...register("details.controlledSchedule")} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]">
                  <option value="">Non-controlled</option>
                  <option value="CII">Schedule II</option>
                  <option value="CIII">Schedule III</option>
                  <option value="CIV">Schedule IV</option>
                  <option value="CV">Schedule V</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Strength</label>
                  <input type="number" {...register("details.strengthValue", { valueAsNumber: true })} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
                </div>
                <div>
                  <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Refills</label>
                  <input type="number" disabled={controlledSchedule === "CII"} {...register("details.refillsAuthorized", { valueAsNumber: true })} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3] disabled:opacity-50" />
                  {errors.details?.refillsAuthorized && <p className="text-[#c0392b] text-xs mt-2">{errors.details.refillsAuthorized.message}</p>}
                </div>
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium uppercase tracking-wider text-[#86868b] mb-2">Directions for Use (Sig)</label>
                <textarea {...register("details.sig")} rows={3} className="w-full border border-[#d2d2d7] rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-[#0071e3]" />
              </div>
            </div>
          </section>

          <div className="flex justify-end pt-6 border-t border-[#d2d2d7]">
            <button type="submit" disabled={!isValid || isSubmitting} className="bg-[#0071e3] text-white px-8 py-3 rounded-full text-sm font-medium hover:bg-[#0077ed] transition-colors disabled:opacity-50">
              {isSubmitting ? "Authorizing..." : "Sign & Submit Prescription"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
