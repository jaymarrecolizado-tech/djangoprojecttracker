import { z } from 'zod';

export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export const projectSchema = z.object({
  site_code: z.string().min(1, 'Site code is required').max(50, 'Site code must be less than 50 characters'),
  site_name: z.string().min(1, 'Site name is required').max(200, 'Site name must be less than 200 characters'),
  latitude: z.number().min(-90).max(90, 'Latitude must be between -90 and 90'),
  longitude: z.number().min(-180).max(180, 'Longitude must be between -180 and 180'),
  status: z.enum(['pending', 'in_progress', 'done', 'cancelled', 'on_hold']),
  project_type: z.number().min(1, 'Project type is required'),
  province: z.number().min(1, 'Province is required'),
  district: z.number().nullable().optional(),
  municipality: z.number().min(1, 'Municipality is required'),
  barangay: z.number().min(1, 'Barangay is required'),
  remarks: z.string().max(2000, 'Remarks must be less than 2000 characters').optional(),
  activation_date: z.string().optional(),
});

export const userSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters').max(150),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  full_name: z.string().min(1, 'Full name is required').max(255),
  role: z.enum(['admin', 'manager', 'editor', 'viewer']),
  is_active: z.boolean().default(true),
});

export const changePasswordSchema = z.object({
  old_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'New password must be at least 8 characters'),
  confirm_password: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

export const statusChangeSchema = z.object({
  new_status: z.enum(['pending', 'in_progress', 'done', 'cancelled', 'on_hold']),
  reason: z.string().min(1, 'Reason is required').max(500),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type ProjectFormData = z.infer<typeof projectSchema>;
export type UserFormData = z.infer<typeof userSchema>;
export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;
export type StatusChangeFormData = z.infer<typeof statusChangeSchema>;
