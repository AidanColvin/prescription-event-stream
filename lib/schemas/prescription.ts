import { z } from "zod";

const phoneRegex = /^(\+?1\s?)?(\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}$/;
const normalizePhone = (val: string): string => {
  const digits = val.replace(/\D/g, "");
  return `+1${digits.startsWith("1") ? digits.slice(1) : digits}`;
};

const postalCodeRegex = /^\d{5}(?:-\d{4})?$/;
const deaRegex = /^[A-Z]{2}\d{7}$/;

export const validateDeaChecksum = (dea: string): boolean => {
  if (!deaRegex.test(dea)) return false;
  const digits = dea.slice(2).split("").map(Number);
  const sum1 = digits[0] + digits[2] + digits[4];
  const sum2 = (digits[1] + digits[3] + digits[5]) * 2;
  return (sum1 + sum2) % 10 === digits[6];
};

export const addressSchema = z.object({
  street1: z.string().min(1, "Street is required").trim(),
  street2: z.string().optional().transform(v => v?.trim()),
  city: z.string().min(1, "City is required").trim(),
  state: z.string().length(2, "2-letter state code").toUpperCase(),
  postalCode: z.string().regex(postalCodeRegex, "Invalid ZIP"),
});

export const patientSchema = z.object({
  fullName: z.string().min(2, "Name required").trim(),
  address: addressSchema,
  dateOfBirth: z.string().refine((val) => {
    const d = new Date(val);
    const min = new Date(); min.setFullYear(min.getFullYear() - 130);
    return !isNaN(d.getTime()) && d <= new Date() && d >= min;
  }, "Invalid DOB"),
  phone: z.string().regex(phoneRegex, "Invalid phone").transform(normalizePhone),
  insurance: z.object({
    provider: z.string().min(1),
    memberId: z.string().min(1),
    groupNumber: z.string().optional()
  }).optional().refine(val => !val || (val.provider && val.memberId), "Provider and Member ID required")
});

export const prescriberSchema = z.object({
  fullName: z.string().min(1).trim(),
  designation: z.enum(["MD", "DO", "NP", "PA", "DDS", "DMD", "DPM", "OD"]),
  address: addressSchema,
  phone: z.string().regex(phoneRegex).transform(normalizePhone),
  licenseState: z.string().length(2).toUpperCase(),
  licenseNumber: z.string().min(1).trim(),
  deaNumber: z.string().optional().transform(v => v?.toUpperCase()),
  signature: z.object({
    typedName: z.string().min(1),
    signedElectronically: z.literal(true)
  })
});

export const prescriptionDetailsSchema = z.object({
  issueDate: z.string().refine(v => !isNaN(new Date(v).getTime()) && new Date(v) <= new Date(), "Invalid issue date"),
  drugName: z.string().min(1).trim(),
  genericName: z.string().optional().transform(v => v?.trim()),
  brandName: z.string().optional().transform(v => v?.trim()),
  strengthValue: z.number().positive(),
  strengthUnit: z.enum(["mg", "mcg", "g", "mL", "IU", "%"]),
  dosageForm: z.enum(["tablet", "capsule", "liquid", "suspension", "topical", "ointment", "cream", "patch", "injection", "inhaler", "drops", "suppository", "other"]),
  quantityValue: z.number().positive(),
  quantityUnit: z.string().min(1),
  sig: z.string().min(1).max(500).trim(),
  refillsAuthorized: z.number().int().min(0).max(11),
  controlledSchedule: z.enum(["CII", "CIII", "CIV", "CV"]).optional(),
}).superRefine((data, ctx) => {
  if (data.controlledSchedule === "CII" && data.refillsAuthorized !== 0) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "CII requires 0 refills.", path: ["refillsAuthorized"] });
  }
});

export const createPrescriptionSchema = z.object({
  patient: patientSchema,
  prescriber: prescriberSchema,
  details: prescriptionDetailsSchema,
}).superRefine((data, ctx) => {
  if (data.details.controlledSchedule) {
    if (!data.prescriber.deaNumber) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "DEA required for controlled meds.", path: ["prescriber", "deaNumber"] });
    } else if (!validateDeaChecksum(data.prescriber.deaNumber)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Invalid DEA Checksum.", path: ["prescriber", "deaNumber"] });
    }
  }
});
