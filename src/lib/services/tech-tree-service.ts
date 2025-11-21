// Tech Tree Service - Logic for capability unlocking and dependencies
import { CapabilityNode, CapabilityStatus } from '../../types/move-system'

export interface WorkspaceState {
  id: string
  hasAnalytics?: boolean
  hasTracking?: boolean
  minICPs?: number
  hasLeadMagnet?: boolean
  minDownloads?: number
  hasEmailSequence?: boolean
  hasAutomation?: boolean
  minTestimonials?: number
  hasCRM?: boolean
  isConnected?: boolean
  hasTestingSetup?: boolean
  minTestsRun?: number
  hasReferralProgram?: boolean
  minReferrals?: number
  minNPS?: number
  hasMLModel?: boolean
  accuracyThreshold?: number
  hasCommunity?: boolean
  minActiveUsers?: number
}

export class TechTreeService {
  /**
   * Check if a capability node can be unlocked
   */
  async canUnlockNode(
    node: CapabilityNode,
    workspaceState: WorkspaceState,
    allNodes: CapabilityNode[]
  ): Promise<boolean> {
    // Check all parent nodes are unlocked
    for (const parentId of node.parentNodeIds) {
      const parent = allNodes.find(n => n.id === parentId)
      if (!parent || parent.status !== 'Unlocked') {
        return false
      }
    }

    // Check completion criteria if automatic
    if (node.completionCriteria.type === 'automatic') {
      return this.checkCriteria(node.completionCriteria.conditions || {}, workspaceState)
    }

    // Manual nodes require explicit unlock
    return false
  }

  /**
   * Check if completion criteria are met
   */
  private checkCriteria(conditions: Record<string, any>, workspaceState: WorkspaceState): boolean {
    for (const [key, value] of Object.entries(conditions)) {
      const workspaceValue = workspaceState[key as keyof WorkspaceState]
      
      if (typeof value === 'number') {
        // Numeric comparison (min, threshold, etc.)
        if (typeof workspaceValue !== 'number' || workspaceValue < value) {
          return false
        }
      } else if (typeof value === 'boolean') {
        // Boolean check
        if (workspaceValue !== value) {
          return false
        }
      } else {
        // Other types - exact match
        if (workspaceValue !== value) {
          return false
        }
      }
    }
    return true
  }

  /**
   * Get all nodes that can be unlocked given current workspace state
   */
  getUnlockableNodes(
    allNodes: CapabilityNode[],
    workspaceState: WorkspaceState
  ): CapabilityNode[] {
    return allNodes.filter(node => {
      if (node.status === 'Unlocked') return false
      
      // Check if all prerequisites are met
      const allParentsUnlocked = node.parentNodeIds.every(parentId => {
        const parent = allNodes.find(n => n.id === parentId)
        return parent?.status === 'Unlocked'
      })

      if (!allParentsUnlocked) return false

      // Check completion criteria
      if (node.completionCriteria.type === 'automatic') {
        return this.checkCriteria(node.completionCriteria.conditions || {}, workspaceState)
      }

      return false
    })
  }

  /**
   * Get nodes that should be unlocked based on current state
   * (for auto-unlocking)
   */
  async autoUnlockNodes(
    allNodes: CapabilityNode[],
    workspaceState: WorkspaceState
  ): Promise<CapabilityNode[]> {
    const unlockable = this.getUnlockableNodes(allNodes, workspaceState)
    
    return unlockable.filter(node => {
      // Only auto-unlock if criteria are met
      if (node.completionCriteria.type === 'automatic') {
        return this.checkCriteria(node.completionCriteria.conditions || {}, workspaceState)
      }
      return false
    })
  }

  /**
   * Get all unlocked capability IDs
   */
  getUnlockedCapabilityIds(nodes: CapabilityNode[]): string[] {
    return nodes
      .filter(node => node.status === 'Unlocked')
      .map(node => node.id)
  }

  /**
   * Check if a maneuver type is unlocked (all required capabilities unlocked)
   */
  isManeuverUnlocked(
    requiredCapabilityIds: string[],
    unlockedCapabilityIds: string[]
  ): boolean {
    if (requiredCapabilityIds.length === 0) return true
    return requiredCapabilityIds.every(id => unlockedCapabilityIds.includes(id))
  }

  /**
   * Get dependency path for a node (all nodes that must be unlocked first)
   */
  getDependencyPath(
    nodeId: string,
    allNodes: CapabilityNode[]
  ): CapabilityNode[] {
    const node = allNodes.find(n => n.id === nodeId)
    if (!node) return []

    const path: CapabilityNode[] = []
    const visited = new Set<string>()

    const traverse = (currentNode: CapabilityNode) => {
      if (visited.has(currentNode.id)) return
      visited.add(currentNode.id)

      for (const parentId of currentNode.parentNodeIds) {
        const parent = allNodes.find(n => n.id === parentId)
        if (parent) {
          traverse(parent)
          if (!path.find(n => n.id === parent.id)) {
            path.push(parent)
          }
        }
      }
    }

    traverse(node)
    return path
  }

  /**
   * Get all nodes that unlock a specific maneuver
   */
  getNodesThatUnlockManeuver(
    maneuverId: string,
    allNodes: CapabilityNode[]
  ): CapabilityNode[] {
    return allNodes.filter(node => 
      node.unlocksManeuverIds.includes(maneuverId)
    )
  }
}

// Export singleton instance
export const techTreeService = new TechTreeService()


