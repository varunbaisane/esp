import React from "react";

interface UserAvatarProps {
  name: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const colors = [
  "bg-blue-600",
  "bg-green-600",
  "bg-purple-600",
  "bg-amber-600",
  "bg-rose-600",
  "bg-cyan-600",
  "bg-indigo-600",
];

const getInitials = (name: string): string => {
  if (!name || name.trim() === "") return "U";
  const words = name.trim().split(/\s+/);
  if (words.length === 1) {
    return words[0].substring(0, 1).toUpperCase();
  }
  return (words[0].substring(0, 1) + words[words.length - 1].substring(0, 1)).toUpperCase();
};

const getColorClass = (name: string): string => {
  if (!name) return "bg-gray-400";
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colors.length;
  return colors[index];
};

export const UserAvatar: React.FC<UserAvatarProps> = ({ name, size = "md", className = "" }) => {
  const initials = getInitials(name);
  const colorClass = getColorClass(name);

  let sizeClass = "";
  let textClass = "";

  switch (size) {
    case "sm":
      sizeClass = "w-6 h-6"; // 24px
      textClass = "text-[10px]";
      break;
    case "md":
      sizeClass = "w-8 h-8"; // 32px
      textClass = "text-xs";
      break;
    case "lg":
      sizeClass = "w-10 h-10"; // 40px
      textClass = "text-sm";
      break;
  }

  return (
    <div
      className={`flex items-center justify-center rounded-full text-white font-semibold flex-shrink-0 ${sizeClass} ${colorClass} ${textClass} ${className}`}
      title={name}
    >
      {initials}
    </div>
  );
};
