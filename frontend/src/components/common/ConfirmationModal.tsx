import type { ReactNode } from "react";
import { ButtonLoader } from "./ButtonLoader";

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  description: ReactNode;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const ConfirmationModal = ({
  isOpen,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  onConfirm,
  onCancel,
  isLoading = false,
}: ConfirmationModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm transition-opacity"
        onClick={onCancel}
      />

      <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <h3 className="text-lg font-bold text-gray-900 tracking-tight mb-2">
          {title}
        </h3>

        <div className="text-sm text-gray-500 mb-6 leading-relaxed">
          {description}
        </div>

        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-semibold text-white bg-amber-600 border border-transparent rounded-md hover:bg-amber-700 shadow-sm transition-colors disabled:opacity-50"
          >
            {isLoading ? <ButtonLoader text={confirmText} /> : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};
