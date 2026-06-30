export interface TicketPermissions {
    canAssign: boolean;
    canChangeAssignee: boolean;
    canStartProgress: boolean;
    canResolve: boolean;
    canClose: boolean;
    canReopen: boolean;
    canEditPriority: boolean;
    canEscalate: boolean;
}
