import type { ReactNode, ButtonHTMLAttributes } from 'react';
import { Link } from 'react-router-dom';
import { COLORS } from '../../styles/design-tokens';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface ButtonBaseProps {
  variant?: ButtonVariant;
  children: ReactNode;
  className?: string;
}

interface ButtonAsButtonProps extends ButtonBaseProps, Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type' | 'children'> {
  to?: never;
  type?: 'button' | 'submit' | 'reset';
}

interface ButtonAsLinkProps extends ButtonBaseProps {
  to: string;
  onClick?: () => void;
  target?: string;
  rel?: string;
}

type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps;

export const Button = ({ 
  variant = 'primary', 
  children, 
  className = '', 
  ...props 
}: ButtonProps) => {
  const baseClasses = "inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap";
  
  let variantClasses = "";
  
  switch (variant) {
    case 'primary':
      variantClasses = `border border-transparent text-white ${COLORS.primary["600"]} ${COLORS.primary.hover.bg["700"]} ${COLORS.primary.ring["500"]}`;
      break;
    case 'secondary':
      variantClasses = `border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-gray-500`;
      break;
    case 'danger':
      variantClasses = `border border-transparent text-white bg-red-600 hover:bg-red-700 focus:ring-red-500`;
      break;
    case 'ghost':
      variantClasses = `text-gray-500 hover:text-gray-900 hover:bg-gray-50 focus:ring-gray-500 border border-transparent`;
      break;
  }
  
  const combinedClasses = `${baseClasses} ${variantClasses} ${className}`.trim();

  if ('to' in props && props.to) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { to, variant, className, ...rest } = props as ButtonAsLinkProps;
    return (
      <Link to={to} className={combinedClasses} {...rest}>
        {children}
      </Link>
    );
  }

  return (
    <button className={combinedClasses} {...(props as ButtonAsButtonProps)}>
      {children}
    </button>
  );
};
