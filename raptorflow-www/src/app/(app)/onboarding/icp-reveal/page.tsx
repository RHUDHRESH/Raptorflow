import { ICPDashboardShell } from "@/components/icp";

/**
 * ICP Reveal / ICP Maker page
 * This is where users will see their generated ICPs after completing Groundwork.
 * 
 * TODO: Implement the full reveal flow:
 * - Black screen "thinking" state
 * - Status messages while backend generates ICPs
 * - Super rare card unlock animations
 * - Split layout with cards (left) and details (right)
 */
export default function ICPRevealPage() {
  return <ICPDashboardShell />;
}

