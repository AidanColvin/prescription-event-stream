import { z } from "zod";

/** Validates US 10 digit phone numbers and normalizes them to E.164 format. */
const phoneRegex = /^(\+?1\s?)?(\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}$/;
const normalizePhone = (val: string): string => {
  const digits = val.replace(/\D/g, "");
  const nationalNumber = digits.startsWith("1") ? digits.slice(1) : digits;
  return `+1${nationalNumber}`;
};

/** Validates US postal codes in NNNNN or NNNNN-NNNN format. */
const postalCodeRegex = /^\d{5}(-\d{4})?$/;

/** Validates DEA registration numbers and performs checksum verification. */
const deaRegex = /^[A-Z]{2}\d{7}$/;
export const validateDeaChecksum = (dea: string): boolean => {
  if (!deaRegex.test(dea)) return false;
  const digits = dea.slice(2).split("").map(Number);
  const sum1 = digits[0] + digits[2] + digits[4];
  const sum2 = (digits[1] + digits[3] + digits[5]) * 2;
  const total = sum1 + sum2;
  return total % 10 === digits[6];
};

/** Schema for US residential and practice addresses. */
export const addressSchema = z.object({
  street1: z.string().min(1, "Street address is required.").trim(),
  street2: z.string().optional().transform((val) => val?.trim()),
  city: z.string().min(1, "City is required.").trim(),
  state: z.string().length(2, "State must be a 2 letter code.").toUpperCase(),
  postalCode: z.string().regex(postalCodeRegex, "Invalid postal code format."),
});

/** Schema for patient information validation. */
export const patientSchema = z.object({
  fullName: z.string().min(2, "Full legal name must be at least 2 characters.").trim(),
  address: addressSchema,
  dateOfBirth: z.string().refine((val) => {
    const date = new Date(val);
    const now = new Date();
    const minDate = new Date();
    minDate.setFullYear(now.getFullYear() - 130);
    return !isNaN(date.getTime()) && date <= now && date >= minDate;
  }, "Invalid date of birth."),
  phone: z.string().regex(phoneRegex, "Invalid US phone number.").transform(normalizePhone),
  insurance: z
    .object({
      provider: z.string().min(1, "Insurance provider is required."),
      memberId: z.string().min(1, "Member ID is required."),
      groupNumber: z.string().optional(),
    })
    .optional()
    .refine((val) => !val || (val.provider && val.memberId), {
      message: "Provider and member ID are required if insurance is provided.",
    }),
});

/** Schema for prescriber credentials validation. */
export const prescriberSchema = z.object({
  fullName: z.string().min(1, "Prescriber name is required.").trim(),
  designation: z.enum(["MD", "DO", "NP", "PA", "DDS", "DMD", "DPM", "OD"]),
  address: addressSchema,
  phone: z.string().regex(phoneRegex, "Invalid phone number.").transform(normalizePhone),
  licenseState: z.string().length(2, "License state must be a 2 letter code.").toUpperCase(),
  licenseNumber: z.string().min(1, "License number is required.").trim(),
  deaNumber: z.string().optional().transform((val) => val?.toUpperCase()),
  signature: z.object({
    typedName: z.string().min(1, "Typed signature name is required."),
    signedElectronically: z.literal(true),
  }),
});

/** Schema for medication and prescription details validation. */
export const prescriptionDetailsSchema = z
  .object({
    issueDate: z.string().refine((val) => {
      const date = new Date(val);
      return !isNaN(date.getTime()) && date <= new Date();
    }, "Issue date cannot be in the future."),
    drugName: z.string().min(1, "Drug name is required.").trim(),
    genericName: z.string().optional().transform((val) => val?.trim()),
    brandName: z.string().optional().transform((val) => val?.trim()),
    strengthValue: z.number().positive("Strength must be greater than zero."),
    strengthUnit: z.enum(["mg", "mcg", "g", "mL", "IU", "%"]),
    dosageForm: z.enum(["tablet", "capsule", "liquid", "suspension", "topical", "ointment", "cream", "patch", "injection", "inhaler", "drops", "suppository", "other"]),
    quantityValue: z.number().positive("Quantity must be a positive number."),
    quantityUnit: z.string().min(1, "Quantity unit is required."),
    sig: z.string().min(1, "Directions for use are required.").max(500, "Sig cannot exceed 500 characters.").trim(),
    refillsAuthorized: z.number().int().min(0).max(11),
    controlledSchedule: z.enum(["CII", "CIII", "CIV", "CV"]).optional(),
  })
  .superRefine((data, ctx) => {
    if (data.controlledSchedule === "CII" && data.refillsAuthorized !== 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Schedule CII medications cannot have authorized refills.",
        path: ["refillsAuthorized"],
      });
    }
  });

/** Combined master prescription creation schema with cross field validation rules. */
export const createPrescriptionSchema = z
  .object({
    patient: patientSchema,
    prescriber: prescriberSchema,
    details: prescriptionDetailsSchema,
  })
  .superRefine((data, ctx) => {
    if (data.details.controlledSchedule) {
      if (!data.prescriber.deaNumber) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "DEA registration number is required for controlled substances.",
          path: ["prescriber", "deaNumber"],
        });
      } else if (!validateDeaChecksum(data.prescriber.deaNumber)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Invalid DEA registration number format or checksum failure.",
          path: ["prescriber", "deaNumber"],
        });
      }
    }
  });
