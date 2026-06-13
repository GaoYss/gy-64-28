import {
  BarChart3,
  CalendarCheck,
  ClipboardCheck,
  Gauge,
  Hammer,
  PackageCheck,
  UsersRound,
} from "lucide-react";

export const MODULES = [
  { id: "dashboard", label: "Overview", icon: Gauge },
  { id: "customers", label: "Customers", icon: UsersRound },
  { id: "appointments", label: "Measurements", icon: CalendarCheck },
  { id: "designers", label: "Designers", icon: BarChart3 },
  { id: "projects", label: "Construction", icon: Hammer },
  { id: "procurement", label: "Procurement", icon: PackageCheck },
  { id: "inspections", label: "Acceptance", icon: ClipboardCheck },
];
